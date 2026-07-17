from __future__ import annotations

import asyncio
import tempfile
import uuid
from pathlib import Path

import edge_tts

VOICE = "pt-BR-AntonioNeural"
NARRATION_DIR = Path(tempfile.gettempdir()) / "local-radio-dl"
NARRATION_DIR.mkdir(exist_ok=True)


async def _generate(text: str, output: Path) -> None:
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(str(output))


def generate_narration(text: str) -> Path:
    """Gera arquivo MP3 de narração a partir do texto. Síncrono (bloqueia)."""
    output = NARRATION_DIR / f"narration-{uuid.uuid4().hex[:8]}.mp3"
    asyncio.run(_generate(text, output))
    return output
