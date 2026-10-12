#!/usr/bin/env python3
"""
Genera una imagen de cabecera/banner 1200x800 cuando no hay foto disponible, siguiendo
el Manual de identidad visual de la URJC: fondo en positivo (claro), franjas graficas
de color como elemento de jerarquia -no una ilustracion tematica-, tipografia Inter
(Arial/DejaVu como sustituta si no esta disponible) y el logotipo de la Escuela.

Ver okf/identidad-corporativa.md de este plugin para el porque de estas reglas.

El color de marca de la URJC (rojo PANTONE 485C, #CB0017) es fijo. El segundo color de
banda es el propio de cada Escuela y se pasa con --brand-color (hex); por defecto usa
el marron/ocre de ejemplo de la ETSII (#8C6239) si no se indica otro.

Equivalente en Python/Pillow de generate-banner.ps1, para usarse en macOS/Linux donde
no hay PowerShell disponible.

Ejemplo:
    python3 generate-banner.py --title "La Escuela acoge la final del hackathon" \
        --kicker "ETSII - Universidad Rey Juan Carlos" --brand-color "#8C6239" \
        --logo "/ruta/logo-escuela.png" --output "/ruta/banner.png"
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit(
        "Falta Pillow en este Python ({}). Usa otro python3 que lo tenga (p. ej. /usr/local/bin/python3 o "
        "/opt/homebrew/bin/python3) o instálalo con: python3 -m pip install --user pillow".format(sys.executable)
    )

# Color de marca de la Universidad (fijo, Manual de identidad visual URJC)
COLOR_RED = (203, 0, 23)      # #CB0017, PANTONE 485 C
COLOR_INK = (20, 17, 15)      # #14110F
COLOR_PAPER = (255, 255, 255)

# Color de marca por defecto de la segunda franja, si no se pasa --brand-color:
# el marron/ocre de ejemplo de la ETSII, tomado de su logotipo.
DEFAULT_BRAND_COLOR = (140, 98, 57)  # #8C6239

# Tipografia Inter (estatica, pesos Regular/Medium/Bold del Manual), empaquetada junto
# al skill; si no esta disponible, se cae a Arial/DejaVu Sans Bold como sustituta.
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
INTER_BOLD_CANDIDATES = [os.path.join(ASSETS_DIR, "Inter-Bold.ttf")]
INTER_MEDIUM_CANDIDATES = [os.path.join(ASSETS_DIR, "Inter-Medium.ttf")]
FALLBACK_BOLD_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]


def parse_hex_color(value):
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise argparse.ArgumentTypeError(f"Color hex invalido: {value!r} (esperado RRGGBB)")
    try:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Color hex invalido: {value!r}") from exc


def find_font(candidates):
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def wrapped_lines(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = word if not current else f"{current} {word}"
        width = draw.textlength(test, font=font)
        if width > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines


def main():
    parser = argparse.ArgumentParser(description="Genera un banner institucional 1200x800.")
    parser.add_argument("--title", required=True, help="Texto principal del banner.")
    parser.add_argument("--output", required=True, help="Ruta del PNG de salida.")
    parser.add_argument("--kicker", default="Universidad Rey Juan Carlos",
                         help="Texto pequeno sobre el titulo (normalmente \"<SIGLAS ESCUELA> - Universidad Rey Juan Carlos\").")
    parser.add_argument("--brand-color", dest="brand_color", type=parse_hex_color, default=DEFAULT_BRAND_COLOR,
                         help="Color hex (RRGGBB o #RRGGBB) de la gama cromatica propia de la Escuela, "
                              "para la segunda franja. Por defecto el marron de ejemplo de la ETSII (#8C6239).")
    parser.add_argument("--width", type=int, default=1200)
    parser.add_argument("--height", type=int, default=800)
    parser.add_argument("--logo", default=None,
                         help="Ruta a un logo PNG opcional (por defecto assets/logo-ejemplo.png junto al skill, "
                              "que hay que sustituir por el de la Escuela real).")
    args = parser.parse_args()

    width, height = args.width, args.height

    out_dir = os.path.dirname(args.output)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    logo_path = args.logo
    if not logo_path:
        default_logo = os.path.join(ASSETS_DIR, "logo-ejemplo.png")
        if os.path.isfile(default_logo):
            logo_path = default_logo

    bg = Image.new("RGB", (width, height), COLOR_PAPER)
    draw = ImageDraw.Draw(bg)

    # Franjas graficas: el elemento distintivo de jerarquia del Manual, no una
    # ilustracion tematica. Roja (marca URJC) + color propio de la Escuela.
    red_band_h = max(6, round(height * 0.0175))
    brand_band_h = max(3, round(height * 0.0075))
    draw.rectangle([0, 0, width, red_band_h], fill=COLOR_RED)
    draw.rectangle([0, red_band_h, width, red_band_h + brand_band_h], fill=args.brand_color)
    bands_bottom = red_band_h + brand_band_h

    margin_x = round(width * 0.0533)
    max_text_width = width - 2 * margin_x

    bold_font_path = find_font(INTER_BOLD_CANDIDATES) or find_font(FALLBACK_BOLD_CANDIDATES)
    medium_font_path = find_font(INTER_MEDIUM_CANDIDATES) or bold_font_path
    if not bold_font_path:
        raise SystemExit(
            "No se ha encontrado ninguna fuente TrueType utilizable (Inter Bold / Arial Bold / DejaVu Sans Bold)."
        )

    # Logo opcional, esquina superior izquierda, debajo de las franjas
    logo_bottom = bands_bottom + round(height * 0.045) + round(height * 0.065)
    if logo_path and os.path.isfile(logo_path):
        with Image.open(logo_path) as logo:
            logo = logo.convert("RGBA")
            max_logo_height = round(height * 0.065)
            scale = max_logo_height / logo.height
            logo_w = round(logo.width * scale)
            logo_h = max_logo_height
            logo_resized = logo.resize((logo_w, logo_h), Image.LANCZOS)
            paste_y = bands_bottom + round(height * 0.045)
            bg.paste(logo_resized, (margin_x, paste_y), logo_resized)
            logo_bottom = paste_y + logo_h + round(height * 0.025)

    # Kicker (texto pequeno sobre el titulo), en rojo de marca
    kicker_font = ImageFont.truetype(medium_font_path, round(height * 0.02))
    kicker_y = max(logo_bottom, bands_bottom + round(height * 0.14))
    kicker_text = args.kicker.upper()
    draw.text((margin_x, kicker_y), kicker_text, font=kicker_font, fill=COLOR_RED)
    kicker_bbox = draw.textbbox((margin_x, kicker_y), kicker_text, font=kicker_font)
    kicker_height = kicker_bbox[3] - kicker_bbox[1]

    # Titulo: autoajuste de tamano de fuente hasta que quepa en el area segura, en negro
    title_top = kicker_y + kicker_height + round(height * 0.025)
    title_max_height = height - title_top - round(height * 0.08)

    chosen_font = None
    lines = None
    chosen_line_height = None
    for font_size in (round(height * 0.08), round(height * 0.0725), round(height * 0.065),
                      round(height * 0.0575), round(height * 0.05), round(height * 0.0425),
                      round(height * 0.0375), round(height * 0.0325)):
        font = ImageFont.truetype(bold_font_path, font_size)
        candidate_lines = wrapped_lines(draw, args.title, font, max_text_width)
        bbox = font.getbbox("Ag")
        line_height = (bbox[3] - bbox[1]) * 1.25
        total_height = line_height * len(candidate_lines)
        if total_height <= title_max_height or font_size == round(height * 0.0325):
            chosen_font = font
            lines = candidate_lines
            chosen_line_height = line_height
            break

    total_height = chosen_line_height * len(lines)
    start_y = title_top + max(0.0, (title_max_height - total_height) / 2.0)

    y = start_y
    for line in lines:
        draw.text((margin_x, y), line, font=chosen_font, fill=COLOR_INK)
        y += chosen_line_height

    bg.save(args.output, "PNG")

    print(
        f"OK: banner guardado en {args.output} ({width}x{height}, "
        f"fuente titulo {chosen_font.size}pt, {len(lines)} linea(s))"
    )


if __name__ == "__main__":
    main()
