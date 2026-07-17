#!/bin/bash
# Detecta IP da rede local e sobe o docker compose
export HOST_IP=$(hostname -I | awk '{print $1}')
export ADMIN_TOKEN=${ADMIN_TOKEN:-changeme}
echo "📻 Local Radio — http://$HOST_IP:8080"
echo "🎛️ Admin — http://$HOST_IP:8080/#/admin (token: $ADMIN_TOKEN)"
exec docker compose up "$@"
