---
type: referencia-editorial
title: Web de la Escuela — CMS Joomla/K2
description: Restricciones del formulario "Editar ítem" del CMS de las webs de Escuela/Facultad de la URJC y el procedimiento para llegar a él y rellenarlo.
---

# Web de la Escuela — CMS Joomla/K2

Las webs de Escuela/Facultad de la URJC corren sobre un gestor de contenidos Joomla/K2, con soporte técnico
del Rectorado. Cada Escuela tiene su propia intranet de edición y su propio sitio público:

- Patrón de URL: intranet `https://eris.urjc.es/<slugCMS>` · sitio público `https://urjc.es/<slugCMS>`.
- `<slugCMS>` es el de `escuela.json` (ver [`escuela.ejemplo.json`](../config/escuela.ejemplo.json)) (`etsii` en el ejemplo).
- **Requiere VPN** de la Universidad si se accede desde fuera del campus.
- Recomendación: editar el HTML directamente, no el editor WYSIWYG de Joomla.

## El formulario "Editar ítem"

Cuatro campos, con estas restricciones:

- **Título** — concreto y específico (no genérico); orientativo hasta 90-100 caracteres, para que quepa en una línea de listado.
- **Texto intro** (extracto, 3-4 líneas) — autónomo: es lo que se ve en el listado de noticias antes de entrar al artículo. No es un corta-pega de la primera frase del texto completo, sino un resumen que sitúa qué/quién/cuándo/dónde.
- **Texto completo** — varios párrafos en pirámide invertida: primero lo esencial, después contexto/cifras/objetivo, cita textual como remate si la hay. Separado en párrafos `<p>...</p>` para pegar en la pestaña "Code" del editor.
- **Imagen** — 1200×800 exactos, acompañada de su texto de créditos/pie de foto.

Además, al rellenar el formulario:

- **Categoría** — buscar la de la Escuela (p. ej. "ETSII") y seleccionar la categoría de `categoriaCMS` (p. ej. "Actualidad ETSII").
- **Etiquetas** — seleccionar la de `etiquetaCMS` (p. ej. "ETSII").

## Cómo se llega al panel de administración

El punto de entrada visible no es directo: hay dos caminos, y el primero puede fallar a media operación sin
avisar.

1. Ir a la web pública de la Escuela (`urjc.es/<slugCMS>`) y pulsar **INTRANET**, arriba a la derecha. Con
   sesión activa, entra directo; si no, aparece el formulario de login del SSO de la Universidad — ver
   [`navegador.md`](navegador.md).
2. Debería aterrizar en `urjc.es/intranet-inicio`; si no, navegar allí a mano. Ahí aparece el enlace **«Panel
   administración editores facultades y escuelas»**.
3. Ese enlace **a veces lleva a una pantalla en blanco** en vez de al panel — comportamiento observado de la
   plataforma, no un fallo de la sesión. Cuando pasa, el rodeo que funciona es entrar **de nuevo por la otra
   puerta**: ir a `eris.urjc.es/<slugCMS>` (o `eris.urjc.es/`) y pulsar **INTRANET** ahí también,
   reautenticándose si lo pide. Eso sí lleva de forma fiable a `eris.urjc.es`, con el menú **«Nuevo artículo» /
   «Ayuda» / «Administración»**.
4. En **Ayuda → Manual de administración** (botón *Ver*) está el manual de usuario del formulario, con detalle.

## Publicar es un paso de la persona

Un agente puede **rellenar y dejar listo** el formulario de artículo — título, categoría, etiquetas, contenido
e imagen —, pero **no darle a publicar**: ese último clic le corresponde a quien coordina la Escuela, con la
ventana visible para confirmarlo en el momento (no está documentado si un artículo a medio rellenar queda
guardado en algún estado intermedio, así que conviene verlo en pantalla antes de cerrar).
