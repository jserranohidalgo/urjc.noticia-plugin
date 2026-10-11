# noticia-urjc (plugin de Claude Code)

Redacta noticias para la web de cualquier Escuela/Facultad de la URJC (CMS Joomla/K2) y sus versiones para
LinkedIn, X, BlueSky e Instagram, con generación de imagen institucional y publicación en Buffer vía MCP.

Este plugin es **autocontenido**: no depende del modelo Speech de
[`etsii.profesion`](https://github.com/jserranohidalgo/etsii.profesion), de donde se extrajo originalmente
(skill `SkillNoticiaEtsii`, instanciado allí para la ETSII). Lo que allí eran actos de habla y recursos de un
metamodelo, aquí son documentos planos de restricciones y procedimientos, en [`okf/`](okf/index.md) — un bundle con
convención OKF (frontmatter + `index.md` con punteros), pero sin ninguna dependencia de Speech ni de ese otro
repositorio.

## Qué incluye

```
.claude-plugin/plugin.json   ← manifiesto del plugin
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

1. Clona este repositorio e instálalo como plugin de Claude Code (o enlázalo en `.claude/skills/` si solo
   quieres el skill, sin el MCP de Buffer).
2. Copia `config/escuela.ejemplo.json` a `config/escuela.json` (no se versiona — cada Escuela tiene el suyo) y
   rellena al menos:
   - `siglas`, `kicker`, `nombreCompleto`
   - `slugCMS`, `categoriaCMS`, `etiquetaCMS` (los de tu web Joomla/K2)
   - `colorMarca` (hex, la gama cromática de tu Escuela) y `logo` (ruta a tu logotipo)
   - `hashtagsBase` y `carpetaLog` (dónde guardar el log de cada noticia)
3. Sustituye `skills/noticia-urjc/assets/logo-ejemplo.png` por el logotipo de tu Escuela (mismo nombre
   de fichero, o cambia la ruta en `config/escuela.json`).
4. Configura el acceso a Buffer: al instalar el plugin, Claude Code pedirá la variable `buffer_api_key`
   (`.mcp.json`) — genera una clave personal en Buffer, *Settings → Integrations*. Si prefieres OAuth, configura
   el MCP de Buffer aparte en tu `.mcp.json` de usuario en vez de usar esta variable (ver
   [`okf/buffer.md`](okf/buffer.md)).
5. Para rellenar el formulario del CMS hace falta además una sesión de navegador — ver
   [`okf/navegador.md`](okf/navegador.md) para montarla (perfil dedicado, puerto de depuración, servidor de
   automatización MCP tipo *attach*).

## Qué no hace

Ni el CMS ni Buffer publican nada por sí solos desde este plugin sin que la persona dé el paso final:

- En la web, el agente puede rellenar el formulario pero no pulsar "Publicar".
- En redes, el agente puede dejar un borrador en la cola de Buffer, pero no programarlo ni publicarlo.

## Procedencia

El contenido de `okf/` se extrajo el 10/10/2026 del modelo Speech de `etsii.profesion`
(`SkillNoticiaEtsii`, `PublicarNoticiaWeb`, `PublicarNoticiaX/BlueSky/LinkedIn/Instagram`, `Buffer`,
`IdentidadCorporativa`, `WebEscuela`, `Chromium`), quitando el envoltorio de actos de habla y recursos del
metamodelo. El skill y el plugin se renombraron de `noticia-etsii` a `noticia-urjc` (2026-10-12): lo único
propio de una Escuela concreta —color de marca, logo, categoría del CMS, nombre de la Escuela— ya estaba
pensado como parámetro de `config/escuela.json` en el propio modelo (ver `IdentidadCorporativa`, "Cada
Facultad y Escuela tiene su propia gama cromática"); el nombre `noticia-etsii` no reflejaba eso y bastaba con
corregirlo, sin tocar el contenido. Lo que seguía siendo válido para cualquier Escuela de la URJC —el dominio
del CMS, el Manual de identidad corporativa, el Libro de estilo, el funcionamiento de Buffer— se mantiene como
está.
