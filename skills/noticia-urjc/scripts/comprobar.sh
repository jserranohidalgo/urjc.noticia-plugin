#!/usr/bin/env bash
# Comprueba de antemano todo lo que van a necesitar los pasos siguientes y lo dice todo a la vez, para que la
# persona pueda arreglarlo (conectar la VPN, iniciar sesión…) mientras el agente redacta la noticia.
#
#   comprobar.sh <web|video|redes|todo> [escuela.json]
#
#   web    configuración, Python con Pillow, Node.js, navegador Chromium, VPN y sesión en la intranet (eris)
#   video  además, sesión en OneDrive (para subir el vídeo)
#   redes  bloque buffer de escuela.json (las herramientas MCP de Buffer las comprueba el agente)
#   todo   todo lo anterior
#
# Una línea por comprobación: «OK …», «FALTA …» (impide seguir) o «AVISO …» (se puede seguir). Sale con código 1
# si hay algún FALTA. Si falta iniciar sesión, deja la ventana del navegador en la pantalla de login.
# Sin escuela.json, usa el único ~/.config/noticia-urjc/*/escuela.json si solo hay uno.
#
# macOS/Linux.
set -uo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/lib/navegador.sh"
FASE="${1:?uso: comprobar.sh <web|video|redes|todo> [escuela.json]}"
ESCUELA="${2:-}"
FALTAS=0

ok()    { echo "OK $*"; }
falta() { echo "FALTA $*"; FALTAS=$((FALTAS + 1)); }
aviso() { echo "AVISO $*"; }
quiere() { [ "$FASE" = "todo" ] || [[ " $* " == *" $FASE "* ]]; }

# --- Configuración ------------------------------------------------------------------------------------------
if [ -z "$ESCUELA" ]; then
  CANDIDATAS=()
  for f in "$HOME"/.config/noticia-urjc/*/escuela.json; do [ -f "$f" ] && CANDIDATAS+=("$f"); done
  if [ "${#CANDIDATAS[@]}" -eq 1 ]; then ESCUELA="${CANDIDATAS[0]}"; fi
  if [ "${#CANDIDATAS[@]}" -gt 1 ]; then aviso "escuela: hay varias configuradas; indica cuál como segundo argumento"; fi
fi
SLUG="-"
if [ -n "$ESCUELA" ] && [ -f "$ESCUELA" ]; then
  FALTAN_CAMPOS="$(python3 -c 'import json,sys; e=json.load(open(sys.argv[1])); print(" ".join(k for k in ["siglas","kicker","slugCMS","categoriaCMS","etiquetaCMS","colorMarca","logo","carpetaLog"] if not e.get(k)))' "$ESCUELA")"
  SLUG="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("slugCMS") or "-")' "$ESCUELA")"
  if [ -n "$FALTAN_CAMPOS" ]; then falta "escuela: faltan campos en $ESCUELA: $FALTAN_CAMPOS"; else ok "escuela: $ESCUELA"; fi
  LOGO="$(python3 -c 'import json,os,sys; print(os.path.expanduser(json.load(open(sys.argv[1])).get("logo") or ""))' "$ESCUELA")"
  [ -n "$LOGO" ] && [ ! -f "$LOGO" ] && aviso "escuela: no existe el logo $LOGO (el banner saldría sin logo)"
else
  falta "escuela: no hay escuela.json (configúrala con la URL de su página en urjc.es)"
fi

if quiere web video; then
  if exigir_usuario 2>/dev/null; then ok "usuario: $USUARIO_JSON (puerto $PUERTO)"; else falta "usuario: falta $USUARIO_JSON o su navegador (perfil, puerto)"; fi
fi

# --- Herramientas -------------------------------------------------------------------------------------------
if quiere web video; then
  PY_PIL=""
  for p in python3 /usr/local/bin/python3 /opt/homebrew/bin/python3; do
    if command -v "$p" >/dev/null && "$p" -c "import PIL" 2>/dev/null; then PY_PIL="$(command -v "$p")"; break; fi
  done
  if [ -n "$PY_PIL" ]; then ok "python con Pillow: $PY_PIL"; else aviso "ningún python3 tiene Pillow: no se podrán generar imágenes (python3 -m pip install --user pillow)"; fi
  if command -v node >/dev/null && command -v npm >/dev/null; then ok "node $(node -v)"; else falta "node/npm no instalados: no se podrá rellenar el CMS ni subir vídeos"; fi
  APP="$(elegir_navegador "${APLICACION:-}" 2>/dev/null)" && ok "navegador: $APP" || falta "navegador: no hay ningún navegador de la familia Chromium (Chrome, Edge, Brave…)"
fi

# --- Red ----------------------------------------------------------------------------------------------------
VPN_OK=0
if quiere web; then
  if python3 -c 'import socket; socket.gethostbyname("eris.urjc.es")' 2>/dev/null; then
    ok "vpn: eris.urjc.es resuelve"; VPN_OK=1
  elif SALIDA="$(sh "$DIR/lib/vpn/conectar.sh" 2>&1)"; then
    ok "vpn: no estaba conectada y se ha conectado ($SALIDA)"; VPN_OK=1
  else
    falta "vpn: eris.urjc.es no resuelve y no se ha podido conectar sola: $SALIDA"
  fi
fi

# --- Sesiones (necesitan el navegador) ----------------------------------------------------------------------
QUE=()
if quiere web && [ "$VPN_OK" = 1 ] && [ "$SLUG" != "-" ]; then QUE+=(eris); fi
if quiere video; then QUE+=(onedrive); fi
if [ "${#QUE[@]}" -gt 0 ] && [ -n "${PUERTO:-}" ] && command -v node >/dev/null; then
  if asegurar_playwright >/dev/null && asegurar_ventana "$PERFIL" "$PUERTO" "${APLICACION:-}" >/dev/null; then
    while IFS= read -r linea; do
      case "$linea" in
        OK*) echo "$linea" ;;
        FALTA*) echo "$linea"; FALTAS=$((FALTAS + 1)) ;;
        *) echo "$linea" ;;
      esac
    done < <(PLAYWRIGHT_CORE_DIR="$NODE_DIR" node "$DIR/lib/comprobar-sesiones.mjs" "$USUARIO_JSON" "$SLUG" "${QUE[@]}" 2>&1)
  else
    falta "navegador: no se ha podido abrir la ventana en el puerto $PUERTO"
  fi
fi

# --- Buffer ---------------------------------------------------------------------------------------------------
if quiere redes && [ -n "$ESCUELA" ] && [ -f "$ESCUELA" ]; then
  if python3 -c 'import json,sys; b=json.load(open(sys.argv[1])).get("buffer") or {}; sys.exit(0 if b.get("organizacion") and b.get("canales") else 1)' "$ESCUELA"; then
    ok "buffer: organización y canales en escuela.json"
  else
    aviso "buffer: falta el bloque buffer en escuela.json (se rellena con get_account y list_channels)"
  fi
fi

exit $(( FALTAS > 0 ? 1 : 0 ))
