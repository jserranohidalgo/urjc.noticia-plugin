#!/usr/bin/env python3
"""
Recorta (centrado) y redimensiona una imagen a un tamano exacto, por defecto 1200x800.

Equivalente en Python/Pillow de resize-image.ps1, para usarse en macOS/Linux donde no hay
PowerShell disponible. Hace un crop centrado para no deformar la foto y luego escala al
tamano final con interpolacion de alta calidad (Lanczos).

Ejemplo:
    python3 resize-image.py --input "/ruta/evento.jpg" --output "/ruta/evento-1200x800.png"
"""
import argparse
import os

from PIL import Image


def main():
    parser = argparse.ArgumentParser(description="Recorta centrado y redimensiona una imagen.")
    parser.add_argument("--input", required=True, help="Ruta de la imagen original (jpg, png, etc).")
    parser.add_argument("--output", required=True, help="Ruta del archivo de salida (.png o .jpg/.jpeg).")
    parser.add_argument("--width", type=int, default=1200, help="Ancho final en pixeles. Por defecto 1200.")
    parser.add_argument("--height", type=int, default=800, help="Alto final en pixeles. Por defecto 800.")
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        raise SystemExit(f"No existe el archivo de entrada: {args.input}")

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    with Image.open(args.input) as img:
        img = img.convert("RGB")
        src_w, src_h = img.size
        target_ratio = args.width / args.height
        source_ratio = src_w / src_h

        if source_ratio > target_ratio:
            # La fuente es mas ancha de lo necesario -> recortar los lados
            crop_h = src_h
            crop_w = round(crop_h * target_ratio)
            x0 = round((src_w - crop_w) / 2)
            y0 = 0
        else:
            # La fuente es mas alta de lo necesario -> recortar arriba/abajo
            crop_w = src_w
            crop_h = round(crop_w / target_ratio)
            x0 = 0
            y0 = round((src_h - crop_h) / 2)

        cropped = img.crop((x0, y0, x0 + crop_w, y0 + crop_h))
        resized = cropped.resize((args.width, args.height), Image.LANCZOS)

        ext = os.path.splitext(args.output)[1].lower()
        fmt = "JPEG" if ext in (".jpg", ".jpeg") else "PNG"
        resized.save(args.output, fmt)

    print(f"OK: imagen guardada en {args.output} ({args.width}x{args.height})")


if __name__ == "__main__":
    main()
