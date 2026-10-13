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
- **Imagen** — 1200×800 exactos, acompañada de su pie de foto y sus créditos.

Además, al rellenar el formulario:

- **Categoría** — la de `categoriaCMS` (p. ej. "Actualidad ETSII"), que cuelga de la de la Escuela en el
  desplegable.
- **Etiquetas** — la de `etiquetaCMS` (p. ej. "ETSII"): se selecciona en la lista y se pasa con «Añadir »».
- **Imagen** — en la pestaña «Imagen»: el fichero, el **pie de foto** y los **créditos** (dos campos distintos).

Detalles del formulario que conviene saber (comprobados en `eris.urjc.es/nuevo-articulo`, octubre de 2026):

- **«Publicado» viene marcado en «Sí»** y el inicio de publicación es el momento de abrir el formulario.
- Solo hay dos botones, **Guardar** y **Cerrar**. Con «Publicado: Sí», Guardar publica: el ítem tiene ya URL
  (`urjc.es/<actualidad>/<…>/<id>-<alias>`), pero **no aparece en la portada de la Escuela hasta que se pulsa
  Cerrar**. Hay que pulsar los dos, en ese orden.
- El texto intro y el texto completo son dos editores JCE separados (`introtext`, `fulltext`); la categoría y
  las etiquetas son desplegables envueltos por Chosen.

## Cómo se llega al formulario

Lo hace el script [`rellenar-cms.sh`](../skills/noticia-urjc/scripts/cms/rellenar-cms.sh), con la sesión de
navegador de [`navegador.md`](navegador.md). La ruta que funciona, y que sigue el script:

1. Con la **VPN** de la Universidad conectada (sin ella, `eris.urjc.es` ni siquiera resuelve), ir a
   `eris.urjc.es/<slugCMS>` y pulsar **Intranet**. Se abre una ventana emergente que pasa por el SSO y, con
   sesión iniciada, llega sola a `eris.urjc.es/intranet-inicio`. Si la cuenta no tiene permiso, el SSO responde
   «Permisos inadecuados para la aplicación solicitada: URJC Intranet».
2. Pulsar **«Panel administración editores facultades y escuelas»** → `eris.urjc.es/administracion-facultades`.
3. En «Nuevo artículo», pulsar **«Publicar»** (solo abre el formulario, no publica nada): se abre otra ventana
   emergente con `eris.urjc.es/nuevo-articulo`, el formulario «Editar ítem».
4. En **Ayuda → Manual de administración** (botón *Ver*) está el manual de usuario del formulario, con detalle.

Por `www.urjc.es` (Intranet → Panel) el panel también carga, pero **«Publicar» no llega a abrir el formulario**:
vuelve a mostrar el índice. Hay que ir por `eris.urjc.es`.

## Publicar es un paso de la persona

Un agente puede **rellenar y dejar listo** el formulario de artículo — título, categoría, etiquetas, contenido
e imagen —, pero **no pulsar Guardar ni Cerrar**: con «Publicado: Sí», Guardar publica, y ese clic le
corresponde a quien coordina la Escuela, con la ventana visible para revisarlo antes. Si la ventana del
formulario se cierra sin guardar, se pierde lo rellenado.

Una vez guardada y cerrada, la URL de la noticia se encuentra sin preguntar a nadie con
[`buscar-url-noticia.py`](../skills/noticia-urjc/scripts/cms/buscar-url-noticia.py), que la busca por título
en la portada de la Escuela y en sus páginas de actualidad.
