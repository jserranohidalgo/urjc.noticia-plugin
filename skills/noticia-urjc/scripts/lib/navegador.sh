#!/usr/bin/env bash
# Funciones comunes para los scripts que operan una ventana de Chrome por CDP (CMS, OneDrive).
# Se carga con `source`. macOS/Linux. Requiere Node.js, Google Chrome y python3 (solo para leer el JSON).

PLAYWRIGHT_CORE_VERSION="1.62.1"
NODE_DIR="$HOME/.cache/noticia-urjc/node"
# Configuración personal (cuenta, perfil de Chrome, puerto, OneDrive): no es de ninguna Escuela.
USUARIO_JSON="${NOTICIA_URJC_USUARIO:-$HOME/.config/noticia-urjc/usuario.json}"

# leer_bloque <fichero.json> <bloque> <campo>: imprime fichero[bloque][campo], con ~ expandido.
leer_bloque() {
  python3 -c 'import json,os,sys; v=json.load(open(sys.argv[1])).get(sys.argv[2],{}).get(sys.argv[3],""); print(os.path.expanduser(str(v)))' "$1" "$2" "$3"
}

# exigir_usuario: falla si no existe usuario.json o le falta navegador.perfil / navegador.puerto, y deja ambos
# en PERFIL y PUERTO.
exigir_usuario() {
  if [ ! -f "$USUARIO_JSON" ]; then
    echo "ERROR no existe $USUARIO_JSON (cuenta, navegador.perfil, navegador.puerto): ver config/usuario.ejemplo.json" >&2
    return 1
  fi
  PERFIL="$(leer_bloque "$USUARIO_JSON" navegador perfil)"
  PUERTO="$(leer_bloque "$USUARIO_JSON" navegador puerto)"
  if [ -z "$PERFIL" ] || [ -z "$PUERTO" ]; then
    echo "ERROR falta navegador.perfil o navegador.puerto en $USUARIO_JSON" >&2
    return 1
  fi
}

# asegurar_playwright: instala playwright-core (versión fija) en $NODE_DIR la primera vez.
asegurar_playwright() {
  if [ ! -d "$NODE_DIR/node_modules/playwright-core" ]; then
    echo "Instalando playwright-core@$PLAYWRIGHT_CORE_VERSION en ${NODE_DIR}…"
    npm install --silent --no-audit --no-fund --prefix "$NODE_DIR" "playwright-core@$PLAYWRIGHT_CORE_VERSION" >&2
  fi
}

# asegurar_ventana <perfil> <puerto>: reutiliza la ventana si el puerto responde; si no, abre CON VENTANA
# Chrome con ese perfil y ese puerto (la persona tiene que ver lo que pasa) y espera a que responda.
asegurar_ventana() {
  local perfil="$1" puerto="$2"
  if curl -s -m 2 "http://localhost:$puerto/json/version" >/dev/null; then
    # Chrome sigue vivo pero sin ventanas (la persona las cerró): sin pestañas no hay contexto al que
    # engancharse, así que se abre una.
    if ! curl -s -m 2 "http://localhost:$puerto/json/list" | grep -q '"type": *"page"'; then
      curl -s -m 5 -X PUT "http://localhost:$puerto/json/new?about:blank" >/dev/null
      sleep 1
    fi
    return 0
  fi
  echo "Abriendo Chrome con el perfil ${perfil} en el puerto ${puerto}…"
  if [ "$(uname)" = "Darwin" ]; then
    open -na "Google Chrome" --args --remote-debugging-port="$puerto" --user-data-dir="$perfil" --window-size=1400,1000
  else
    (google-chrome --remote-debugging-port="$puerto" --user-data-dir="$perfil" --window-size=1400,1000 >/dev/null 2>&1 &)
  fi
  for _ in $(seq 1 40); do
    curl -s -m 1 "http://localhost:$puerto/json/version" >/dev/null && return 0
    sleep 0.5
  done
  echo "ERROR Chrome no responde en el puerto $puerto" >&2
  return 1
}
