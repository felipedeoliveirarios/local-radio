<script setup>
import { ref } from "vue";

const url = ref("");
const requester = ref(localStorage.getItem("requester") || "");
const message = ref("");
const loading = ref(false);

function saveRequester() {
  localStorage.setItem("requester", requester.value.trim());
}

async function submit() {
  if (!url.value.trim()) return;
  loading.value = true;
  message.value = "";

  try {
    const res = await fetch("/queue", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: url.value.trim(),
        requester: requester.value.trim() || null,
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      message.value = `❌ ${err.detail || "Erro ao adicionar"}`;
      return;
    }

    const data = await res.json();
    message.value = `✅ "${data.track}" (${data.artist}) adicionada na posição ${data.position}`;
    url.value = "";
  } catch (e) {
    message.value = "❌ Erro de conexão com o servidor";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <form class="submit-form" @submit.prevent="submit">
    <input
      v-model="url"
      type="url"
      placeholder="Link do YouTube"
      required
    />
    <input
      v-model="requester"
      type="text"
      placeholder="Seu nome (opcional)"
      @blur="saveRequester"
    />
    <button type="submit" :disabled="loading">
      <span v-if="loading" class="spinner"></span>
      {{ loading ? "Adicionando..." : "Adicionar à fila" }}
    </button>
    <p v-if="message" class="message">{{ message }}</p>
  </form>
</template>

<style scoped>
.submit-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

input {
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text);
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus {
  outline: none;
  border-color: var(--primary);
}

input::placeholder {
  color: var(--muted);
}

button {
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  background: var(--primary);
  color: #fff;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover:not(:disabled) {
  background: var(--primary-hover);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  vertical-align: middle;
  margin-right: 0.4rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.message {
  text-align: center;
  font-size: 0.9rem;
}
</style>
