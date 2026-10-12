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
  escuela.ejemplo.json       ← plantilla de configuración por Escuela
skills/noticia-urjc/
  SKILL.md                   ← el procedimiento (invocable con /noticia-urjc)
  scripts/                   ← generación/recorte de imagen (Python y PowerShell)
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
2. Copia `config/escuela.ejemplo.json` a `config/escuela.json` (no se versiona — cada Escuela tiene el suyo) y
   rellena al menos:
   - `siglas`, `kicker`, `nombreCompleto`
   - `slugCMS`, `categoriaCMS`, `etiquetaCMS` (los de tu web Joomla/K2)
   - `colorMarca` (hex, la gama cromática de tu Escuela) y `logo` (ruta a tu logotipo)
   - `hashtagsBase` y `carpetaLog` (dónde guardar el log de cada noticia)
3. Sustituye `skills/noticia-urjc/assets/logo-ejemplo.png` por el logotipo de tu Escuela (mismo nombre
   de fichero, o cambia la ruta en `config/escuela.json`).
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
