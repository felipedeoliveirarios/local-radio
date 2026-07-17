#!/bin/bash
# Detecta IP da rede local e sobe o docker compose
export HOST_IP=$(hostname -I | awk '{print $1}')
export ADMIN_TOKEN=${ADMIN_TOKEN:-changeme}

URL="http://$HOST_IP:8080"

echo ""
echo "📻 Local Radio"
echo "   URL:   $URL"
echo "   Admin: $URL/#/admin (token: $ADMIN_TOKEN)"
echo "   QR:    $URL/#/qr"
echo ""

# Exibe QR code no terminal se qrencode estiver instalado
if command -v qrencode &>/dev/null; then
    qrencode -t ANSIUTF8 "$URL"
    echo ""
fi

exec docker compose up "$@"
