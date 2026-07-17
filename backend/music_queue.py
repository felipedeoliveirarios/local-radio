from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class QueueItem:
    url: str
    track: str
    artist: str
    requester: str | None
    artist_confident: bool = True
    added_at: datetime = field(default_factory=datetime.now)


class MusicQueue:
    def __init__(self) -> None:
        self._queue: deque[QueueItem] = deque()
        self._lock = threading.Lock()
        self._not_empty = threading.Condition(self._lock)
        self._now_playing: QueueItem | None = None

    def enqueue(self, item: QueueItem) -> int:
        """Adiciona item à fila. Retorna posição (1-based)."""
        with self._not_empty:
            self._queue.append(item)
            position = len(self._queue)
            self._not_empty.notify()
            return position

    def dequeue(self) -> QueueItem:
        """Remove e retorna próximo item. Bloqueia se fila vazia."""
        with self._not_empty:
            while not self._queue:
                self._not_empty.wait()
            return self._queue.popleft()

    def list(self) -> list[QueueItem]:
        """Retorna snapshot da fila atual."""
        with self._lock:
            return list(self._queue)

    def remove(self, position: int) -> bool:
        """Remove item pela posição (1-based). Retorna True se removido."""
        with self._lock:
            idx = position - 1
            if 0 <= idx < len(self._queue):
                del self._queue[idx]
                return True
            return False

    def peek(self) -> QueueItem | None:
        """Retorna o próximo item sem removê-lo, ou None se vazio."""
        with self._lock:
            return self._queue[0] if self._queue else None

    @property
    def now_playing(self) -> QueueItem | None:
        with self._lock:
            return self._now_playing

    @now_playing.setter
    def now_playing(self, item: QueueItem | None) -> None:
        with self._lock:
            self._now_playing = item
