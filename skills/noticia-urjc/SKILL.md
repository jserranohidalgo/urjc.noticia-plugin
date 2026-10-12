---
name: noticia-urjc
description: Redacta noticias para la web de una Escuela/Facultad de la URJC siguiendo exactamente el formulario "Editar ítem" del CMS (Joomla/K2) - título, texto intro (extracto breve), texto completo e imagen 1200x800 con su pie/créditos - y además los textos equivalentes para publicar la misma noticia en LinkedIn, X, BlueSky e Instagram. Usa este skill SIEMPRE que el usuario, en su rol de coordinador de una Escuela/Facultad, pida escribir, redactar, montar o preparar una noticia/artículo para la web del centro, mencione el formulario con campos Título/Texto intro/Texto completo/Imagen del ítem, o pida publicar/adaptar una noticia para redes sociales. Se invoca explícitamente con /noticia-urjc "tema de la noticia", o con /noticia-urjc <URL de la Escuela en urjc.es> para configurar una Escuela.
---

# Noticia URJC

Genera el contenido completo de una noticia para la web de una Escuela/Facultad de la URJC — los cuatro
campos que pide el formulario "Editar ítem" del CMS —, además de los textos para publicar la misma noticia en
LinkedIn, X, BlueSky e Instagram, y lo deja todo guardado como log en una carpeta local, listo para
copiar/pegar. El pegado real en el CMS y en las redes sociales lo hace el usuario a mano (o el agente deja el
borrador en Buffer — ver más abajo): este skill no publica nada directamente.

## Configuración de la Escuela

Todo lo que distingue a una Escuela de otra (siglas, kicker, nombre, slug y categoría del CMS, color de marca,
logotipo, hashtags, carpeta del log) está en un `escuela.json` **fuera del plugin**, en
`~/.config/noticia-urjc/<slug>/escuela.json`, junto con el logotipo de la Escuela (`logo.svg` y `logo.png`).
Así no se pierde al actualizar el plugin y puede haber una configuración por cada Escuela.

Antes de redactar nada, decide qué Escuela usar:

1. Si el usuario da la página de una Escuela (`https://www.urjc.es/<slug>` o solo el slug), usa esa. Si ya
   existe su configuración, reutilízala; genérala de nuevo solo si el usuario lo pide.
2. Si no la da, mira qué hay en `~/.config/noticia-urjc/*/escuela.json`: si hay una, úsala; si hay varias,
   pregunta cuál.
3. Si no hay ninguna, pide la URL de la página de la Escuela en urjc.es.

Para generar la configuración a partir de la página, ejecuta (Python 3, solo biblioteca estándar):

```bash
python3 "<ruta-al-skill>/scripts/configurar-escuela.py" "https://www.urjc.es/<slug>"
```

El script imprime el `escuela.json` generado y avisa (por stderr) de lo que no ha podido deducir. Saca:

- `siglas` y `kicker` del `<title>` de la página («ETSII - Universidad Rey Juan Carlos»).
- `nombreCompleto` del bloque de contacto de la portada.
- `logo` del logotipo de la cabecera (`/images/facultades/logos/logo-<slug>.svg`), convertido a PNG.
- `colorMarca` del SVG del logotipo: el color que no es el rojo URJC ni un neutro.
- `slugCMS` de la URL, y `categoriaCMS`/`etiquetaCMS` por convención («Actualidad <SIGLAS>» / «<SIGLAS>»).
- `hashtagsBase` de las siglas (`#<SIGLAS> #URJC`), y `carpetaLog` con un valor por defecto
  (`~/Documents/Noticias<SIGLAS>`).

