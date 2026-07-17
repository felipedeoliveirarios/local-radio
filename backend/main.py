from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from downloader import get_video_info
from player import Player
from music_queue import MusicQueue, QueueItem

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "changeme")

music_queue = MusicQueue()
player = Player(music_queue)


@asynccontextmanager
async def lifespan(app: FastAPI):
    player.start()
    yield


app = FastAPI(title="Local Radio", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth helper ---


def _check_token(authorization: str | None) -> None:
    if not authorization or authorization != f"Bearer {ADMIN_TOKEN}":
        raise HTTPException(status_code=401, detail="Token inválido")


# --- Schemas ---


class AddRequest(BaseModel):
    url: str
    requester: str | None = None


class QueueItemResponse(BaseModel):
    track: str
    artist: str
    requester: str | None
    position: int
    url: str


class AddResponse(BaseModel):
    track: str
    artist: str
    position: int


class NowPlayingResponse(BaseModel):
    track: str
    artist: str
    requester: str | None
    url: str


class StatusResponse(BaseModel):
    ok: bool
    message: str


# --- Public endpoints ---


@app.post("/queue", response_model=AddResponse)
async def add_to_queue(body: AddRequest):
    from urllib.parse import urlparse
    parsed = urlparse(body.url)
    valid_hosts = {"www.youtube.com", "youtube.com", "m.youtube.com", "youtu.be", "music.youtube.com"}
    if parsed.hostname not in valid_hosts:
        raise HTTPException(status_code=400, detail="Apenas links do YouTube são aceitos")

    try:
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, get_video_info, body.url)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Não foi possível obter o vídeo: {exc}")

    item = QueueItem(url=body.url, track=info.track, artist=info.artist, requester=body.requester or "Ouvinte Anônimo", artist_confident=info.artist_confident)
    position = music_queue.enqueue(item)
    return AddResponse(track=info.track, artist=info.artist, position=position)


@app.get("/queue", response_model=list[QueueItemResponse])
async def get_queue():
    items = music_queue.list()
    return [
        QueueItemResponse(track=it.track, artist=it.artist, requester=it.requester, position=i + 1, url=it.url)
        for i, it in enumerate(items)
    ]


@app.get("/now-playing", response_model=NowPlayingResponse | None)
async def now_playing():
    item = music_queue.now_playing
    if item is None:
        return None
    return NowPlayingResponse(track=item.track, artist=item.artist, requester=item.requester, url=item.url)


# --- Admin endpoints ---


@app.post("/admin/skip", response_model=StatusResponse)
async def admin_skip(authorization: str | None = Header(default=None)):
    _check_token(authorization)
    if player.skip():
        return StatusResponse(ok=True, message="Música pulada")
    return StatusResponse(ok=False, message="Nenhuma música tocando")


@app.post("/admin/pause", response_model=StatusResponse)
async def admin_pause(authorization: str | None = Header(default=None)):
    _check_token(authorization)
    if player.pause():
        return StatusResponse(ok=True, message="Pausado")
    return StatusResponse(ok=False, message="Não foi possível pausar")


@app.post("/admin/resume", response_model=StatusResponse)
async def admin_resume(authorization: str | None = Header(default=None)):
    _check_token(authorization)
    if player.resume():
        return StatusResponse(ok=True, message="Retomado")
    return StatusResponse(ok=False, message="Não está pausado")


@app.delete("/admin/queue/{position}", response_model=StatusResponse)
async def admin_remove(position: int, authorization: str | None = Header(default=None)):
    _check_token(authorization)
    if music_queue.remove(position):
        return StatusResponse(ok=True, message=f"Item {position} removido da fila")
    return StatusResponse(ok=False, message=f"Posição {position} não encontrada")
