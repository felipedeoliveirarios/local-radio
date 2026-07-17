<script setup>
import { ref, onMounted } from "vue";

const nowPlaying = ref(null);
const queue = ref([]);
const loading = ref(true);
const refreshing = ref(false);

async function refresh() {
  refreshing.value = true;
  try {
    const [npRes, qRes] = await Promise.all([
      fetch("/now-playing"),
      fetch("/queue"),
    ]);
    nowPlaying.value = npRes.ok ? await npRes.json() : null;
    queue.value = qRes.ok ? await qRes.json() : [];
  } catch {
    // silencioso em caso de erro de rede
  } finally {
    loading.value = false;
    refreshing.value = false;
  }
}

onMounted(() => {
  refresh();
  setInterval(refresh, 10000);
});
</script>

<template>
  <section class="queue-view">
    <div class="now-playing" :class="{ playing: nowPlaying }">
      <h2>🎵 Tocando agora</h2>
      <template v-if="loading">
        <div class="skeleton skeleton-line"></div>
        <div class="skeleton skeleton-line short"></div>
      </template>
      <template v-else-if="nowPlaying">
        <div class="track-row">
          <p class="track">{{ nowPlaying.track }}</p>
          <a :href="nowPlaying.url" target="_blank" rel="noopener" class="yt-link" title="Abrir no YouTube">▶</a>
        </div>
        <p class="artist">{{ nowPlaying.artist }}</p>
        <p class="requester" v-if="nowPlaying.requester">
          Pedido de <strong>{{ nowPlaying.requester }}</strong>
        </p>
      </template>
      <p v-else class="empty">Nenhuma música tocando</p>
    </div>

    <div class="queue-list">
      <div class="queue-header">
        <h2>📋 Fila</h2>
        <button class="refresh-btn" :class="{ spinning: refreshing }" @click="refresh">
          <span class="refresh-icon">↻</span> Atualizar
        </button>
      </div>

      <template v-if="loading">
        <div v-for="n in 3" :key="n" class="skeleton-item">
          <div class="skeleton skeleton-line"></div>
          <div class="skeleton skeleton-line short"></div>
        </div>
      </template>

      <p v-else-if="queue.length === 0" class="empty">Fila vazia</p>

      <ul v-else>
        <li v-for="item in queue" :key="item.position" class="queue-item">
          <span class="position">{{ item.position }}.</span>
          <span class="info">
            <span class="track-row">
              <span class="track">{{ item.track }}</span>
              <a :href="item.url" target="_blank" rel="noopener" class="yt-link" title="Abrir no YouTube">▶</a>
            </span>
            <span class="artist">{{ item.artist }}</span>
            <span class="requester" v-if="item.requester">
              Pedido de {{ item.requester }}
            </span>
          </span>
        </li>
      </ul>
    </div>
  </section>
</template>

<style scoped>
.queue-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.now-playing {
  background: var(--surface);
  border-left: 4px solid var(--accent);
  padding: 1rem 1.25rem;
  border-radius: 6px;
  transition: border-color 0.3s;
}

.now-playing.playing {
  animation: pulse-border 2s ease-in-out infinite;
}

@keyframes pulse-border {
  0%, 100% { border-left-color: var(--accent); }
  50% { border-left-color: var(--primary); }
}

.now-playing h2 {
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.now-playing .track {
  font-size: 1.1rem;
  font-weight: 600;
}

.track-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.yt-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.4rem;
  height: 1.4rem;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-size: 0.65rem;
  text-decoration: none;
  flex-shrink: 0;
  transition: opacity 0.2s;
}

.yt-link:hover {
  opacity: 0.8;
}

.now-playing .artist {
  color: var(--primary);
  font-size: 0.9rem;
  margin-top: 0.15rem;
}

.now-playing .requester {
  color: var(--muted);
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.queue-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.queue-header h2 {
  font-size: 1.1rem;
}

.refresh-btn {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.refresh-btn:hover {
  background: var(--border);
}

.refresh-icon {
  display: inline-block;
  transition: transform 0.3s;
}

.refresh-btn.spinning .refresh-icon {
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty {
  color: var(--muted);
  text-align: center;
  padding: 1rem;
}

ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

li.queue-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.6rem 1rem;
  background: var(--surface);
  border-radius: 6px;
  animation: fade-in 0.3s ease-out;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(4px); }
  to { opacity: 1; transform: translateY(0); }
}

.position {
  color: var(--primary);
  font-weight: 700;
  min-width: 1.5rem;
}

.info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.info .track {
  font-weight: 500;
}

.info .artist {
  color: var(--primary);
  font-size: 0.85rem;
}

.info .requester {
  color: var(--muted);
  font-size: 0.8rem;
}

/* Skeleton loading */
.skeleton {
  background: linear-gradient(90deg, var(--border) 25%, var(--surface) 50%, var(--border) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
  height: 1rem;
  margin-top: 0.4rem;
}

.skeleton-line {
  width: 80%;
}

.skeleton-line.short {
  width: 50%;
}

.skeleton-item {
  padding: 0.6rem 1rem;
  background: var(--surface);
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
