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

## Montaje (una vez)

1. **Perfil dedicado**: un directorio de perfil propio para esta identidad (no el perfil habitual de la
   persona — los navegadores de esta familia bloquean la depuración remota en el perfil por defecto desde
   versiones recientes). No debe iniciar sesión en la cuenta del navegador (sincronización, autorrelleno): eso
   ampliaría el alcance del agente a cualquier sitio que ese perfil reconozca.
2. **Puerto de depuración fijo** para ese perfil, p. ej. `9222`.
3. **Arranque sin ventana** (headless) con una ventana virtual amplia — en headless por defecto el viewport es
   pequeño y la maquetación de una interfaz web corporativa puede no llegar a pintarse.
4. **Un servidor de automatización** (p. ej. `@playwright/mcp` u otro cliente MCP de automatización de
   navegador) apuntando al endpoint CDP de ese puerto ya abierto (modo *attach*, no *launch* — si lanzara su
   propio navegador, nacería con perfil vacío y sin sesión).

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
| No se pinta el formulario o el menú | ventana virtual pequeña en headless | relanzar con tamaño amplio |
| La página da menos de lo esperado, sin aviso | se entró por una URL interna en vez de por la puerta pública | entrar por la ruta de acceso del servicio |
| Formulario de login con la sesión "viva" | la sesión ha caducado, o el servicio fuerza reautenticación | pedir a la persona que inicie sesión con ventana |
| Las herramientas de navegador no responden | el puerto está caído | relanzar la sesión headless |

## Publicar sigue siendo un paso de la persona

El agente puede rellenar el formulario y dejarlo listo, pero el clic de publicar en la web de la Escuela le
corresponde a la persona, con la ventana visible — ver [`web-cms.md`](web-cms.md), "Publicar es un paso de la
persona". Por eso esta sesión conviene operarla con ventana visible en todos sus pasos, no solo al iniciar
sesión: no hay garantía de que un formulario a medias quede guardado, así que la persona necesita ver la
pantalla para confirmar.
