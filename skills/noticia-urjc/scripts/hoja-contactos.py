#!/usr/bin/env python3
"""
Hoja de contactos: las fotos de una carpeta en miniatura, en una sola imagen, con su nombre debajo, para elegir
cuáles usar sin abrirlas una a una (las de un fotógrafo pesan 10-20 MB cada una).

    python3 hoja-contactos.py --carpeta "<carpeta con fotos>" --salida "<hoja.jpg>" [--columnas 4] [--lado 420]

Lee JPEG y PNG de la carpeta (no de sus subcarpetas), respeta la orientación EXIF y quita del nombre lo que
tengan todos en común, para que quede corto. Necesita Pillow.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageOps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carpeta", required=True)
    ap.add_argument("--salida", required=True)
    ap.add_argument("--columnas", type=int, default=4)
    ap.add_argument("--lado", type=int, default=420, help="lado máximo de cada miniatura, en píxeles")
    a = ap.parse_args()

    nombres = sorted(f for f in os.listdir(a.carpeta) if f.lower().endswith((".jpg", ".jpeg", ".png")))
    if not nombres:
        raise SystemExit(f"no hay fotos en {a.carpeta}")
    prefijo = os.path.commonprefix(nombres) if len(nombres) > 1 else ""

    lado, pie = a.lado, 24
    filas = (len(nombres) + a.columnas - 1) // a.columnas
    hoja = Image.new("RGB", (a.columnas * lado, filas * (lado + pie)), "white")
    d = ImageDraw.Draw(hoja)
    for i, f in enumerate(nombres):
        im = Image.open(os.path.join(a.carpeta, f))
        im.draft("RGB", (lado * 2, lado * 2))  # en JPEG, decodifica ya reducida: mucho más rápido
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((lado, lado))
        x, y = (i % a.columnas) * lado, (i // a.columnas) * (lado + pie)
        hoja.paste(im, (x + (lado - im.width) // 2, y + (lado - im.height) // 2))
        d.text((x + 5, y + lado + 5), f[len(prefijo):] or f, fill="black")
    hoja.save(a.salida, quality=80)
    print(f"{a.salida}: {len(nombres)} fotos")


if __name__ == "__main__":
    main()
