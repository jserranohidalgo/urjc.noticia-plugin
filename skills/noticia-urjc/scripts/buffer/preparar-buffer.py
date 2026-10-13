#!/usr/bin/env python3
"""
Prepara el plan de subida a Buffer de una noticia: una entrada por red con los argumentos EXACTOS de la
herramienta create_post del MCP de Buffer (canal, texto, adjunto y metadatos), sacados de redes-sociales.md y
del bloque `buffer` de escuela.json. El agente solo tiene que llamar a create_post con cada entrada, sin cambiar
nada; todas quedan como borrador (saveToDraft), nunca programadas ni publicadas.

Reglas que aplica:
- Texto: el de la sección de cada red en redes-sociales.md, sin la línea «(caracteres: …)». Comprueba otra vez
  los límites de X (280, URL = 23) y BlueSky (300, URL con su longitud real).
- Vídeo (--video, o si no la URL de la sección «Vídeo» de noticia.md; URL de descarga directa pública, p. ej. la
  de subir-onedrive.sh): se adjunta en LinkedIn, X e
  Instagram (como reel, también en el feed); en BlueSky solo si pesa 100 MB o menos.
- Sin vídeo: LinkedIn, X y BlueSky van con el enlace de la noticia (tarjeta de vista previa); Instagram, que
  exige imagen o vídeo, lleva la imagen publicada de la noticia en la web (o --imagen), con el pie de foto como
  texto alternativo.
- Una red sin canal en `buffer.canales` se omite, con el motivo.

Uso:
    python3 preparar-buffer.py <carpeta-noticia> <escuela.json> [--video URL] [--imagen URL]

Imprime el plan en JSON y lo guarda en <carpeta-noticia>/buffer-plan.json. Sale con código 1 si falta algo
(configuración, secciones, un texto que se pasa del límite) y lo dice.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

REDES = [("LinkedIn", "linkedin"), ("X", "twitter"), ("BlueSky", "bluesky"), ("Instagram", "instagram")]
USER_AGENT = "Mozilla/5.0 (noticia-urjc; preparar-buffer)"
BLUESKY_VIDEO_MAX = 100 * 1024 * 1024


def fail(msg):
    print(f"ERROR {msg}", file=sys.stderr)
    sys.exit(1)


def seccion(md, titulo):
    m = re.search(rf"^## {re.escape(titulo)}\n(.*?)(?=^## |\Z)", md, re.S | re.M)
    return m.group(1).strip() if m else None


def len_x(t):
    t = re.sub(r"https?://\S+", "x" * 23, t)
    return sum(2 if ord(c) > 0x2000 else 1 for c in t if c != "️")


def len_bluesky(t):
    return sum(1 for c in t if unicodedata.category(c) != "Mn" and c != "️")


def head(url):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.headers.get("Content-Type", ""), int(r.headers.get("Content-Length") or 0)


def imagen_de_la_noticia(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        page = r.read().decode("utf-8", errors="replace")
    m = re.search(r'(/media/k2/items/cache/[0-9a-f]+_XL\.jpg)', page)
    return urllib.parse.urljoin(url, m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("carpeta")
    ap.add_argument("escuela")
    ap.add_argument("--video", help="URL de descarga directa pública del vídeo")
    ap.add_argument("--imagen", help="URL pública de la imagen para Instagram (por defecto, la de la noticia)")
    a = ap.parse_args()

    escuela = json.load(open(a.escuela, encoding="utf-8"))
    buf = escuela.get("buffer") or {}
    canales = buf.get("canales") or {}
    if not buf.get("organizacion") or not canales:
        fail(f"falta el bloque buffer (organizacion y canales) en {a.escuela}: rellénalo con get_account y list_channels")

    redes_md = open(os.path.join(a.carpeta, "redes-sociales.md"), encoding="utf-8").read()
    noticia_md = open(os.path.join(a.carpeta, "noticia.md"), encoding="utf-8").read()
    url_noticia = re.search(r"^URL:\s*(https?://\S+)", noticia_md, re.M)
    url_noticia = url_noticia.group(1) if url_noticia else None
    if not a.video:
        # El vídeo de la noticia, si lo hay (sección «Vídeo» de noticia.md, la misma URL que usa la web).
        m = re.search(r"^## Vídeo\n(?:.*\n)*?URL:\s*(https?://\S+)", noticia_md, re.M)
        a.video = m.group(1) if m else None
    pie = (re.search(r"^Pie de foto:\s*(.+)$", noticia_md, re.M) or re.search(r"^# (.+)$", noticia_md, re.M)).group(1).strip()

    video_bytes = None
    if a.video:
        tipo, video_bytes = head(a.video)
        if not tipo.startswith("video/"):
            fail(f"--video no devuelve un vídeo ({tipo}): {a.video}")
    imagen = a.imagen
    if not a.video and not imagen and url_noticia:
        imagen = imagen_de_la_noticia(url_noticia)

    plan = {"organizacion": buf["organizacion"], "publicaciones": [], "omitidas": []}
    for titulo, servicio in REDES:
        texto = seccion(redes_md, titulo)
        if texto is None:
            plan["omitidas"].append({"red": titulo, "motivo": "no hay sección en redes-sociales.md"})
            continue
        texto = re.sub(r"\n\(caracteres: [^)]*\)\s*$", "", texto).strip()
        if servicio == "twitter" and len_x(texto) > 280:
            fail(f"el texto de X tiene {len_x(texto)} caracteres (máximo 280)")
        if servicio == "bluesky" and len_bluesky(texto) > 300:
            fail(f"el texto de BlueSky tiene {len_bluesky(texto)} caracteres (máximo 300)")
        if not canales.get(servicio):
            plan["omitidas"].append({"red": titulo, "motivo": "sin canal conectado en Buffer"})
            continue

        args = {"channelId": canales[servicio], "schedulingType": "automatic", "saveToDraft": True, "text": texto}
        if a.video and (servicio != "bluesky" or video_bytes <= BLUESKY_VIDEO_MAX):
            args["assets"] = [{"video": {"url": a.video}}]
            if servicio == "instagram":
                args["metadata"] = {"instagram": {"type": "reel", "shouldShareToFeed": True}}
        elif servicio == "instagram":
            if not imagen:
                plan["omitidas"].append({"red": titulo, "motivo": "Instagram exige imagen o vídeo con URL pública y no hay ninguno"})
                continue
            args["assets"] = [{"image": {"url": imagen, "metadata": {"altText": pie}}}]
            args["metadata"] = {"instagram": {"type": "post", "shouldShareToFeed": True}}
        elif servicio == "bluesky" and url_noticia:
            args["metadata"] = {"bluesky": {"linkAttachment": {"url": url_noticia}}}
        plan["publicaciones"].append({"red": titulo, "servicio": servicio, "create_post": args})

    salida = os.path.join(a.carpeta, "buffer-plan.json")
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    print(f"\nGuardado en: {salida}", file=sys.stderr)


if __name__ == "__main__":
    main()
