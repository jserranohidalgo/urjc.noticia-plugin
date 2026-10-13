# noticia-urjc (plugin de Claude Code)

Redacta noticias para la web de cualquier Escuela/Facultad de la URJC (CMS Joomla/K2) y sus versiones para
LinkedIn, X, BlueSky e Instagram, con generación de imagen institucional y publicación en Buffer vía MCP.

Las reglas y procedimientos que usa el skill están en [`okf/`](okf/index.md), un bundle con convención OKF
(frontmatter + `index.md` con punteros).

## Qué incluye

```
.claude-plugin/plugin.json   ← manifiesto del plugin
.claude-plugin/marketplace.json ← marketplace de un solo plugin (para instalarlo)
.mcp.json                    ← registra el MCP remoto de Buffer (OAuth)
config/
  escuela.ejemplo.json       ← ejemplo de los campos de configuración de una Escuela
  usuario.ejemplo.json       ← ejemplo de tu configuración personal (cuenta, navegador, OneDrive)
skills/noticia-urjc/
  SKILL.md                   ← el procedimiento (invocable con /noticia-urjc)
  scripts/                   ← configuración desde la web y generación/recorte de imagen
  scripts/cms/               ← relleno del formulario del CMS y búsqueda de la URL publicada
  scripts/buffer/            ← plan de borradores para Buffer y subida de vídeos a OneDrive
  scripts/lib/               ← funciones comunes (Chrome por CDP, playwright-core)
  assets/                    ← tipografía Inter (licencia SIL OFL 1.1, ver assets/OFL.txt)
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
4. Conecta Buffer. El plugin registra el servidor MCP oficial de Buffer, que se conecta por **OAuth**: inicias
   sesión en Buffer y aceptas, sin copiar ninguna clave.
   1. Reinicia Claude Code después de instalar el plugin.
   2. Ejecuta `/mcp`, elige el servidor **buffer** del plugin y pulsa *Authenticate*.
   3. Se abre Buffer en el navegador: inicia sesión con la cuenta que gestiona las redes de tu Escuela y
      aprueba el acceso.

   **Alternativa con clave de API** (si prefieres no usar OAuth o necesitas una clave con nombre y caducidad):
   1. Entra en Buffer con la cuenta de la Escuela y abre **https://publish.buffer.com/settings/api**
      (*Settings → API*).
   2. Genera una clave nueva y cópiala: normalmente solo se muestra una vez.
   3. Registra un servidor con esa clave y reinicia Claude Code:

          claude mcp add --scope user --transport http buffer-api https://mcp.buffer.com/mcp \
            --header "Authorization: Bearer <tu-clave>"

   Más detalle en [`okf/buffer.md`](okf/buffer.md) y en la
   [guía de Buffer para Claude](https://developers.buffer.com/guides/integrations/claude.html).
5. Para que el skill rellene el formulario del CMS hacen falta la **VPN** de la Universidad, **Node.js** y
   **Google Chrome**. La primera vez te preguntará con qué cuenta editas la web de tu Escuela y guardará en tu
   configuración personal, `~/.config/noticia-urjc/usuario.json` (ver
   [`config/usuario.ejemplo.json`](config/usuario.ejemplo.json)), esa cuenta, el perfil de Chrome y el puerto que
   usa; con esa misma cuenta se suben a tu OneDrive los vídeos para Buffer. Si esa cuenta no ha iniciado sesión
   nunca en ese perfil, te pedirá que lo hagas en la ventana. El skill deja el formulario relleno: lo revisas y
   pulsas **Guardar** y después **Cerrar** (sin Cerrar, la noticia no aparece en la portada de la Escuela). Ver
   [`okf/navegador.md`](okf/navegador.md) y [`okf/web-cms.md`](okf/web-cms.md).

## Qué no hace

Ni el CMS ni Buffer publican nada por sí solos desde este plugin sin que la persona dé el paso final:

- En la web, el agente puede rellenar el formulario pero no pulsar "Guardar" ni "Cerrar".
- En redes, el agente puede dejar un borrador en la cola de Buffer, pero no programarlo ni publicarlo.

## Licencia

El código y la documentación de este repositorio se distribuyen con licencia [MIT](LICENSE).

La tipografía [Inter](https://github.com/rsms/inter) incluida en `skills/noticia-urjc/assets/` (`Inter-*.ttf`)
es de The Inter Project Authors y se redistribuye con su propia licencia, la
[SIL Open Font License 1.1](skills/noticia-urjc/assets/OFL.txt).

Los logotipos, nombres y colores de la Universidad Rey Juan Carlos y de sus Escuelas y Facultades son marcas de
la Universidad: no forman parte de este repositorio ni de su licencia. El plugin los descarga de la web pública
de cada Escuela al configurarla.
