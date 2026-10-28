---
name: noticia-urjc
description: Redacta noticias para la web de una Escuela/Facultad de la URJC siguiendo exactamente el formulario "Editar ítem" del CMS (Joomla/K2) - título, texto intro (extracto breve), texto completo e imagen 1200x800 con su pie/créditos - y además los textos equivalentes para publicar la misma noticia en LinkedIn, X, BlueSky e Instagram. Usa este skill SIEMPRE que el usuario, en su rol de coordinador de una Escuela/Facultad, pida escribir, redactar, montar o preparar una noticia/artículo para la web del centro, mencione el formulario con campos Título/Texto intro/Texto completo/Imagen del ítem, o pida publicar/adaptar una noticia para redes sociales. Se puede invocar explícitamente con el tema de la noticia (p. ej. /noticia-urjc "tema" en Claude Code), o con la URL de una Escuela en urjc.es para configurarla.
---

# Noticia URJC

Genera el contenido completo de una noticia para la web de una Escuela/Facultad de la URJC — los cuatro
campos que pide el formulario "Editar ítem" del CMS —, además de los textos para publicar la misma noticia en
LinkedIn, X, BlueSky e Instagram, y lo deja todo guardado como log en una carpeta local, listo para
copiar/pegar. El pegado real en el CMS y en las redes sociales lo hace el usuario a mano (o el agente deja el
borrador en Buffer — ver más abajo): este skill no publica nada directamente.

El orden es fijo: **primero se publica la noticia en la web de la Escuela y después, con la URL de esa
noticia, se publica en redes**. Los posts de redes enlazan a la noticia de la web, así que no se redactan
hasta tener su URL definitiva.

## Configuración de la Escuela

Todo lo que distingue a una Escuela de otra (siglas, kicker, nombre, slug y categoría del CMS, color de marca,
logotipo, hashtags, carpeta del log) está en un `escuela.json` **fuera del skill**, en
`~/.config/noticia-urjc/<slug>/escuela.json`, junto con el logotipo de la Escuela (`logo.svg` y `logo.png`).
Así no se pierde al actualizar el skill y puede haber una configuración por cada Escuela.

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

## Comprobaciones previas

Nada más tener la Escuela, **antes de redactar**, comprueba todo lo que van a necesitar los pasos siguientes, para
que el usuario arregle lo que falte (conectar la VPN, iniciar sesión…) mientras tú redactas, y no a mitad de
camino:

```bash
bash "<ruta-al-skill>/scripts/comprobar.sh" todo "<ruta del escuela.json>"
```

Revisa la configuración, Python con Pillow, Node.js, el navegador Chromium, la VPN, la sesión en la intranet de
la web (`eris`), la sesión en OneDrive y el bloque `buffer`. Si falta la VPN, intenta conectarla sola
(`scripts/lib/vpn/conectar.sh`, macOS: pulsa «Connect» en GlobalProtect, que reconecta sin MFA con la sesión
guardada), y solo si no puede lo da como `FALTA`, con el motivo. Imprime una línea por comprobación (`OK`, `FALTA`,
`AVISO`). Si falta iniciar sesión, deja la ventana del navegador en la pantalla de login. Comprueba tú además
que tienes disponibles las herramientas del servidor MCP de Buffer.

Cuenta al usuario, de una vez, todos los `FALTA` y `AVISO` con lo que tiene que hacer, y sigue redactando
(Pasos 1-3) mientras lo arregla. Vuelve a ejecutarlo antes de rellenar el CMS (`comprobar.sh web`, o `video` si
hay vídeo) y antes de Buffer (`comprobar.sh redes`): la sesión de la intranet caduca y la VPN se desconecta.

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
usuario lo pida explícitamente cada vez, es el flujo estándar, en dos fases: web (Pasos 1-4) y, cuando la
noticia ya está publicada, redes (Pasos 5-6). Si en algún caso el usuario solo quiere el contenido para la web
(sin redes), pregúntalo o hazlo si lo pide explícitamente.

## Rutas importantes

- Scripts de imagen (relativos a este archivo), en dos variantes equivalentes:
  - **Windows**: `scripts/resize-image.ps1` y `scripts/generate-banner.ps1` (PowerShell + System.Drawing de .NET).
  - **macOS/Linux**: `scripts/resize-image.py` y `scripts/generate-banner.py` (Python 3 + Pillow).
