import random
import re


def _clean(text: str) -> str:
    """Remove textos entre parênteses e colchetes."""
    text = re.sub(r"\s*[\(\[][^)\]]*[\)\]]", "", text)
    return text.strip()


# --- Com artista + requester ---

TEMPLATES_FULL = [
    "Agora tocando {track}, de {artist}, a pedido de {requester}.",
    "Essa é pra você, {requester}! Vem aí: {track}, de {artist}.",
    "{requester} mandou bem! Próxima: {track}, de {artist}.",
    "Atendendo ao pedido de {requester}, com vocês: {artist}, {track}.",
    "E agora, {track}! {artist} na voz, {requester} no pedido.",
    "Vem som novo! {requester} escolheu {track}, de {artist}.",
    "{track}, de {artist}. Dedicação especial de {requester}.",
    "O DJ {requester} manda: {artist} com {track}!",
    "Segura que vem hit! {requester} trouxe {artist} pra gente. É {track}.",
    "Chegou a vez de {requester}! Solta o play: {artist}, {track}.",
    "Atenção, galera! {requester} tá comandando com {artist}.",
    "Pedido anotado! {requester} quer ouvir {track}, de {artist}.",
    "Quem manda agora é {requester}, e o som é {artist} com {track}.",
    "Olha o gosto refinado de {requester}! Bora de {artist}, {track}.",
    "Direto do pedido de {requester}: {track}, na voz de {artist}.",
]

# --- Com artista, sem requester ---

TEMPLATES_ARTIST_ONLY = [
    "Agora tocando: {track}, de {artist}.",
    "Próxima na fila: {artist} com {track}.",
    "Vem aí: {track}, de {artist}.",
    "E agora, com vocês: {artist}, {track}!",
    "Solta o som! {artist}, {track}.",
    "Mais uma pra vocês: {track}, de {artist}.",
    "Olha o que chegou: {artist} com {track}.",
    "Hora de {artist}! É {track}.",
]

# --- Sem artista, com requester (fallback título inteiro) ---

TEMPLATES_NO_ARTIST = [
    "Agora tocando {track}, a pedido de {requester}.",
    "Essa é pra você, {requester}! Vem aí: {track}.",
    "{requester} mandou bem! Próxima na fila: {track}.",
    "E agora, {track}! Quem pediu foi {requester}.",
    "Vem som novo! {requester} escolheu {track}.",
    "O DJ {requester} manda: {track}!",
    "Segura que vem hit! {requester} trouxe {track} pra gente.",
    "Chegou a vez de {requester}! Solta o play: {track}.",
]

# --- Sem artista, sem requester ---

TEMPLATES_BARE = [
    "Agora tocando: {track}.",
    "Próxima na fila: {track}.",
    "Vem aí: {track}.",
    "E agora, com vocês: {track}!",
    "Toca aí: {track}.",
    "Solta o som! {track}.",
    "Mais uma pra vocês: {track}.",
]


def pick_template(track: str, artist: str | None, requester: str | None) -> str:
    """Escolhe template aleatório e formata com track, artist e requester."""
    track = _clean(track)
    if artist:
        artist = _clean(artist)

    has_artist = bool(artist)
    has_requester = bool(requester)

    if has_artist and has_requester:
        templates = TEMPLATES_FULL
    elif has_artist:
        templates = TEMPLATES_ARTIST_ONLY
    elif has_requester:
        templates = TEMPLATES_NO_ARTIST
    else:
        templates = TEMPLATES_BARE

    return random.choice(templates).format(
        track=track, artist=artist or "", requester=requester or ""
    )
