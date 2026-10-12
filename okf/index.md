---
type: Index
title: Base de conocimiento del plugin noticia-urjc
description: Bundle OKF con las reglas y procedimientos que el skill noticia-urjc necesita para redactar y publicar noticias de una Escuela/Facultad de la URJC, documentadas como restricciones y procedimientos.
---

# Base de conocimiento

Este bundle documenta, de forma independiente, lo que el skill [`noticia-urjc`](../skills/noticia-urjc/SKILL.md)
necesita saber para hacer su trabajo. Las cosas se documentan como **restricciones de un medio** y
**procedimientos para operarlo**.

Lo que varía de una Escuela a otra de la URJC vive en el `escuela.json` de cada Escuela
(`~/.config/noticia-urjc/<slug>/`, generado a partir de su página web; campos en
[`escuela.ejemplo.json`](../config/escuela.ejemplo.json)), no aquí: estos documentos son el conocimiento común a
cualquier Escuela que use el mismo CMS y la misma cuenta de Buffer.

<!-- okf:concepts -->
- [`identidad-corporativa.md`](identidad-corporativa.md) — colores, tipografía y logotipo del Manual de identidad visual de la URJC, y la distinción logo propio/ajeno.
- [`web-cms.md`](web-cms.md) — el formulario "Editar ítem" del CMS Joomla/K2 y cómo llegar a él.
- [`redes-sociales.md`](redes-sociales.md) — límites de caracteres, tono y estructura de LinkedIn, X, BlueSky e Instagram.
- [`buffer.md`](buffer.md) — el conector MCP de Buffer, su techo de autonomía y cómo llegan los posts a cada red.
- [`navegador.md`](navegador.md) — cómo conseguir una sesión de navegador autenticada para operar el CMS (necesario solo para `web-cms.md`; Buffer no lo necesita, tiene MCP propio).
