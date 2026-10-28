#!/bin/sh
# Conecta la VPN de la Universidad (GlobalProtect) si está caída, sin MFA.
#
#     sh scripts/lib/vpn/conectar.sh [--comprobar | --desconectar] [--host eris.urjc.es] [--espera 90]
#
# Copia de `src/main/infra/vpn/conectar.sh` del modelo `etsii.profesion`: lo que se
# corrija en uno se lleva al otro. macOS; en otro sistema no hace nada (código 4).
#
# La VPN se cae sola (el 2026-10-27, tres veces en una tarde: «Tunnel is down due
# to keep-alive timeout», en `pan_gp_event.log`), y volver a conectar no pide
# MFA: GlobalProtect guarda la cookie de la última autenticación SAML, y con ella
# entra en el portal y en la pasarela sin preguntar («Auto Gateway login»). Lo
# único que falta es pulsar «Conectar», porque el modo es *on-demand*. Este
# programa lo pulsa, por la interfaz de la app (System Events), y espera a que
# el host interno resuelva.
#
# Requiere que la persona dé una vez permiso de **Accesibilidad** (Ajustes del
# Sistema → Privacidad y seguridad → Accesibilidad) a la aplicación desde la que
# corre el agente (el terminal). Sin él, termina con 3 y lo dice.
#
# Con --comprobar solo dice si está conectada (0) o no (1), sin tocar nada. Con
# --desconectar la desconecta, por la misma vía: sirve para probar la reconexión.
#
# Códigos: 0 hecho (o ya lo estaba); 1 no conectada (con --comprobar);
# 3 falta el permiso de Accesibilidad (paso de la persona); 4 GlobalProtect no
# está abierto o no se encuentra el botón (se dicen los que hay); 5 pulsado,
# pero no cambia en la espera: al conectar, la cookie habrá caducado y hay que
# iniciar sesión (con MFA) en la ventana de GlobalProtect, que es paso de la
# persona; 6 el túnel está arriba pero el host no resuelve: el DNS del sistema
# no es el de la VPN (con Tailscale y su DNS activo, el 2026-10-28: Tailscale
# había tomado como DNS del sistema el del router, con la VPN caída, y no ve el
# de la VPN; ver `okf/navegador.md`).

HOST=eris.urjc.es
ESPERA=90
COMPROBAR=
DESCONECTAR=
while [ $# -gt 0 ]; do
  case "$1" in
    --host) HOST=$2; shift 2 ;;
    --espera) ESPERA=$2; shift 2 ;;
    --comprobar) COMPROBAR=1; shift ;;
    --desconectar) DESCONECTAR=1; shift ;;
    *) echo "argumento desconocido: $1" >&2; exit 2 ;;
  esac
done

# Un host interno solo resuelve con la VPN (DNS partido): es la señal, como en
# `comprobar.sh`.
conectada() { python3 -c 'import socket,sys; socket.gethostbyname(sys.argv[1])' "$HOST" 2>/dev/null; }

# ¿El túnel está arriba y lo que falla es el nombre? Lo dice el botón del panel. Si es eso, termina con 6.
sin_dns() {
  case "$(osascript "$(dirname "$0")/globalprotect.applescript" estado 2>&1)" in
    *Disconnect*|*Desconectar*)
      dns=""
      if command -v tailscale >/dev/null && tailscale dns status 2>/dev/null | grep -q 'Tailscale DNS: enabled'; then
        dns=" Tailscale resuelve los nombres (su DNS está activo) y no ve el de la VPN: reiniciar Tailscale con la VPN arriba, o 'tailscale set --accept-dns=false', es decisión de la persona"
      fi
      echo "vpn: el túnel está arriba, pero $HOST no resuelve: el DNS del sistema no es el de la VPN.$dns" >&2
      exit 6 ;;
  esac
}

if [ -n "$COMPROBAR" ]; then
  if conectada; then echo "vpn: conectada ($HOST resuelve)"; exit 0; fi
  echo "vpn: no conectada ($HOST no resuelve)"; exit 1
fi
if [ -n "$DESCONECTAR" ]; then
  if ! conectada; then echo "vpn: ya estaba desconectada"; exit 0; fi
  QUIERO=desconectar
else
  if conectada; then echo "vpn: conectada ($HOST resuelve)"; exit 0; fi
  QUIERO=conectar
fi
if [ "$(uname)" != Darwin ]; then
  echo "vpn: conectarla solo se sabe hacer en macOS: conéctala a mano" >&2; exit 4
fi
if ! pgrep -qx GlobalProtect; then
  echo "vpn: GlobalProtect no está abierto: ábrelo (open -a GlobalProtect) y repite" >&2; exit 4
fi
[ "$QUIERO" = conectar ] && sin_dns

# El icono de la barra de menús abre el panel, y en él está el botón de conectar
# o desconectar («Connect»/«Conectar», «Disconnect»/«Desconectar», según el
# idioma). Si no se encuentra, se dicen los elementos que hay, para corregirlo.
salida=$(osascript "$(dirname "$0")/globalprotect.applescript" "$QUIERO" 2>&1)
case "$salida" in
  # -1719 también es «índice no válido» (sin panel abierto): solo cuenta el texto del permiso.
  *"assistive access"*|*"acceso de asistencia"*|*-25211*)
    echo "vpn: sin permiso de Accesibilidad para manejar GlobalProtect: la persona tiene que darlo una vez en" \
         "Ajustes del Sistema → Privacidad y seguridad → Accesibilidad, a la aplicación del terminal" >&2; exit 3 ;;
  pulsado) ;;
  *) echo "vpn: no se encuentra el botón de $QUIERO en GlobalProtect ($salida)" >&2; exit 4 ;;
esac

i=0
while [ $i -lt "$ESPERA" ]; do
  if [ -n "$DESCONECTAR" ]; then
    if ! conectada; then echo "vpn: desconectada (en ${i} s)"; exit 0; fi
  elif conectada; then
    echo "vpn: conectada ($HOST resuelve, en ${i} s)"; exit 0
  fi
  sleep 3; i=$((i + 3))
done
if [ -n "$DESCONECTAR" ]; then
  echo "vpn: pulsado «Desconectar», pero $HOST sigue resolviendo tras ${ESPERA} s" >&2; exit 5
fi
sin_dns
echo "vpn: pulsado «Conectar», pero no conecta en ${ESPERA} s: la sesión de GlobalProtect habrá caducado;" \
     "la persona tiene que iniciarla (con MFA) en su ventana" >&2
exit 5
