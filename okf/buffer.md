---
type: conector
title: Buffer — conector MCP
description: Cómo este plugin llega a LinkedIn, X, BlueSky e Instagram a través del servidor MCP remoto y oficial de Buffer, y qué puede y no puede hacer el agente con él.
---

# Buffer — conector MCP

Gestor centralizado de redes sociales. A diferencia de la web del CMS (que se opera por navegador — ver
[`navegador.md`](navegador.md)), Buffer publica un **servidor MCP remoto y oficial**: el propio servicio expone
un canal de agente de primera clase, sin necesidad de automatizar un navegador ni de una sesión dedicada.

El servidor es `https://mcp.buffer.com/mcp` (HTTP). Cualquier agente compatible con MCP puede usarlo; cómo se
registra depende del agente (en Claude Code lo registra el propio plugin, en [`.mcp.json`](../.mcp.json); para
los demás, ver el README del repositorio).

## Autenticación

Dos vías, ninguna pasa por el SSO de la Universidad — es un proveedor de identidad propio de Buffer:

- **OAuth** — la vía por defecto: el servidor se registra sin credenciales y, la primera vez, el agente abre
  Buffer en el navegador para iniciar sesión con la cuenta de la Escuela y aprobar el acceso. El agente guarda
  el permiso; no hay que copiar nada. Si caduca, se repite el inicio de sesión. Es la vía que documenta Buffer
  (p. ej. en su [guía para Claude](https://developers.buffer.com/guides/integrations/claude.html)).
- **API key personal** — alternativa, para agentes sin OAuth para MCP o para quien prefiera una clave con nombre
  y caducidad. Se genera en **https://publish.buffer.com/settings/api** (*Settings → API*), copiándola en el
  momento porque normalmente solo se muestra una vez, y se registra el mismo servidor con la cabecera
  `Authorization: Bearer <clave>`. Si falla con un 401 («Invalid or expired token»), la clave está mal copiada
  o ha caducado.

Basta con una de las dos: el skill usa las herramientas del servidor de Buffer que esté conectado. Los comandos
concretos para registrarlo en cada agente están en el README del repositorio.

## Capacidades expuestas

Redactar y enviar posts, programarlos y elegir canal, gestionar la cola de publicaciones, capturar ideas y
consultar analíticas.

## Techo del agente

Un agente puede **crear el borrador** de un post en la cola de Buffer a través del MCP, pero **no programarlo
ni publicarlo**: todo lo que crea un agente por este MCP entra en la cola como **borrador o programado**, nunca
publicado de inmediato — pero a diferencia de un borrador (que exige una acción humana posterior para salir),
lo **programado** se publica solo en su hora sin más confirmación. La garantía de revisión humana que anuncia
Buffer solo es completa si el agente se limita a dejar **borradores**, nunca a programar ni publicar.

Este límite no es una cautela adoptada por analogía con otras plataformas: lo impone la propia mecánica de
Buffer (programar es indistinguible de publicar, porque no queda ningún paso humano pendiente).

## Qué canales hay

Los canales conectados (qué cuenta de X, LinkedIn, Instagram, etc.) son configuración de la propia cuenta de
Buffer, no de este plugin — se gestionan desde la interfaz web de Buffer. El plan gratuito limita a 3 canales
simultáneos. Sus id se guardan una vez en el bloque `buffer` del `escuela.json` de la Escuela (`organizacion` y
`canales`), para no tener que buscarlos en cada noticia.

## Adjuntos: imágenes y vídeos

El MCP de Buffer no sube ficheros: cada adjunto es una **URL pública de descarga directa** (no una ruta local, ni
una página para compartir, ni un enlace que caduque). Por eso:

- **Imagen**: la de la noticia ya publicada en la web (`/media/k2/items/cache/<hash>_XL.jpg`), que es pública.
- **Vídeo**: se sube al OneDrive **personal de quien usa el plugin** (la cuenta de su `usuario.json`) con
  [`subir-onedrive.sh`](../skills/noticia-urjc/scripts/buffer/subir-onedrive.sh), que crea un vínculo de solo
  lectura para cualquier persona y devuelve la URL `<sitio>/personal/<cuenta>/_layouts/15/download.aspx?share=<token>`.
  Esa forma descarga el fichero sin sesión ni cookies; el vínculo de compartir normal (`/:v:/g/…`) y su variante
  `?download=1` necesitan cookies y Buffer recibe un 403. El script sube por la API de SharePoint, por trozos de
  8 MB, a la carpeta `onedrive.carpeta` de «Mis archivos» (por defecto `noticia-urjc`). Una vez publicadas las redes, se puede quitar el acceso
  público: Buffer y las redes ya tienen su copia.

Restricciones por red al adjuntar (comprobadas en octubre de 2026):

- **Instagram** exige imagen o vídeo; con vídeo va como **reel** (`type: reel`, `shouldShareToFeed: true`).
- **BlueSky** limita los vídeos a 100 MB; si el vídeo pesa más, el post va solo con el enlace.
- **LinkedIn y X** aceptan el vídeo; sin vídeo, van solo con el enlace de la noticia (tarjeta de vista previa).
- Al editar un post (`edit_post`), Buffer lo valida entero: hay que volver a mandar el texto y los adjuntos.

Todo esto lo aplica [`preparar-buffer.py`](../skills/noticia-urjc/scripts/buffer/preparar-buffer.py), que
genera los argumentos exactos de `create_post` para cada red.
