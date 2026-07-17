<script setup>
import { ref, onMounted } from "vue";
import SubmitForm from "./components/SubmitForm.vue";
import QueueView from "./components/QueueView.vue";
import AdminPanel from "./components/AdminPanel.vue";

const dark = ref(true);
const route = ref(window.location.hash);

function toggleTheme() {
  dark.value = !dark.value;
  localStorage.setItem("theme", dark.value ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", dark.value ? "dark" : "light");
}

onMounted(() => {
  const saved = localStorage.getItem("theme");
  if (saved) {
    dark.value = saved === "dark";
  }
  document.documentElement.setAttribute("data-theme", dark.value ? "dark" : "light");

  window.addEventListener("hashchange", () => {
    route.value = window.location.hash;
  });
});
</script>

<template>
  <div class="app">
    <template v-if="route === '#/admin'">
      <AdminPanel />
    </template>
    <template v-else>
      <header>
        <h1>📻 Local Radio</h1>
        <button class="theme-toggle" @click="toggleTheme">
          {{ dark ? "☀️" : "🌙" }}
        </button>
      </header>
      <div class="columns">
        <div class="col-left">
          <SubmitForm />
          <div class="qr-section">
            <p class="qr-label">Escaneie pra acessar:</p>
            <img :src="'/qrcode'" alt="QR Code" class="qr-code" />
          </div>
        </div>
        <div class="col-right">
          <QueueView />
        </div>
      </div>
    </template>
  </div>
</template>

<style>
:root[data-theme="dark"] {
  --bg: #282a36;
  --surface: #343746;
  --primary: #bd93f9;
  --primary-hover: #caa8fc;
  --text: #f8f8f2;
  --muted: #6272a4;
  --border: #44475a;
  --accent: #ff79c6;
  --success: #50fa7b;
  --error: #ff5555;
}

:root[data-theme="light"] {
  --bg: #f8f8f2;
  --surface: #ffffff;
  --primary: #7c3aed;
  --primary-hover: #6d28d9;
  --text: #282a36;
  --muted: #6272a4;
  --border: #d4d4d8;
  --accent: #db2777;
  --success: #16a34a;
  --error: #dc2626;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  padding: 2rem;
  transition: background 0.3s, color 0.3s;
}

.app {
  max-width: 1000px;
  margin: 0 auto;
}

header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 2rem;
}

h1 {
  text-align: center;
  font-size: 1.8rem;
}

.theme-toggle {
  position: absolute;
  right: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.4rem 0.6rem;
  font-size: 1.2rem;
  cursor: pointer;
  transition: background 0.2s;
}

.theme-toggle:hover {
  background: var(--border);
}

.columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  align-items: start;
}

@media (max-width: 700px) {
  .columns {
    grid-template-columns: 1fr;
  }
}

.qr-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background: var(--surface);
  border-radius: 6px;
}

.qr-label {
  font-size: 0.85rem;
  color: var(--muted);
}

.qr-code {
  width: 160px;
  height: 160px;
  border-radius: 4px;
  background: #fff;
  padding: 8px;
}
</style>
