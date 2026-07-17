from __future__ import annotations

import logging
import signal
import subprocess
import threading
from pathlib import Path

from downloader import download_audio
from narrator import generate_narration
from music_queue import MusicQueue
from templates import pick_template

logger = logging.getLogger(__name__)


class Player:
    """Controla reprodução de áudio com skip/pause/resume."""

    def __init__(self, music_queue: MusicQueue) -> None:
        self._queue = music_queue
        self._process: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._paused = False
        self._skipping = False

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

    def _run(self) -> None:
        """Loop principal do player."""
        logger.info("Player loop iniciado.")
        while True:
            item = self._queue.dequeue()
            logger.info("Processando: %s - %s", item.artist, item.track)

            self._skipping = False
            audio_path: Path | None = None
            narration_path: Path | None = None
            try:
                # Download
                audio_path = download_audio(item.url)

                # Narração
                text = pick_template(item.track, item.artist, item.requester)
                narration_path = generate_narration(text)
                self._play_file(narration_path)

                if self._skipping:
                    continue

                # Reprodução
                self._queue.now_playing = item
                self._play_file(audio_path)
                self._queue.now_playing = None

            except Exception:
                logger.exception("Erro ao reproduzir: %s - %s", item.artist, item.track)
                self._queue.now_playing = None
            finally:
                files_to_clean = [p for p in (audio_path, narration_path) if p]
                _cleanup(*files_to_clean)

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
