<template>
  <div class="qr-page">
    <h1>📻 Local Radio</h1>
    <p class="subtitle">Escaneie pra pedir sua música</p>
    <img :src="'/qrcode'" alt="QR Code" class="qr" />
    <p class="url">{{ url }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const url = ref("");

onMounted(async () => {
  // Pega o URL do QR a partir do mesmo endpoint (extrai do SVG seria complexo)
  // Melhor: endpoint dedicado
  try {
    const res = await fetch("/qrcode-url");
    if (res.ok) {
      const data = await res.json();
      url.value = data.url;
    }
  } catch {
    url.value = window.location.origin;
  }
});
</script>

<style scoped>
.qr-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  gap: 1.5rem;
  padding: 2rem;
}

h1 {
  font-size: 2.5rem;
}

.subtitle {
  font-size: 1.2rem;
  color: var(--muted);
}

.qr {
  width: 280px;
  height: 280px;
  background: #fff;
  padding: 16px;
  border-radius: 12px;
}

.url {
  font-size: 1.1rem;
  font-family: monospace;
  color: var(--primary);
}
</style>
