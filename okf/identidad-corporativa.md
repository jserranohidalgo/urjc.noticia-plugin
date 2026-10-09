---
type: referencia-editorial
title: Identidad corporativa de la URJC
description: Colores, tipografía y reglas de logotipo del Manual de identidad visual y el Libro de estilo de la Universidad Rey Juan Carlos, para cualquier material de promoción generado por este plugin.
---

# Identidad corporativa de la URJC

La referencia para cualquier material que este plugin produzca — noticias, banners, publicaciones en redes —
la fija el Rectorado en dos documentos públicos, en su [sala de prensa](https://www.urjc.es/sala-de-prensa):

- **[Manual de identidad corporativa](https://www.urjc.es/images/Comunicacion/Manual_URJC.pdf)** — el logotipo en sus variantes, la paleta de color, la tipografía y las normas de uso de la marca.
- **[Libro de estilo](https://www.urjc.es/images/Comunicacion/Libro_de_Estilo_URJC.pdf)** — el tono y las convenciones de redacción editorial de la Universidad.

## El logotipo, según de quién es

La distinción que importa no es «con logo o sin logo», es **de quién**:

- **El logotipo de la propia Escuela o de la Universidad se puede usar libremente** en el material que se produce: es la identidad de la propia institución, no la de un tercero. Cada Escuela/Facultad publica el suyo en su propia página (p. ej. `images/facultades/logos/logo-<escuela>.svg` en `urjc.es/<escuela>`).
- **El logotipo de una entidad externa —una empresa patrocinadora, una institución colaboradora— no se reproduce** sin su autorización expresa, aunque la noticia trate sobre ella: es su marca registrada, no material propio. Lo que sí puede tomarse de una entidad externa, sin permiso adicional, es su **paleta de color pública** (la que expone en su propia web) para dar un acento visual coherente con el tema, siempre que el resultado no se confunda con material producido por esa entidad.

## Lo que fija el Manual, en concreto

Para no releer el PDF cada vez, los valores que más se usan al generar una pieza:

- **Color de marca de la Universidad** (fijo, igual en todas las Escuelas): blanco `#FFFFFF`, negro `#000000` y rojo `#CB0017` (PANTONE 485 C) — los tres válidos en RGB/hexadecimal para entornos digitales.
- **Tipografía**: **Inter** (pesos Light/Regular/Medium/Bold, descargable en Google Fonts) para comunicaciones digitales e impresas; **Arial** como sustituta en documentos que se comparten o editan fuera de la Universidad, o donde no se pueda incluir una tipografía propia.
- **Cada Facultad y Escuela tiene su propia gama cromática**, además del rojo de marca — se toma del logotipo de cada centro (no hay una lista textual de todas las gamas en el Manual). Este valor es el `colorMarca` de [`config/escuela.json`](../config/escuela.json); el de ejemplo (ETSII) es el marrón/ocre `#8C6239` de su logotipo.
- **El recurso visual distintivo son las «franjas gráficas»**: bandas de color, no ilustraciones temáticas, las que jerarquizan la información y dan dinamismo a un layout. Es el principio a seguir en banners e infografías, en vez de motivos narrativos propios (una metáfora, un diagrama temático).

## Cómo se aplica

El tono de los textos sigue el Libro de estilo; el logotipo y el color, el Manual de identidad corporativa. Los
scripts de imagen del skill (`generate-banner.py`/`.ps1`) ya implementan las franjas rojo + color de Escuela, la
tipografía Inter empaquetada y la superposición del logo — ver [`SKILL.md`](../skills/noticia-etsii/SKILL.md).
