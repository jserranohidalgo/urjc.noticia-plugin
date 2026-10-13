#!/usr/bin/env bash
# Sube un fichero a TU OneDrive (la cuenta de usuario.json) y devuelve una URL de descarga directa pública
# (solo lectura), para adjuntarlo en Buffer. Ver subir-onedrive.mjs.
#
#   subir-onedrive.sh <fichero>
#
# macOS/Linux. Requiere Node.js, un navegador Chromium (Chrome, Edge, Brave…) y python3 (solo para leer el JSON).
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/../lib/navegador.sh"
FICHERO="${1:?uso: subir-onedrive.sh <fichero>}"

exigir_usuario
asegurar_playwright
asegurar_ventana "$PERFIL" "$PUERTO" "$APLICACION"
PLAYWRIGHT_CORE_DIR="$NODE_DIR" exec node "$DIR/subir-onedrive.mjs" "$FICHERO" "$USUARIO_JSON"
