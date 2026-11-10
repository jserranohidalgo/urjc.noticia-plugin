#!/usr/bin/env python3
"""
Collage: varias fotos en una sola imagen, en una rejilla de teselas, con logotipos superpuestos si hace falta.
Sirve para la imagen de la web (1200x800) y para la de Instagram (1080x1350, el 4:5 que prefiere el feed), que se
montan las dos desde las fotos originales: recortar la de la web para Instagram pierde calidad y encuadre.

    python3 collage.py --spec "<collage.json>" --salida "<imagen.png|.jpg>"

El JSON describe el lienzo, las teselas y los logotipos:

    {
      "tamaño": [1200, 800],
      "separación": 6,
      "teselas": [
        {"foto": "/ruta/foto1.jpg", "caja": [0, 0, 300, 400], "cx": 0.47, "y": [0.0, 0.92]},
        ...
      ],
      "logos": [
        {"logo": "/ruta/logo.png", "x": 813, "y": 413, "ancho": 190}
      ]
    }

- `caja` es [x, y, ancho, alto] de la tesela en el lienzo; la separación (blanca) se reparte por dentro.
- El recorte de cada foto se elige con `y` (la franja vertical que se conserva, en fracciones del alto: [0, 1] es
  entera) y `cx` (el centro horizontal, en fracción del ancho). El ancho del recorte sale de la proporción de la
  tesela, así que la foto no se deforma; si no cabe, se desplaza hasta el borde. Para elegir `cx` e `y`, mira la
  foto con una rejilla de décimas: que se vean las caras enteras y, si la hay, la pantalla con el nombre.
- Cada logotipo va sobre un recuadro blanco redondeado (un PNG con transparencia se lee igual sobre una foto
  oscura), con `ancho` en píxeles y la altura proporcional. Úsalo cuando la foto no enseña el logo de quien
  tiene que salir, y nunca para poner el de quien no quiere que se proyecte.

Respeta la orientación EXIF y decodifica las fotos a tamaño reducido. Necesita Pillow.
"""
import argparse
import json

from PIL import Image, ImageDraw, ImageOps


def tesela(t, sep):
    im = Image.open(t["foto"])
    x, y, w, h = t["caja"]
    w2, h2 = w - sep, h - sep
    im.draft("RGB", (w2 * 3, h2 * 3))
    im = ImageOps.exif_transpose(im).convert("RGB")
    iw, ih = im.size
    y0, y1 = t.get("y", [0.0, 1.0])
    alto = (y1 - y0) * ih
    ancho = alto * w2 / h2
    if ancho > iw:  # la franja pedida es más ancha que la foto: se recorta en alto
        ancho = iw
        alto = ancho * h2 / w2
    izq = max(0, min(iw - ancho, t.get("cx", 0.5) * iw - ancho / 2))
    arriba = max(0, min(ih - alto, y0 * ih))
    recorte = im.crop((int(izq), int(arriba), int(izq + ancho), int(arriba + alto)))
    return recorte.resize((w2, h2), Image.LANCZOS), (x + sep // 2, y + sep // 2)


def logo(lienzo, l):
    lg = Image.open(l["logo"]).convert("RGBA")
    ancho = l["ancho"]
    alto = round(lg.height * ancho / lg.width)
    lg = lg.resize((ancho, alto), Image.LANCZOS)
    margen = l.get("margen", 8)
    panel = Image.new("RGBA", (ancho + 2 * margen, alto + 2 * margen), (0, 0, 0, 0))
    ImageDraw.Draw(panel).rounded_rectangle([0, 0, panel.width - 1, panel.height - 1], radius=6,
                                            fill=(255, 255, 255, 240))
    panel.alpha_composite(lg, (margen, margen))
    lienzo.alpha_composite(panel, (l["x"], l["y"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--salida", required=True)
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))

    w, h = spec["tamaño"]
    sep = spec.get("separación", 6)
    lienzo = Image.new("RGBA", (w, h), "white")
    for t in spec["teselas"]:
        im, pos = tesela(t, sep)
        lienzo.paste(im, pos)
    for l in spec.get("logos", []):
        logo(lienzo, l)

    final = lienzo.convert("RGB")
    if a.salida.lower().endswith((".jpg", ".jpeg")):
        final.save(a.salida, quality=93, subsampling=0)
    else:
        final.save(a.salida)
    print(f"{a.salida}: {w}x{h}, {len(spec['teselas'])} fotos, {len(spec.get('logos', []))} logotipos")


if __name__ == "__main__":
    main()
