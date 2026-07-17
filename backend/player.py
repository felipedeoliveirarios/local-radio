from __future__ import annotations

import logging
import signal
import subprocess
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from downloader import download_audio
from music_queue import MusicQueue, QueueItem
from narrator import generate_narration
from templates import pick_template

logger = logging.getLogger(__name__)


@dataclass
class PreparedItem:
    """Item pronto pra tocar (áudio + narração já baixados)."""
    item: QueueItem
    audio_path: Path
    narration_path: Path


class Player:
    """Controla reprodução de áudio com skip/pause/resume e prefetch."""

    def __init__(self, music_queue: MusicQueue) -> None:
        self._queue = music_queue
        self._process: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._paused = False
        self._skipping = False
        self._prefetch_executor = ThreadPoolExecutor(max_workers=1)
        self._prefetch_future: Future[PreparedItem] | None = None
        self._prefetch_url: str | None = None  # URL sendo prefetchada

    @property
    def paused(self) -> bool:
        return self._paused

    def skip(self) -> bool:
        """Pula a música atual. Retorna True se havia algo tocando."""
        with self._lock:
            if self._process and self._process.poll() is None:
                self._skipping = True
                self._process.terminate()
                return True
            return False

    def pause(self) -> bool:
        """Pausa a reprodução atual."""
        with self._lock:
            if self._process and self._process.poll() is None and not self._paused:
                self._process.send_signal(signal.SIGSTOP)
                self._paused = True
                return True
            return False

    def resume(self) -> bool:
        """Retoma a reprodução pausada."""
        with self._lock:
            if self._process and self._paused:
                self._process.send_signal(signal.SIGCONT)
                self._paused = False
                return True
            return False

    def _play_file(self, path: Path) -> None:
        """Reproduz arquivo via mpv. Bloqueia até terminar."""
        with self._lock:
            self._process = subprocess.Popen(
                ["mpv", "--no-video", "--really-quiet", str(path)],
            )
        self._process.wait()
        with self._lock:
            self._process = None
            self._paused = False

    def _prepare(self, item: QueueItem) -> PreparedItem:
        """Baixa áudio e gera narração pra um item."""
        audio_path = download_audio(item.url)
        narration_artist = item.artist if item.artist_confident else None
        text = pick_template(item.track, narration_artist, item.requester)
        narration_path = generate_narration(text)
        return PreparedItem(item=item, audio_path=audio_path, narration_path=narration_path)

    def _start_prefetch(self) -> None:
        """Inicia prefetch do próximo item da fila se houver."""
        next_item = self._queue.peek()
        if next_item and next_item.url != self._prefetch_url:
            self._prefetch_url = next_item.url
            self._prefetch_future = self._prefetch_executor.submit(self._prepare, next_item)

    def _get_prepared(self, item: QueueItem) -> PreparedItem:
        """Retorna item preparado: usa prefetch se disponível, senão prepara na hora."""
        # Verifica se o prefetch corresponde a este item
        if self._prefetch_future and self._prefetch_url == item.url:
            try:
                prepared = self._prefetch_future.result(timeout=300)
                self._prefetch_future = None
                self._prefetch_url = None
                return prepared
            except Exception:
                logger.warning("Prefetch falhou, preparando na hora.")
                self._prefetch_future = None
                self._prefetch_url = None

        # Prepara na hora
        return self._prepare(item)

    def _run(self) -> None:
        """Loop principal do player."""
        logger.info("Player loop iniciado.")
        while True:
            item = self._queue.dequeue()
            logger.info("Processando: %s - %s", item.artist, item.track)

            self._skipping = False
            prepared: PreparedItem | None = None
            try:
                prepared = self._get_prepared(item)

                # Toca narração
                self._play_file(prepared.narration_path)

                if self._skipping:
                    continue

                # Inicia prefetch da próxima enquanto a música toca
                self._start_prefetch()

                # Reprodução
                self._queue.now_playing = prepared.item
                self._play_file(prepared.audio_path)
                self._queue.now_playing = None

            except Exception:
                logger.exception("Erro ao reproduzir: %s - %s", item.artist, item.track)
                self._queue.now_playing = None
            finally:
                if prepared:
                    _cleanup(prepared.audio_path, prepared.narration_path)

    def start(self) -> threading.Thread:
        """Inicia player loop em daemon thread."""
        t = threading.Thread(target=self._run, daemon=True)
        t.start()
        return t


def _cleanup(*paths: Path) -> None:
    for p in paths:
        try:
            p.unlink(missing_ok=True)
        except OSError:
            pass