- Antes de elegir cuál ejecutar, comprueba el sistema operativo (por ejemplo con `uname` en Bash, o mirando
  si estás operando sobre una ruta `C:\...` vs `/Users/...` o `/home/...`). En macOS/Linux no hay PowerShell
  instalado — usa siempre la variante `.py` desde una terminal (bash/zsh); en Windows usa la variante `.ps1`
  desde PowerShell.
- Las variantes `.py` necesitan Pillow, y el `python3` que va primero en el PATH puede no tenerlo (hay
  equipos con varios Python instalados). Antes de usarlas, busca un intérprete que lo tenga: prueba
  `<python> -c "import PIL"` con `python3`, `/usr/local/bin/python3` y `/opt/homebrew/bin/python3`, y usa el
  primero que funcione en todos los comandos de imagen. Si ninguno lo tiene, propón al usuario instalarlo
  (`python3 -m pip install --user pillow`) en vez de hacerlo por tu cuenta. `configurar-escuela.py` no lo
  necesita: solo usa la biblioteca estándar.
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

El script recorta centrado (sin deformar) y redimensiona a 1200x800 exactos. Tras generarla, mírala (o ábrela
con el visor del sistema, p. ej. `open` en macOS) para comprobar visualmente el encuadre antes de darla por buena — el
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

En ambos modos, redacta también el **pie de foto** (una frase corta describiendo la imagen) y los **créditos**
(autor o fuente de la foto, si aplica): en el CMS son dos campos distintos.

### Vídeo (opcional)

Si la noticia tiene un vídeo (p. ej. un reel que envía una organización), va en el **campo de vídeo del
artículo**, no dentro del texto: K2 lo muestra en su propio bloque, con su pie y sus créditos. Como el CMS no
admite subidas de más de 20 MB, el vídeo se aloja en el OneDrive **del usuario** y la web (y después Buffer)
usan su URL de descarga directa pública:

```bash
bash "<ruta-al-skill>/scripts/buffer/subir-onedrive.sh" "<ruta del vídeo>"
```

Imprime un JSON con la URL `descarga`. Anótala en la sección «Vídeo» de `noticia.md` (Paso 4), con un pie de
vídeo y sus créditos; el script del CMS la rellena y `preparar-buffer.py` la adjunta en las redes. El vídeo
depende de ese fichero: no se puede borrar ni quitarle el acceso público mientras la noticia siga en la web.

