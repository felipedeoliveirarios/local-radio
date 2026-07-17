FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        mpv \
        ffmpeg \
        pulseaudio-utils \
        curl \
        ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

RUN mkdir -p /tmp/local-radio-dl /tmp/uv-cache && chmod 777 /tmp/local-radio-dl /tmp/uv-cache

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

ENV UV_CACHE_DIR=/tmp/uv-cache

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
