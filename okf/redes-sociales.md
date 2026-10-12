---
type: referencia-editorial
title: Redes sociales — restricciones por red
description: Límite de caracteres, tono, estructura y hashtags de LinkedIn, X, BlueSky e Instagram para la publicación de noticias, y cómo se verifican antes de entregarlas.
---

# Redes sociales — restricciones por red

Cada noticia se adapta a cada red con su propio texto — no se copia literalmente el texto intro de la web en
las cuatro: cada una tiene su tono, longitud y convenciones. Los datos factuales (nombres, cifras, fechas,
cargos) deben ser exactamente los mismos que en el texto completo de la web — no se inventan ni se redondean
de forma distinta entre un texto y otro.

Reparte 2-6 emoticonos que refuercen el contenido (🎓 🚀 📢 🔬 🏆 🌍 según encaje con el tema); evita ponerlos en
cada línea o saturar el texto. Hashtags de la Escuela y la Universidad siempre presentes
(`hashtagsBase` de `escuela.json` (ver [`escuela.ejemplo.json`](../config/escuela.ejemplo.json)), p. ej. `#ETSII #URJC`), más 2-4 específicos
del tema según la red.

El enlace de cada post debe apuntar, siempre que sea posible, a la URL ya publicada de la noticia en la web de
la Escuela (no a una fuente externa). Si la noticia todavía no está publicada en el CMS, se usa un enlace
provisional (a la fuente/evento) y se deja constancia expresa de que hay que sustituirlo por la URL definitiva
en cuanto se publique — sin bloquear el resto del trabajo por esto.

Todas se publican (o programan) a través de **Buffer** — ver [`buffer.md`](buffer.md) para el conector y su
techo de autonomía.

## LinkedIn

- Sin límite estricto de caracteres que verificar (LinkedIn admite hasta 3000), pero solo se ven los primeros
  ~200-300 en el feed antes de "ver más": prioriza que se lea bien completo, no que quepa en la vista previa.
- Estructura en líneas cortas separadas (no un bloque compacto), con emoticonos a modo de viñetas para
  cifras/datos destacados; cierre con una idea de agradecimiento/impacto y 3-5 hashtags.
- Tono profesional-cercano.

## X (antes Twitter)

- **Límite estricto de 280 caracteres**, contando emoticonos, espacios, hashtags y enlace — a verificar por
  recuento real, no a ojo.
- Si incluye un enlace, resérvale unos 24 caracteres orientativos: X lo acorta automáticamente a longitud fija
  (`t.co`), sea cual sea la longitud real de la URL.
- Tono más cercano e idiomático que la web, con 2-6 emoticonos.

## BlueSky

- **Límite estricto de 300 caracteres**, contando emoticonos, espacios, hashtags y enlace — a verificar por
  recuento real, no a ojo.
- A diferencia de X, BlueSky **no acorta las URLs**: el enlace cuenta con su longitud real.
- Tono más cercano e idiomático que la web, con 2-6 emoticonos.
- Si el canal no está conectado a Buffer (puede pasar: el plan gratuito limita a 3 canales y a veces se
  prioriza otra red), este texto simplemente queda sin canal donde publicarse — igual se redacta, por si se
  reconecta más adelante.

## Instagram

- Sin límite práctico relevante (Instagram admite hasta 2200 caracteres); caption más narrativo que en el
  resto de redes, con los emoticonos repartidos de forma natural a lo largo del texto.
- Bloque final de **como mucho 5 hashtags** separados por espacios (además de los de la Escuela y la
  Universidad) **cuando se publica vía Buffer**: es un límite duro de esa vía, no una recomendación de estilo
  — pasar de 5 rechaza la publicación. Instagram en sí admite hasta 30 al publicar directamente desde la app;
  el límite de 5 es propio de Buffer.
- El feed prefiere el formato vertical 4:5 (p. ej. 1080×1350), no el 1200×800 horizontal de la web. Si la
  fuente original (p. ej. el cartel de una asociación) ya viene en un ratio cercano a 4:5, úsese esa imagen
  directamente en vez del recorte 1200×800 pensado para la web — recortar ese recorte a la fuerza pierde
  calidad y encuadre.
- **Exige un asset de imagen o vídeo**: no admite un post de solo texto (restricción del propio MCP de Buffer).

## Verificación obligatoria

Antes de entregar los textos, confirma con un recuento real de caracteres (no a ojo — por ejemplo con
`python3 -c "print(len('''<texto>'''))"` desde Bash) que los textos de X y BlueSky respetan los límites de 280
y 300.