## Paso 4 — Guardar la noticia y publicarla en la web

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
  Pie de foto: <descripción breve de la imagen>
  Créditos: <autor o fuente de la imagen>

  ## Vídeo
  URL: <URL de descarga directa del vídeo>
  Pie de vídeo: <descripción breve del vídeo>
  Créditos: <autor o fuente del vídeo>

  ## Publicación en la web
  URL: <pendiente — se rellena cuando la noticia esté publicada>
  ```

  La sección «Vídeo» solo si hay vídeo (ver Paso 3).

- El archivo de imagen final (`imagen-1200x800.png`, generado en el Paso 3).

Muestra en el chat, listos para copiar/pegar, los cuatro campos del formulario del CMS en este orden:
**Título**, **Texto intro**, **Texto completo**, y la ruta del **archivo de imagen** junto con su **pie de
foto** y sus **créditos**, además de la categoría y la etiqueta (`categoriaCMS`, `etiquetaCMS`).

Después rellena el formulario del CMS con el script, que hace todo el recorrido sin que tengas que decidir nada
(ver [`okf/web-cms.md`](../../okf/web-cms.md) y [`okf/navegador.md`](../../okf/navegador.md)):

```bash
bash "<ruta-al-skill>/scripts/cms/rellenar-cms.sh" "<carpeta-noticia>" "<ruta del escuela.json>"
```

- Necesita la configuración personal del usuario, `~/.config/noticia-urjc/usuario.json` (no es de ninguna
  Escuela; ver [`usuario.ejemplo.json`](../../config/usuario.ejemplo.json)): su **cuenta de la URJC con permiso
  de editor de la web de la Escuela** (no tiene por qué ser la del cargo), un perfil de navegador para esa cuenta
  (`navegador.perfil`, p. ej. `~/chrome-<parte local de la cuenta>`), un puerto CDP fijo (`navegador.puerto`) y,
  opcionalmente, qué navegador de la familia Chromium usar (`navegador.aplicacion`: Chrome, Edge, Brave…; si no
  se indica, el primero instalado). Si no existe, pregunta al usuario con qué cuenta edita la web, propón perfil
  y puerto y guárdalo.
- El script abre la ventana de ese perfil si no está abierta, entra por `eris.urjc.es/<slugCMS>` hasta el
  formulario, lo rellena desde `noticia.md`, comprueba lo que ha quedado e imprime un resumen. Nunca pulsa
  Guardar ni Cerrar.
- Si no hay sesión, espera hasta 5 minutos a que el usuario inicie sesión en la ventana: díselo. No teclees
  credenciales.
- Solo si sale con error, interpreta el mensaje: 2 = falta la VPN de la Universidad y no se ha
  podido conectar sola (el mensaje dice por qué: el permiso de Accesibilidad del terminal, la sesión de
  GlobalProtect caducada, que pide MFA, o un DNS que no es el de la VPN); 3 = no se inició sesión a
  tiempo; 4 = la cuenta de ese perfil no tiene permisos de editor; 5 = la web no muestra lo esperado (mira la
  ventana); 6 = el formulario no quedó como se esperaba (categoría o etiqueta inexistente, o un campo vacío).
  Si el script no puede ejecutarse (sin Node.js, Windows), da los campos para que el usuario los pegue a mano.

Termina esta fase pidiendo al usuario que revise el formulario y pulse **Guardar** y después **Cerrar**: con
«Publicado: Sí» (el valor por defecto del CMS), Guardar publica la noticia y le da URL, pero no aparece en la
portada de la Escuela hasta que se cierra el formulario. Indica dónde ha quedado el log. No redactes todavía
los textos de redes.

## Paso 5 — Textos para redes sociales, con la URL de la noticia

Empieza cuando el usuario diga que ha guardado y cerrado la noticia (en esta conversación o en otra; si es en
otra, busca la carpeta de la noticia en `carpetaLog`: la más reciente cuya URL en `noticia.md` siga pendiente,
o la que corresponda al título). Los textos de redes salen de los mismos hechos que `noticia.md`.

1. Busca tú la URL, sin pedírsela al usuario:

   ```bash
   python3 "<ruta-al-skill>/scripts/cms/buscar-url-noticia.py" "<carpeta-noticia>" "<ruta del escuela.json>"
   ```

   El script busca la noticia por su título en la portada de la Escuela y en sus páginas de actualidad,
   comprueba que la página responde y que el título coincide, y anota la URL en «Publicación en la web» de
   `noticia.md`. Solo si no la encuentra (código de salida 1), pregunta al usuario: lo más habitual es que no
   haya pulsado **Cerrar** después de **Guardar**, o que la noticia no se guardara publicada.
2. Si el usuario te da la URL a mano, comprueba igualmente que responde y que el título coincide, y anótala en
   `noticia.md`.
3. Redacta un texto específico para cada red **en la que publica la Escuela** a partir de los hechos del
   Paso 1 y del texto completo del Paso 2, con el enlace a esa URL. Las redes de la Escuela son las que tienen
   canal en `buffer.canales` de su `escuela.json` (LinkedIn, X, BlueSky, Instagram); una red sin canal no se
   redacta. Solo si no hay bloque `buffer`, redacta las cuatro. No copies literalmente el texto intro en
   todas: cada una tiene su propio tono, longitud y convenciones.

Las restricciones de cada red —límite de caracteres, estructura, tono, hashtags, cómo cuenta cada una el
enlace— están en [`okf/redes-sociales.md`](../../okf/redes-sociales.md): léelas antes de escribir, incluida la
verificación obligatoria de caracteres para X y BlueSky, que se hace ya con la URL definitiva.

Para Instagram, si el usuario quiere el encuadre exacto del feed (Instagram recorta la imagen 1200x800 a un
formato más cuadrado/vertical), ofrece generar una versión adicional (por ejemplo 1080x1350 o 1080x1080) con
los mismos scripts de imagen del Paso 3, pasando `--width`/`--height` (Python) o `-Width`/`-Height`
(PowerShell) distintos.

Si el usuario pide expresamente publicar en redes antes que en la web (por ejemplo, por urgencia), es la
excepción: usa un enlace provisional a la fuente o al evento y, al final, recuérdale que hay que sustituirlo
por la URL de la noticia en los cuatro textos (y en Buffer, si quedaron allí como borrador) en cuanto se
publique.

### Dejar los borradores en Buffer

Con un procedimiento fijo, sin decidir nada por tu cuenta (detalles en [`okf/buffer.md`](../../okf/buffer.md)):

1. **Guarda antes `redes-sociales.md`** con la estructura del Paso 6: el plan sale de ese fichero.
2. **El vídeo, si lo hay, ya está subido** desde la fase web (Paso 3): `preparar-buffer.py` toma su URL de la
   sección «Vídeo» de `noticia.md`. Si el vídeo es solo para redes y no está en `noticia.md`, súbelo igual
   con `subir-onedrive.sh` y pasa su URL con `--video`.
3. **Genera el plan**:

   ```bash
   python3 "<ruta-al-skill>/scripts/buffer/preparar-buffer.py" "<carpeta-noticia>" "<ruta del escuela.json>" [--video "<descarga>"]
   ```

   Imprime (y guarda en `buffer-plan.json`) una entrada por red con los argumentos exactos de `create_post`, y
   las redes omitidas con su motivo.
4. **Llama a `create_post` una vez por cada entrada de `publicaciones`, con su `create_post` tal cual.** Todas
   llevan `saveToDraft: true`: quedan como **borrador**. No las programes ni las publiques — ese paso es de la
   persona. No añadas `mode` ni `dueAt`.
5. Anota en `redes-sociales.md` el id de cada borrador creado y, si lo hay, la URL del vídeo.

Solo interpreta algo si un paso falla:

- Falta el bloque `buffer` en `escuela.json`: llama a `get_account` y `list_channels` del MCP de Buffer, guarda
  `buffer.organizacion` y `buffer.canales` (`linkedin`, `twitter`, `instagram`, `bluesky`: el id de cada canal
  conectado) y repite el paso 3. Si hay varias organizaciones, pregunta cuál.
- Falta `usuario.json`: el mismo caso que en el Paso 4 (pregunta la cuenta del usuario y guárdala). El bloque
  `onedrive` es opcional: por defecto, `https://urjc-my.sharepoint.com` y la carpeta `noticia-urjc`.
