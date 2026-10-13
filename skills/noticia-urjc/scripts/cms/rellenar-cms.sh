#!/usr/bin/env bash
# Rellena el formulario del CMS de la web de la Escuela con una noticia, sin guardarla.
#
#   rellenar-cms.sh <carpeta-noticia> <escuela.json>
#
# 1. Instala playwright-core (versión fija) en ~/.cache/noticia-urjc/node la primera vez.
# 2. Si el puerto de tu navegador (usuario.json) no responde, abre CON VENTANA tu perfil de Chrome en ese
#    puerto: la persona tiene que ver el formulario para pulsar Guardar y Cerrar.
# 3. Ejecuta rellenar-cms.mjs, que navega hasta el formulario y lo rellena (ver sus códigos de salida).
#
# macOS/Linux. Requiere Node.js, Google Chrome y python3 (solo para leer el JSON).
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/../lib/navegador.sh"
NOTICIA="${1:?uso: rellenar-cms.sh <carpeta-noticia> <escuela.json>}"
ESCUELA="${2:?uso: rellenar-cms.sh <carpeta-noticia> <escuela.json>}"

exigir_usuario
asegurar_playwright
asegurar_ventana "$PERFIL" "$PUERTO"
PLAYWRIGHT_CORE_DIR="$NODE_DIR" exec node "$DIR/rellenar-cms.mjs" "$NOTICIA" "$ESCUELA" "$USUARIO_JSON"
