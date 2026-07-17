from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yt_dlp

DOWNLOAD_DIR = Path(tempfile.gettempdir()) / "local-radio-dl"
DOWNLOAD_DIR.mkdir(exist_ok=True)


@dataclass
class VideoInfo:
    track: str
    artist: str
    title: str  # título original completo


def _sanitize_url(url: str) -> str:
    """Extrai apenas o vídeo, removendo parâmetros de playlist/radio."""
    parsed = urlparse(url)
    if parsed.hostname in ("youtu.be",):
        # youtu.be/VIDEO_ID?list=... → limpa query params
        video_id = parsed.path.lstrip("/")
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
    params = parse_qs(parsed.query)
    video_id = params.get("v", [None])[0]
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


def _base_opts() -> dict:
    """Opções base compartilhadas entre extração e download."""
    return {
        "quiet": True,
        "no_warnings": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        },
    }


def _extract_track_artist(info: dict) -> VideoInfo:
    """Extrai track e artist dos metadados. Fallback: título e canal."""
    track = info.get("track") or ""
    artist = info.get("artist") or ""

    title = info.get("title", "Sem título")
    channel = info.get("channel") or info.get("uploader") or ""

    if not track:
        # Heurística: muitos vídeos usam "Artista - Título" ou "Título - Artista"
        separator = " - " if " - " in title else (" — " if " — " in title else "")
        if separator:
            left, right = title.split(separator, 1)
            left, right = left.strip(), right.strip()

            # Usa o canal pra decidir qual lado é o artista
            channel_lower = channel.lower()
            if channel_lower and channel_lower in right.lower():
                # Canal aparece no lado direito → direito é artista
                artist = artist or right
                track = left
            else:
                # Padrão: lado esquerdo é artista (caso mais comum)
                artist = artist or left
                track = right
        else:
            track = title

    if not artist:
        artist = channel

    return VideoInfo(track=track, artist=artist, title=title)


def get_video_info(url: str) -> VideoInfo:
    """Extrai metadados do vídeo sem baixar."""
    url = _sanitize_url(url)
    opts = {**_base_opts(), "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return _extract_track_artist(info)


def download_audio(url: str) -> Path:
    """Baixa áudio do vídeo e retorna caminho do arquivo."""
    url = _sanitize_url(url)
    opts = {
        **_base_opts(),
        "format": "bestaudio*/best",
        "outtmpl": str(DOWNLOAD_DIR / "%(id)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info["id"]
    return DOWNLOAD_DIR / f"{video_id}.mp3"
