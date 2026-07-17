# 📻 Local Radio

Rádio local colaborativa. Qualquer pessoa na rede pode adicionar músicas do YouTube à fila. O servidor reproduz as músicas em sequência nas caixas de som conectadas, com narração estilo rádio entre as faixas.

## Como funciona

- Front-end web pra enviar links e visualizar a fila
- Back-end baixa o áudio, gera narração TTS e reproduz localmente
- Narração com variações de texto e voz neural em pt-BR (edge-tts)
- Extração inteligente de artista/título dos metadados do vídeo
- Pré-download da próxima música pra transição suave entre faixas
- QR code pra compartilhar acesso com quem estiver na mesma rede

## Requisitos

- Docker e Docker Compose
- PulseAudio ou PipeWire (pra saída de áudio do container)

## Rodando

```bash
./start.sh --build
```

O script detecta o IP da rede local automaticamente e exibe:

```
📻 Local Radio
   URL:   http://192.168.x.x:8080
   Admin: http://192.168.x.x:8080/#/admin (token: changeme)
   QR:    http://192.168.x.x:8080/#/qr
```

Se tiver `qrencode` instalado (`sudo apt install qrencode`), exibe o QR code direto no terminal.

O áudio sai pelas caixas da máquina que roda o Docker.

## Painel Admin

Acesse `http://localhost:8080/#/admin` pra controlar a rádio:

- Pular música atual
- Pausar / retomar reprodução
- Remover itens da fila

O token padrão é `changeme`. Pra personalizar:

```bash
ADMIN_TOKEN=minhaSenha ./start.sh --build
```

## QR Code

Acesse `http://localhost:8080/#/qr` pra exibir um QR code fullscreen — ideal pra projetar num monitor ou TV.

## Stack

| Camada | Tecnologia |
|--------|-----------|
| API | FastAPI |
| Download | yt-dlp |
| TTS | edge-tts (pt-BR-AntonioNeural) |
| Player | mpv |
| Front-end | Vue 3 + Vite |
| Servidor web | Nginx (proxy + SPA) |

## Estrutura

```
├── docker-compose.yml
├── start.sh               # Script de inicialização
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml / uv.lock
│   ├── main.py            # API FastAPI
│   ├── music_queue.py     # Fila thread-safe
│   ├── player.py          # Loop de reprodução + prefetch
│   ├── downloader.py      # Download + extração de metadados
│   ├── narrator.py        # Geração de narração TTS
│   └── templates.py       # Variações de locução
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    └── src/
        ├── App.vue
        └── components/
            ├── SubmitForm.vue
            ├── QueueView.vue
            ├── AdminPanel.vue
            └── QrPage.vue
```

## Configuração

O áudio do container chega ao host via PulseAudio socket. O `docker-compose.yml` mapeia `/run/user/1000/pulse` — ajuste o UID se necessário.

## Desenvolvimento local (sem Docker)

```bash
# Back-end
cd backend
uv sync
uv run uvicorn main:app --reload

# Front-end
cd frontend
npm install
npm run dev   # localhost:5173, proxy pro backend em :8000
```

Requer `mpv` e `ffmpeg` instalados no sistema.