Enséñale al usuario los valores y el logotipo antes de seguir, y corrige en el `escuela.json` lo que haga
falta. Fíjate sobre todo en `nombreCompleto` (la web a veces lo escribe distinto que el logotipo), en
`carpetaLog` (es personal) y en `categoriaCMS`/`etiquetaCMS` (confírmalas en el desplegable del CMS la primera
vez que rellenes el formulario). Si el script no puede ejecutarse (por ejemplo, Windows sin Python), sigue los
mismos pasos a mano: descarga la página y el logotipo, deduce los campos como se describe arriba y escribe el
`escuela.json` en la misma ruta (`%USERPROFILE%\.config\noticia-urjc\<slug>\` en Windows). Los campos
están descritos en [`config/escuela.ejemplo.json`](../../config/escuela.ejemplo.json).

Usa esos valores en todos los pasos siguientes; no asumas los de la ETSII del fichero de ejemplo.

## Base de conocimiento

Las restricciones de cada medio —campos del CMS, límites de caracteres, estructura, tono— están en
[`okf/`](../../okf/index.md), un bundle de referencia que no cambia entre Escuelas (lo que sí cambia está en el
`escuela.json` de la Escuela):

- [`okf/web-cms.md`](../../okf/web-cms.md) — el formulario de la web y cómo llegar a él.
- [`okf/redes-sociales.md`](../../okf/redes-sociales.md) — restricciones de LinkedIn, X, BlueSky e Instagram.
- [`okf/identidad-corporativa.md`](../../okf/identidad-corporativa.md) — colores, tipografía y logotipo.
- [`okf/buffer.md`](../../okf/buffer.md) y [`okf/navegador.md`](../../okf/navegador.md) — los dos conectores:
  Buffer por MCP para redes, navegador por CDP para la web.

Este `SKILL.md` aporta el **procedimiento**: cómo generar esos contenidos a partir de un texto y una imagen.
Léelos antes de escribir — no repitas aquí sus restricciones de memoria.

Por defecto, toda noticia para la web se acompaña de sus versiones para redes sociales — no hace falta que el
usuario lo pida explícitamente cada vez, es el flujo estándar. Si en algún caso el usuario solo quiere el
contenido para la web (sin redes), pregúntalo o hazlo si lo pide explícitamente.

## Rutas importantes

- Scripts de imagen (relativos a este archivo), en dos variantes equivalentes:
  - **Windows**: `scripts/resize-image.ps1` y `scripts/generate-banner.ps1` (PowerShell + System.Drawing de .NET).
  - **macOS/Linux**: `scripts/resize-image.py` y `scripts/generate-banner.py` (Python 3 + Pillow/NumPy).
- Antes de elegir cuál ejecutar, comprueba el sistema operativo (por ejemplo con `uname` en Bash, o mirando
  si estás operando sobre una ruta `C:\...` vs `/Users/...` o `/home/...`). En macOS/Linux no hay PowerShell
  instalado — usa siempre la variante `.py` con la herramienta Bash; en Windows usa la variante `.ps1` con
  la herramienta de PowerShell.
- Carpeta donde se guarda cada noticia generada (log): la de `carpetaLog` en el `escuela.json` de la Escuela.
  Si no está configurada, pregunta al usuario dónde quiere guardarlo y anótalo allí para no volver a preguntar.
- Estas rutas pueden contener espacios y acentos: referencia siempre las rutas completas entre comillas dobles,
  tanto en PowerShell como en Bash.

## Paso 1 — Reunir los hechos

Antes de redactar nada, identifica si tienes lo esencial de una noticia: **qué** ha pasado o va a pasar,
**quién** participa, **cuándo** y **dónde**, y si hay alguna **cita textual** o dato concreto (cifras de
participantes, nombre de la empresa/entidad colaboradora, etc.).

Si el usuario ya dio estos datos en su petición, úsalos tal cual. Si falta algo importante, pregúntalo antes
de escribir — no inventes datos factuales sobre la Escuela, sus eventos, cargos o colaboradores (fechas,
nombres, cifras). Es mejor una pregunta rápida que un dato incorrecto publicado en la web del centro. El tono
y la estructura de la noticia sí puedes resolverlos tú sin preguntar.

## Paso 2 — Redactar los tres textos

Escribe con tono institucional e informativo, propio de una noticia de escuela universitaria: claro, en
tercera persona, sin excesivo entusiasmo publicitario ni lenguaje coloquial — el tono concreto de la
Universidad lo fija el Libro de estilo referenciado en
[`okf/identidad-corporativa.md`](../../okf/identidad-corporativa.md).

Los tres campos (título, texto intro, texto completo) y sus restricciones — extensión, qué debe poder leerse
de forma autónoma, estructura de pirámide invertida, forma de pegado en el CMS — están especificados en
[`okf/web-cms.md`](../../okf/web-cms.md): léelo antes de escribir. Si hay una cita textual de algún
protagonista, resérvala como cierre o remate de un párrafo del texto completo.

## Paso 3 — Imagen (1200x800)

Antes de generarla, si el usuario no lo ha dicho ya, pregunta qué modo quiere usar en esta ocasión:

**MODO FOTO** (el usuario aporta una imagen ya existente):
Pide la ruta del archivo si no la ha dado. Ejecuta, según el sistema operativo:

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File "<ruta-al-skill>\scripts\resize-image.ps1" -InputPath "<ruta-foto-original>" -OutputPath "<carpeta-noticia>\imagen-1200x800.png"
```

```bash
# macOS/Linux (Bash)
python3 "<ruta-al-skill>/scripts/resize-image.py" --input "<ruta-foto-original>" --output "<carpeta-noticia>/imagen-1200x800.png"
```

El script recorta centrado (sin deformar) y redimensiona a 1200x800 exactos. Tras generarla, ábrela con la
herramienta Read (o `open` en macOS) para comprobar visualmente el encuadre antes de darla por buena — el
recorte centrado puede cortar cabezas o elementos importantes si la foto original no está bien compuesta.

**MODO DISEÑO** (no hay foto, se genera un banner con el título sobre fondo institucional):

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy Bypass -File "<ruta-al-skill>\scripts\generate-banner.ps1" -Title "<texto corto a mostrar>" -Kicker "<kicker de escuela.json>" -BrandColor "<colorMarca de escuela.json>" -LogoPath "<ruta-al-logo-de-la-escuela>" -OutputPath "<carpeta-noticia>\imagen-1200x800.png"
```

```bash
# macOS/Linux (Bash)
python3 "<ruta-al-skill>/scripts/generate-banner.py" --title "<texto corto a mostrar>" --kicker "<kicker de escuela.json>" --brand-color "<colorMarca de escuela.json>" --logo "<ruta-al-logo-de-la-escuela>" --output "<carpeta-noticia>/imagen-1200x800.png"
```

- `--title`/`-Title` no tiene por qué ser el título completo de la noticia si es muy largo: usa una versión
  corta que quepa bien (el script autoajusta el tamaño de letra y hace wrap, pero un texto muy largo queda
  pequeño). Cuatro o cinco palabras clave suelen funcionar mejor que la frase completa.
- `--kicker`/`-Kicker` y `--brand-color`/`-BrandColor` deben venir de `escuela.json` (`kicker` y
  `colorMarca`) — no los inventes ni dejes el valor de ejemplo de la ETSII si la Escuela configurada es otra.
- `--logo`/`-LogoPath` debe apuntar al logotipo en PNG de la Escuela (`logo` en `escuela.json`). Si no hay
  PNG (el script no encontró conversor de SVG), conviértelo antes o genera el banner sin logo y avísalo.
- El **modo diseño** dibuja las franjas gráficas rojo (marca URJC) / color de Escuela sobre fondo blanco, no
  un degradado: usa `assets/Inter-Bold.ttf` y `assets/Inter-Medium.ttf` (empaquetadas con el skill, sin
  instalación) para el titular y el texto de cabecera. Si esos ficheros faltaran, la variante Python cae en
  "Arial Bold" del sistema y la de PowerShell en "Segoe UI" — ver
  [`okf/identidad-corporativa.md`](../../okf/identidad-corporativa.md).

En ambos modos, redacta también el **texto de créditos/pie de foto** (una frase corta describiendo la imagen,
y si aplica, créditos del autor de la foto).

## Paso 4 — Textos para redes sociales

Cada noticia de la web se publica también en LinkedIn, X, BlueSky e Instagram. Redacta un texto específico
para cada red a partir de los mismos hechos del Paso 1 y del texto completo del Paso 2 — no copies literalmente
el texto intro en las cuatro redes: cada una tiene su propio tono, longitud y convenciones.

Las restricciones de cada red —límite de caracteres, estructura, tono, hashtags— están en
[`okf/redes-sociales.md`](../../okf/redes-sociales.md): léelas antes de escribir, incluida la verificación
obligatoria de caracteres para X y BlueSky.

Para Instagram, si el usuario quiere el encuadre exacto del feed (Instagram recorta la imagen 1200x800 a un
formato más cuadrado/vertical), ofrece generar una versión adicional (por ejemplo 1080x1350 o 1080x1080) con
los mismos scripts de imagen del Paso 3, pasando `--width`/`--height` (Python) o `-Width`/`-Height`
(PowerShell) distintos.

### Publicar el borrador en Buffer

Si el MCP de Buffer está configurado (ver [`okf/buffer.md`](../../okf/buffer.md)), puedes dejar cada texto como
**borrador** en la cola de Buffer, en el canal correspondiente, adjuntando la imagen si aplica. No lo programes
ni lo publiques — ese paso es de la persona. Si el MCP no está disponible, deja los cuatro textos en el log
(Paso 5) para que el usuario los copie y pegue a mano en Buffer o en cada red.

## Paso 5 — Guardar el log

Crea la carpeta de la noticia dentro de la carpeta base de noticias (`carpetaLog` de `escuela.json`),
con nombre `AAAA-MM-DD-slug-del-titulo` (fecha de hoy + versión en minúsculas del título, sin acentos ni
caracteres especiales, palabras separadas por guiones). Dentro de esa carpeta guarda:

- `noticia.md` — con esta estructura:

  ```markdown
  # <Título>

  ## Texto intro
  <texto breve 3-4 líneas>

  ## Texto completo
  <texto largo>

  ## Imagen
  Archivo: imagen-1200x800.png
  Créditos / pie de foto: <texto de créditos>
  ```

- El archivo de imagen final (`imagen-1200x800.png`, generado en el Paso 3).

- `redes-sociales.md` — con esta estructura:

  ```markdown
  # <Título> — Redes sociales

  ## LinkedIn
  <texto>

  ## X
  <texto>
  (caracteres: <n>/280)

  ## BlueSky
  <texto>
  (caracteres: <n>/300)

  ## Instagram
  <texto>
  ```

## Paso 6 — Resumen final para el usuario

Termina mostrando en el chat, de forma clara y lista para copiar/pegar:

1. Los cuatro campos del formulario del CMS, en este orden: **Título**, **Texto intro**, **Texto completo**, y
   la ruta del **archivo de imagen** junto con su **texto de créditos**.
2. Los cuatro textos para redes sociales, en este orden: **LinkedIn**, **X** (con recuento de caracteres sobre
   280), **BlueSky** (con recuento de caracteres sobre 300) e **Instagram**, indicando si quedaron como
   borrador en Buffer o solo en el log.

Indica también dónde ha quedado guardado el log completo (`noticia.md` y `redes-sociales.md`) por si quiere
consultarlo más tarde.

Si los textos de redes se generaron con un enlace provisional porque la noticia todavía no estaba publicada en
la web, termina con un recordatorio explícito: en cuanto la noticia esté publicada, hay que sustituir ese
enlace por la URL definitiva en los cuatro textos (y en Buffer, si quedaron allí como borrador), antes de
publicarlos.
