# noticia-urjc (plugin de Claude Code)

Redacta noticias para la web de cualquier Escuela/Facultad de la URJC (CMS Joomla/K2) y sus versiones para
LinkedIn, X, BlueSky e Instagram, con generación de imagen institucional y publicación en Buffer vía MCP.

Las reglas y procedimientos que usa el skill están en [`okf/`](okf/index.md), un bundle con convención OKF
(frontmatter + `index.md` con punteros).

## Qué incluye

```
.claude-plugin/plugin.json   ← manifiesto del plugin
.claude-plugin/marketplace.json ← marketplace de un solo plugin (para instalarlo)
.mcp.json                    ← registra el MCP remoto de Buffer
config/
  escuela.ejemplo.json       ← ejemplo de los campos de configuración de una Escuela
skills/noticia-urjc/
  SKILL.md                   ← el procedimiento (invocable con /noticia-urjc)
  scripts/                   ← configuración desde la web y generación/recorte de imagen
  assets/                    ← tipografía Inter + logo de ejemplo
okf/
  index.md, identidad-corporativa.md, web-cms.md, redes-sociales.md,
  buffer.md, navegador.md    ← la base de conocimiento (común a cualquier Escuela)
```

## Instalar y configurar para tu Escuela

1. Instala el plugin desde GitHub:

       /plugin install noticia-urjc --marketplace jserranohidalgo/urjc.noticia-plugin

   O, si has clonado el repositorio, desde la carpeta local:

       claude plugin install noticia-urjc --marketplace /ruta/a/urjc.noticia-plugin

   (Si solo quieres el skill, sin el MCP de Buffer, enlaza `skills/noticia-urjc` en `.claude/skills/`.)
2. Configura tu Escuela dándole al skill su página en urjc.es:

       /noticia-urjc https://www.urjc.es/<tu-escuela>

   El skill saca de esa página las siglas, el nombre, el slug y la categoría del CMS, los hashtags, el
   logotipo y el color de marca (el del logotipo), te los enseña para que los confirmes y los guarda en
   `~/.config/noticia-urjc/<slug>/` (`escuela.json` y el logo). Esa carpeta está fuera del plugin, así que la
   configuración se mantiene al actualizarlo. Las siguientes veces la reutiliza sin preguntar; si configuras
   varias Escuelas, te pregunta cuál usar. Para convertir el logo a PNG hace falta `rsvg-convert`
   (`brew install librsvg`), ImageMagick o `inkscape`; en macOS, si no hay ninguno, usa Quick Look.
3. Revisa los valores que el skill no puede saber por la web: la carpeta donde guardar el log de cada noticia
   (`carpetaLog`) y, la primera vez que rellenes el formulario, la categoría y la etiqueta del CMS.
4. Configura el acceso a Buffer: el plugin declara la opción `buffer_api_key` (en `plugin.json`). Genera una
   clave personal en Buffer, *Settings → Integrations*, y guárdala con
   `/plugin configure noticia-urjc@noticia-urjc` (o al instalar, con `--config buffer_api_key=…`). Si prefieres
   OAuth, configura el MCP de Buffer aparte en tu `.mcp.json` de usuario en vez de usar esta opción (ver
   [`okf/buffer.md`](okf/buffer.md)).
5. Para rellenar el formulario del CMS hace falta además una sesión de navegador — ver
   [`okf/navegador.md`](okf/navegador.md) para montarla (perfil dedicado, puerto de depuración, servidor de
   automatización MCP tipo *attach*).

## Qué no hace

Ni el CMS ni Buffer publican nada por sí solos desde este plugin sin que la persona dé el paso final:

- En la web, el agente puede rellenar el formulario pero no pulsar "Publicar".
- En redes, el agente puede dejar un borrador en la cola de Buffer, pero no programarlo ni publicarlo.
