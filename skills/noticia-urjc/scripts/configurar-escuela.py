#!/usr/bin/env python3
"""
Genera la configuracion de una Escuela/Facultad de la URJC a partir de su pagina web
(p. ej. https://www.urjc.es/etsii): siglas, kicker, nombre completo, slug y categoria del
CMS, hashtags, logotipo y color de marca (el del logotipo que no es el rojo URJC).

Guarda el resultado en <dir>/<slug>/: escuela.json, logo.svg y logo.png (el PNG es el que
usa generate-banner.py; Pillow no lee SVG). Por defecto <dir> es ~/.config/noticia-urjc,
fuera del plugin, para que la configuracion sobreviva a las actualizaciones.

Solo usa la biblioteca estandar. Para convertir el logo a PNG busca, por este orden,
rsvg-convert, magick (ImageMagick), inkscape, el modulo cairosvg o qlmanage (macOS); si no
hay ninguno, deja solo el SVG y lo avisa.

Imprime el escuela.json generado y, en stderr, los avisos sobre lo que no se pudo deducir.

Ejemplo:
    python3 configurar-escuela.py https://www.urjc.es/etsii
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

BASE = "https://www.urjc.es"
USER_AGENT = "Mozilla/5.0 (noticia-urjc; configuracion de Escuela)"
URJC_REDS = [(0xCB, 0x00, 0x17), (0xC9, 0x07, 0x1D)]


def fetch(url, retries=3):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            # La web de la URJC responde 503 de forma intermitente: reintenta con espera.
            if e.code == 503 and attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def slug_from_url(url):
    path = urllib.parse.urlparse(url if "//" in url else BASE + "/" + url.lstrip("/")).path
    parts = [p for p in path.split("/") if p]
    if not parts:
        raise SystemExit(f"No se reconoce el slug de la Escuela en la URL: {url}")
    return parts[0].lower()


def hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def is_brand_candidate(rgb):
    """Descarta el rojo URJC y los neutros (negro, blanco, grises)."""
    if any(sum((a - b) ** 2 for a, b in zip(rgb, red)) < 40 ** 2 for red in URJC_REDS):
        return False
    return max(rgb) - min(rgb) > 30


def brand_color_from_svg(svg):
    counts = {}
    for h in re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", svg):
        rgb = hex_to_rgb(h)
        if is_brand_candidate(rgb):
            key = "#%02X%02X%02X" % rgb
            counts[key] = counts.get(key, 0) + 1
    if not counts:
        return None
    return max(counts, key=counts.get)


def svg_to_png(svg_path, png_path, height=400):
    if shutil.which("rsvg-convert"):
        cmd = ["rsvg-convert", "-h", str(height), "-o", png_path, svg_path]
    elif shutil.which("magick"):
        cmd = ["magick", "-background", "none", "-density", "300", svg_path, "-resize", f"x{height}", png_path]
    elif shutil.which("inkscape"):
        cmd = ["inkscape", svg_path, "--export-type=png", f"--export-height={height}", f"--export-filename={png_path}"]
    else:
        try:
            import cairosvg
            cairosvg.svg2png(url=svg_path, write_to=png_path, output_height=height)
            return True
        except ImportError:
            pass
        if shutil.which("qlmanage"):
            # Vista previa de Quick Look: fondo blanco, suficiente porque el banner es blanco.
            with tempfile.TemporaryDirectory() as tmp:
                subprocess.run(["qlmanage", "-t", "-s", "1000", "-o", tmp, svg_path],
                               capture_output=True, check=False)
                out = os.path.join(tmp, os.path.basename(svg_path) + ".png")
                if os.path.isfile(out):
                    shutil.move(out, png_path)
                    return True
        return False
    return subprocess.run(cmd, capture_output=True).returncode == 0 and os.path.isfile(png_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", help="Página de la Escuela en urjc.es (p. ej. https://www.urjc.es/etsii) o su slug")
    parser.add_argument("--dir", default=os.path.join(os.path.expanduser("~"), ".config", "noticia-urjc"),
                        help="Carpeta base de configuraciones (por defecto ~/.config/noticia-urjc)")
    args = parser.parse_args()

    slug = slug_from_url(args.url)
    page_url = f"{BASE}/{slug}"
    page = fetch(page_url).decode("utf-8", errors="replace")
    warnings = []

    title = clean(re.search(r"<title>(.*?)</title>", page, re.S).group(1))
    if "error" in title.lower() or " - " not in title:
        raise SystemExit(f"{page_url} no parece la página de una Escuela/Facultad (título: «{title}»).")
    siglas = title.split(" - ")[0].strip()

    m = re.search(r'fp-demo-info.*?<h2[^>]*class="g-title"[^>]*>(.*?)</h2>', page, re.S)
    nombre = clean(m.group(1)) if m else None
    if not nombre:
        m = re.search(r'<meta name="description" content="[^"]*?((?:Escuela|Facultad)[^".,]*?)(?: de la Universidad| \.|,|")',
                      page)
        nombre = clean(m.group(1)) if m else None
        warnings.append("nombreCompleto: no está en el bloque de contacto; tomado de la meta descripción, revísalo"
                        if nombre else "nombreCompleto: no se ha encontrado en la página")

    out_dir = os.path.join(args.dir, slug)
    os.makedirs(out_dir, exist_ok=True)

    color = None
    logo_png = None
    m = re.search(r'id="logo-facultad".*?<img[^>]*src="([^"]+)"', page, re.S) or \
        re.search(r'src="([^"]*/logos/[^"]+\.svg)"', page)
    if m:
        logo_url = urllib.parse.urljoin(page_url + "/", m.group(1))
        logo_bytes = fetch(logo_url)
        ext = os.path.splitext(urllib.parse.urlparse(logo_url).path)[1].lower() or ".svg"
        logo_src = os.path.join(out_dir, "logo" + ext)
        with open(logo_src, "wb") as f:
            f.write(logo_bytes)
        if ext == ".svg":
            color = brand_color_from_svg(logo_bytes.decode("utf-8", errors="replace"))
            png = os.path.join(out_dir, "logo.png")
            if svg_to_png(logo_src, png):
                logo_png = png
            else:
                warnings.append("logo: no hay conversor SVG→PNG (rsvg-convert, ImageMagick, inkscape o cairosvg); "
                                f"convierte {logo_src} a logo.png a mano")
        else:
            logo_png = logo_src
            warnings.append("colorMarca: el logo no es SVG, el color no se puede leer de él")
    else:
        warnings.append("logo: no se ha encontrado el logotipo en la página")
    if not color:
        warnings.append("colorMarca: no se ha podido deducir del logotipo; pídeselo al usuario")

    config = {
        "url": page_url,
        "nombreCompleto": nombre,
        "siglas": siglas,
        "kicker": title,
        "slugCMS": slug,
        "categoriaCMS": f"Actualidad {siglas}",
        "etiquetaCMS": siglas,
        "colorMarca": color,
        "logo": logo_png,
        "hashtagsBase": [f"#{re.sub(r'[^0-9A-Za-z]', '', siglas)}", "#URJC"],
        "carpetaLog": os.path.join(os.path.expanduser("~"), "Documents", f"Noticias{siglas}"),
    }
    warnings.append(f"categoriaCMS/etiquetaCMS: deducidas por convención («Actualidad {siglas}»); "
                    "confírmalas en el desplegable del CMS")
    warnings.append("carpetaLog: valor por defecto; confírmalo con el usuario")

    path = os.path.join(out_dir, "escuela.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(json.dumps(config, ensure_ascii=False, indent=2))
    print(f"\nGuardado en: {path}", file=sys.stderr)
    for w in warnings:
        print(f"AVISO {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
