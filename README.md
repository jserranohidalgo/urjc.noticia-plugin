# noticia-urjc

Redacta noticias para la web de cualquier Escuela/Facultad de la URJC (CMS Joomla/K2) y sus versiones para
LinkedIn, X, BlueSky e Instagram, con generación de imagen institucional y publicación de borradores en Buffer
vía MCP.

Es un **skill para agentes**, no atado a ningún agente concreto:

- El procedimiento es un skill en formato *Agent Skills* ([`skills/noticia-urjc/SKILL.md`](skills/noticia-urjc/SKILL.md)).
- Las reglas de cada medio están en [`okf/`](okf/index.md), un bundle de markdown con convención OKF.
- Los scripts (Python, Node, bash) se ejecutan desde cualquier terminal.
- La configuración vive en `~/.config/noticia-urjc/`, fuera de cualquier agente.
- Buffer se usa por MCP, que es un protocolo estándar.
- La web se opera con cualquier navegador de la familia Chromium (Chrome, Edge, Brave…) por CDP.

Para **Claude Code** hay además un plugin listo para instalar, que registra solo el servidor de Buffer.

## Qué incluye

```
skills/noticia-urjc/
  SKILL.md                   ← el procedimiento (Agent Skills)
  scripts/                   ← configuración desde la web y generación/recorte de imagen
  scripts/cms/               ← relleno del formulario del CMS y búsqueda de la URL publicada
  scripts/buffer/            ← plan de borradores para Buffer y subida de vídeos a OneDrive
  scripts/lib/               ← funciones comunes (navegador Chromium por CDP, playwright-core)
  assets/                    ← tipografía Inter (licencia SIL OFL 1.1, ver assets/OFL.txt)
okf/
  index.md, identidad-corporativa.md, web-cms.md, redes-sociales.md,
  buffer.md, navegador.md    ← la base de conocimiento (común a cualquier Escuela)
config/
  escuela.ejemplo.json       ← ejemplo de los campos de configuración de una Escuela
  usuario.ejemplo.json       ← ejemplo de tu configuración personal (cuenta, navegador, OneDrive)
AGENTS.md                    ← punto de entrada para agentes que lean AGENTS.md en vez de skills

.claude-plugin/              ← adaptador para Claude Code: manifiesto y marketplace del plugin
.mcp.json                    ← adaptador para Claude Code: registra el MCP de Buffer (OAuth)
```

## Requisitos

- Python 3, para configurar la Escuela, buscar la URL y preparar Buffer. Los scripts de imagen necesitan además
  Pillow.
- Node.js y un navegador de la familia Chromium (Chrome, Edge, Brave, Chromium…), para el CMS y OneDrive.
- Para rellenar el CMS desde fuera del campus, la **VPN** de la Universidad.
- Un agente que pueda ejecutar comandos, ver imágenes y usar servidores MCP.

Los scripts del CMS y de OneDrive son bash: funcionan en macOS y Linux. En Windows, el skill da los campos para
pegarlos a mano.

## Instalar

### En Claude Code

```
/plugin install noticia-urjc --marketplace jserranohidalgo/urjc.noticia-plugin
```

O, si has clonado el repositorio: `claude plugin install noticia-urjc --marketplace /ruta/a/urjc.noticia-plugin`.

El plugin registra el servidor MCP de Buffer. Reinicia Claude Code y conéctalo con `/mcp` → **buffer** →
*Authenticate*. Se invoca con `/noticia-urjc`.

### En otros agentes

1. **El skill:** copia o enlaza `skills/noticia-urjc/` en el directorio de skills de tu agente, si admite el
   formato Agent Skills; consulta su documentación. Si tu agente no admite skills pero sí lee `AGENTS.md`,
   trabaja desde una copia de este repositorio: [`AGENTS.md`](AGENTS.md) lo remite al skill.
2. **Buffer:** registra en tu agente un servidor MCP HTTP con la URL `https://mcp.buffer.com/mcp`, sin
   credenciales (OAuth: el agente te pedirá iniciar sesión en Buffer) o con la cabecera
   `Authorization: Bearer <clave>` (ver más abajo).

### Conectar Buffer

Por defecto, por **OAuth**: inicias sesión en Buffer con la cuenta que gestiona las redes de tu Escuela y
apruebas el acceso, sin copiar ninguna clave.

**Alternativa con clave de API**, para agentes sin OAuth para MCP o si prefieres una clave con nombre y
caducidad:
1. Entra en Buffer con la cuenta de la Escuela y abre **https://publish.buffer.com/settings/api**
   (*Settings → API*).
2. Genera una clave nueva y cópiala: normalmente solo se muestra una vez.
3. Registra el servidor con esa clave. En Claude Code:

       claude mcp add --scope user --transport http buffer-api https://mcp.buffer.com/mcp \
         --header "Authorization: Bearer <tu-clave>"

Más detalle en [`okf/buffer.md`](okf/buffer.md).

## Configurar tu Escuela y tu cuenta

1. Dale al skill la página de tu Escuela en urjc.es, por ejemplo `/noticia-urjc https://www.urjc.es/<tu-escuela>`
   en Claude Code, o pidiéndoselo a tu agente.
   - El skill saca de esa página las siglas, el nombre, el slug y la categoría del CMS, los hashtags, el
     logotipo y el color de marca (el del logotipo).
   - Te los enseña para que los confirmes y los guarda en `~/.config/noticia-urjc/<slug>/` (`escuela.json` y el
     logo).
   - Las siguientes veces la reutiliza sin preguntar; si configuras varias Escuelas, te pregunta cuál usar.
   - Para convertir el logo a PNG hace falta `rsvg-convert` (`brew install librsvg`), ImageMagick o `inkscape`;
     en macOS, si no hay ninguno, usa Quick Look.
2. Revisa los valores que el skill no puede saber por la web: la carpeta donde guardar el log de cada noticia
   (`carpetaLog`) y, la primera vez que rellenes el formulario, la categoría y la etiqueta del CMS.
3. La primera vez que rellene el CMS, te preguntará con qué cuenta editas la web de tu Escuela. La guardará en
   tu configuración personal, `~/.config/noticia-urjc/usuario.json` (ver
   [`config/usuario.ejemplo.json`](config/usuario.ejemplo.json)), junto con el navegador, el perfil y el puerto
   que usa.
   - Con esa misma cuenta se suben a tu OneDrive los vídeos para Buffer.
   - Si esa cuenta no ha iniciado sesión nunca en ese perfil, te pedirá que lo hagas en la ventana.
   - El skill deja el formulario relleno: lo revisas y pulsas **Guardar** y después **Cerrar**. Sin Cerrar, la
     noticia no aparece en la portada de la Escuela.

   Ver [`okf/navegador.md`](okf/navegador.md) y [`okf/web-cms.md`](okf/web-cms.md).

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
