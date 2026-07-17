<script setup>
import { ref, onMounted } from "vue";

const token = ref(localStorage.getItem("admin_token") || "");
const authenticated = ref(false);
const nowPlaying = ref(null);
const queue = ref([]);
const message = ref("");
const paused = ref(false);

function login() {
  if (token.value.trim()) {
    localStorage.setItem("admin_token", token.value.trim());
    authenticated.value = true;
    refresh();
  }
}

function logout() {
  localStorage.removeItem("admin_token");
  token.value = "";
  authenticated.value = false;
}

function headers() {
  return { Authorization: `Bearer ${token.value}` };
}

async function refresh() {
  try {
    const [npRes, qRes] = await Promise.all([
      fetch("/now-playing"),
      fetch("/queue"),
    ]);
    nowPlaying.value = npRes.ok ? await npRes.json() : null;
    queue.value = qRes.ok ? await qRes.json() : [];
  } catch {}
}

async function action(method, url) {
  message.value = "";
  try {
    const res = await fetch(url, { method, headers: headers() });
    const data = await res.json();
    if (res.status === 401) {
      message.value = "❌ Token inválido";
      authenticated.value = false;
      return;
    }
    message.value = data.ok ? `✅ ${data.message}` : `⚠️ ${data.message}`;
    refresh();
  } catch {
    message.value = "❌ Erro de conexão";
  }
}

async function skip() {
  await action("POST", "/admin/skip");
  paused.value = false;
}

async function pause() {
  await action("POST", "/admin/pause");
  paused.value = true;
}

async function resume() {
  await action("POST", "/admin/resume");
  paused.value = false;
}

async function remove(position) {
  await action("DELETE", `/admin/queue/${position}`);
}

onMounted(() => {
  if (token.value) {
    authenticated.value = true;
    refresh();
    setInterval(refresh, 5000);
  }
});
</script>

<template>
  <div class="admin">
    <h1>🎛️ Admin</h1>

    <div v-if="!authenticated" class="login-form">
      <input
        v-model="token"
        type="password"
        placeholder="Token de admin"
        @keyup.enter="login"
      />
      <button @click="login">Entrar</button>
    </div>

    <template v-else>
      <div class="controls">
        <button class="btn-skip" @click="skip">⏭ Pular</button>
        <button class="btn-pause" @click="pause" v-if="!paused">⏸ Pausar</button>
        <button class="btn-resume" @click="resume" v-else>▶ Retomar</button>
        <button class="btn-logout" @click="logout">Sair</button>
      </div>

      <p v-if="message" class="message">{{ message }}</p>

      <div class="now-playing" v-if="nowPlaying">
        <h2>🎵 Tocando agora</h2>
        <p class="track">{{ nowPlaying.track }}</p>
        <p class="artist">{{ nowPlaying.artist }}</p>
      </div>

      <div class="queue-section">
        <h2>📋 Fila</h2>
        <p v-if="queue.length === 0" class="empty">Fila vazia</p>
        <ul v-else>
          <li v-for="item in queue" :key="item.position">
            <span class="info">
              <span class="position">{{ item.position }}.</span>
              <span class="track">{{ item.track }}</span>
              <span class="artist">{{ item.artist }}</span>
            </span>
            <button class="btn-remove" @click="remove(item.position)">✕</button>
          </li>
        </ul>
      </div>
    </template>
  </div>
</template>

<style scoped>
.admin {
  max-width: 600px;
  margin: 0 auto;
  padding: 2rem;
}

h1 {
  text-align: center;
  margin-bottom: 1.5rem;
}

.login-form {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.login-form input {
  padding: 0.6rem 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text);
  font-size: 1rem;
}

.login-form button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  background: var(--primary);
  color: #fff;
  cursor: pointer;
  font-weight: 600;
}

.controls {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.controls button {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.controls button:hover {
  opacity: 0.85;
}

.btn-skip { background: var(--accent); color: #fff; }
.btn-pause { background: var(--primary); color: #fff; }
.btn-resume { background: var(--success); color: #fff; }
.btn-logout { background: var(--border); color: var(--text); }

.message {
  text-align: center;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.now-playing {
  background: var(--surface);
  border-left: 4px solid var(--accent);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.now-playing h2 { font-size: 1rem; margin-bottom: 0.4rem; }
.now-playing .track { font-weight: 600; }
.now-playing .artist { color: var(--primary); font-size: 0.9rem; }

.queue-section h2 {
  font-size: 1.1rem;
  margin-bottom: 0.75rem;
}

.empty {
  color: var(--muted);
  text-align: center;
}

ul {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background: var(--surface);
  border-radius: 6px;
}

li .info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

li .position { color: var(--muted); font-size: 0.8rem; }
li .track { font-weight: 500; font-size: 0.9rem; }
li .artist { color: var(--primary); font-size: 0.8rem; }

.btn-remove {
  background: transparent;
  border: 1px solid var(--error, #ff5555);
  color: var(--error, #ff5555);
  width: 1.8rem;
  height: 1.8rem;
  border-radius: 50%;
  cursor: pointer;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.btn-remove:hover {
  background: var(--error, #ff5555);
  color: #fff;
}
</style>
