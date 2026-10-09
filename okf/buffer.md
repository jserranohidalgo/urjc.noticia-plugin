---
type: conector
title: Buffer — conector MCP
description: Cómo este plugin llega a LinkedIn, X, BlueSky e Instagram a través del servidor MCP remoto y oficial de Buffer, y qué puede y no puede hacer el agente con él.
---

# Buffer — conector MCP

Gestor centralizado de redes sociales. A diferencia de la web del CMS (que se opera por navegador — ver
[`navegador.md`](navegador.md)), Buffer publica un **servidor MCP remoto y oficial**: el propio servicio expone
un canal de agente de primera clase, sin necesidad de automatizar un navegador ni de una sesión dedicada.

Este plugin lo registra en [`.mcp.json`](../.mcp.json) apuntando a `https://mcp.buffer.com/mcp`.

## Autenticación

Dos vías, ninguna pasa por el SSO de la Universidad — es un proveedor de identidad propio de Buffer:

- **API key personal** — la vía que usa este plugin por defecto: se genera desde la propia cuenta de Buffer en
  *Settings → Integrations* y se configura como variable `buffer_api_key` (ver `userConfig` en
  [`.mcp.json`](../.mcp.json)) al instalar el plugin.
- **OAuth** (inicio de sesión de un clic, con la cuenta del cargo) — alternativa si se prefiere no guardar una
  clave; configúralo directamente en tu propio `.mcp.json` de usuario en lugar de la variable de este plugin.

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
simultáneos.