- `subir-onedrive.sh` sale con 3 (sin sesión: pide al usuario que inicie sesión en la ventana), 4 (la
  organización no permite vínculos para cualquier persona), 5 (falló la subida) o 6 (la URL no devuelve el
  fichero): díselo al usuario con el mensaje del script.
- `preparar-buffer.py` dice que un texto se pasa del límite: acórtalo en `redes-sociales.md` y repítelo.
- `create_post` devuelve un error: enséñaselo al usuario; no reintentes con otros argumentos.

Si las herramientas de Buffer no están disponibles, deja los textos en el log para que el usuario los pegue a
mano, y dile que conecte en su agente el servidor MCP de Buffer (`https://mcp.buffer.com/mcp`), iniciando
sesión en Buffer con la cuenta de la Escuela (OAuth, sin clave) o con una clave de API — ver
[`okf/buffer.md`](../../okf/buffer.md) y, para los pasos concretos de cada agente, el README del repositorio. Usa
las herramientas de cualquier servidor de Buffer que esté conectado.

## Paso 6 — Guardar los textos de redes y resumen final

Guarda en la carpeta de la noticia `redes-sociales.md`, con esta estructura:

```markdown
# <Título> — Redes sociales

Enlace: <URL de la noticia en la web>

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

Termina mostrando en el chat, listos para copiar/pegar, los textos de las redes de la Escuela, en este orden:
**LinkedIn**, **X** (con recuento de caracteres sobre 280), **BlueSky** (con recuento sobre 300) e **Instagram**, indicando si
quedaron como borrador en Buffer o solo en el log, y dónde está el log completo.
