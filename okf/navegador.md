---
type: conector
title: Sesión de navegador para el CMS
description: Cómo un agente consigue y opera una sesión de navegador autenticada para rellenar el formulario del CMS de la web de Escuela, cuando no hay una API disponible.
---

# Sesión de navegador para el CMS

La web de Escuela (Joomla/K2, ver [`web-cms.md`](web-cms.md)) no ofrece una API: se opera como la opera una
persona, leyendo el árbol de la página y rellenando el formulario. Hace falta, por tanto, un navegador de la
familia **Chromium** (Chrome, Edge, Brave…; no sirven Safari ni Firefox) al que el agente se enganche por su
protocolo de depuración remota (CDP) — no uno que el agente lance por su cuenta, sino uno **ya abierto** por la
persona, para reutilizar su sesión ya iniciada.

## Qué identidad

La sesión es la **cuenta personal de quien usa el plugin**, la que tiene permiso de editor de la web de la
Escuela (no tiene por qué ser la del cargo: con una cuenta sin ese permiso, el SSO deja entrar pero la Intranet
responde «Permisos inadecuados»). Es la misma con la que se suben los vídeos a su OneDrive para Buffer. Como no
es de ninguna Escuela, no va en `escuela.json`, sino en `~/.config/noticia-urjc/usuario.json` (ver
[`usuario.ejemplo.json`](../config/usuario.ejemplo.json)):

```json
{
  "cuenta": "<cuenta>@urjc.es",
  "navegador": { "aplicacion": "Google Chrome", "perfil": "~/chrome-<cuenta>", "puerto": 9223 },
  "onedrive": { "sitio": "https://urjc-my.sharepoint.com", "carpeta": "noticia-urjc" }
}
```

El perfil se deriva de la cuenta (p. ej. `~/chrome-<parte local>`) y el puerto es cualquiera libre, fijo para
ese perfil. `aplicacion` es opcional: cualquier navegador de la familia Chromium (en macOS, el nombre de la
aplicación, p. ej. «Microsoft Edge» o «Brave Browser»; en Linux, el ejecutable, p. ej. `chromium`); si no se
indica, se usa el primero instalado (Chrome, Edge, Brave, Chromium, Vivaldi, Opera). Los scripts [`rellenar-cms.sh`](../skills/noticia-urjc/scripts/cms/rellenar-cms.sh) y
[`subir-onedrive.sh`](../skills/noticia-urjc/scripts/buffer/subir-onedrive.sh) usan estos valores:
reutiliza la ventana si el puerto ya responde y, si no, la abre **con ventana** con ese perfil y ese puerto, y
se engancha a ella por CDP con `playwright-core` (que instala la primera vez en `~/.cache/noticia-urjc/node`).
No hace falta registrar ningún servidor MCP de navegador.

## Montaje (una vez)

1. **Perfil dedicado**: un directorio de perfil propio para esta identidad (no el perfil habitual de la
   persona — los navegadores de esta familia bloquean la depuración remota en el perfil por defecto desde
   versiones recientes). No debe iniciar sesión en la cuenta del navegador (sincronización, autorrelleno): eso
   ampliaría el alcance del agente a cualquier sitio que ese perfil reconozca.
2. **Puerto de depuración fijo** para ese perfil, p. ej. `9222`.
3. **Con ventana** y tamaño amplio: la persona tiene que ver el formulario para revisarlo y pulsar Guardar y
   Cerrar (ver más abajo).
4. **Engancharse al navegador ya abierto** por el endpoint CDP de ese puerto (modo *attach*, no *launch* — un
   navegador lanzado por la herramienta nacería con perfil vacío y sin sesión). Es lo que hace el script.

## El primer inicio de sesión es de la persona

Igual que el resto de servicios de la Universidad, el CMS se autentica con el **SSO propio de la Universidad**
(no con el proveedor de correo, que es otro distinto): la primera vez hace falta que la persona abra ese
perfil **con ventana**, inicie sesión a mano (usuario/contraseña y, si aplica, segundo factor) y a partir de
ahí la sesión vive en el perfil — sobrevive a reinicios del navegador, incluso en headless. Si el agente se
encuentra un formulario de login, lo dice y para: no teclea credenciales.

**Entra siempre por la puerta del servicio**, no directamente a una URL interna del panel: ir derecho a una
ruta interna con la sesión viva puede devolver una vista anónima sin ningún aviso de que la sesión ha caducado
— hay que entrar por la ruta de acceso pública (ver [`web-cms.md`](web-cms.md), "Cómo se llega al panel de
administración"), que es la que dispara el ida y vuelta con el SSO y se resuelve sola si la sesión existe.

## Cuando no se ve lo que se espera

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `eris.urjc.es` no resuelve (`ERR_NAME_NOT_RESOLVED`) | falta la VPN de la Universidad | conectar la VPN |
| «Permisos inadecuados para la aplicación solicitada: URJC Intranet» | la cuenta del perfil no es editora de la web | usar el perfil de la cuenta editora (`usuario.json`) |
| No se pinta el formulario o el menú | ventana pequeña | relanzar con tamaño amplio |
| La página da menos de lo esperado, sin aviso | se entró por una URL interna en vez de por la puerta pública | entrar por la ruta de acceso del servicio |
| Formulario de login con la sesión "viva" | la sesión ha caducado, o el servicio fuerza reautenticación | pedir a la persona que inicie sesión con ventana |
| El script no conecta con el navegador | el puerto está caído | cerrar la ventana y relanzar el script |

## Publicar sigue siendo un paso de la persona

El agente puede rellenar el formulario y dejarlo listo, pero pulsar **Guardar** (que publica) y después
**Cerrar** le corresponde a la persona, con la ventana visible — ver [`web-cms.md`](web-cms.md), "Publicar es un
paso de la persona". Por eso esta sesión se opera con ventana visible en todos sus pasos, no solo al iniciar
sesión: si la ventana del formulario se cierra sin guardar, se pierde lo rellenado.
