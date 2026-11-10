#!/usr/bin/env python3
"""
Busca en la web pública de la Escuela la URL de una noticia ya guardada en el CMS, a partir del título de su
noticia.md, la comprueba (responde y el <title> coincide) y la anota en la sección «Publicación en la web» de
noticia.md.

Joomla/K2 publica cada ítem en .../<id>-<alias>, donde el alias es el título en minúsculas, sin acentos y con
guiones. Se busca un enlace con ese alias (o con el título como texto) en la portada de la Escuela
(urjc.es/<slugCMS>) y, si no está, en las páginas de actualidad enlazadas desde ella.

La web pública (www.urjc.es) sirve una caché y una noticia recién guardada puede tardar en aparecer en ella; si
no se encuentra allí, se busca en eris.urjc.es (el mismo sitio sin caché, accesible con la VPN) y se devuelve
igualmente la URL pública, que es la que se enlaza en las redes.

Solo usa la biblioteca estándar, y `curl` si Python no puede validar el certificado de un sitio: en macOS, el
Python de python.org o de Homebrew no usa el llavero del sistema, y la cadena de eris.urjc.es no se completa
(CERTIFICATE_VERIFY_FAILED); curl sí lo usa. Si un sitio no se puede leer, lo dice y por qué, en vez de
saltárselo en silencio. Imprime la URL; sale con código 1 si no la encuentra (en ese caso, pídesela
al usuario: puede que la noticia no se haya guardado, que no se haya cerrado el formulario o que aún no
aparezca en los listados).

Ejemplo:
    python3 buscar-url-noticia.py "<carpeta-noticia>" ~/.config/noticia-urjc/etsii/escuela.json
"""
import html
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

BASE = "https://www.urjc.es"
USER_AGENT = "Mozilla/5.0 (noticia-urjc; busqueda de URL de noticia)"


def fetch_curl(url):
    """Descarga con curl, que valida el certificado con el almacén del sistema."""
    if not shutil.which("curl"):
        raise OSError(f"no se puede validar el certificado de {urllib.parse.urlparse(url).netloc} con Python, "
                      "y no hay curl para intentarlo con los certificados del sistema")
    r = subprocess.run(["curl", "-sfL", "--max-time", "30", "-A", USER_AGENT, url], capture_output=True)
    if r.returncode != 0:
        raise OSError(f"curl no pudo leer {url} (código {r.returncode})")
    return r.stdout.decode("utf-8", errors="replace")


def fetch(url, retries=3):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            # La web de la URJC responde 503 de forma intermitente: reintenta con espera.
            if e.code == 503 and attempt < retries - 1:
                time.sleep(3 * (attempt + 1))
                continue
            raise
        except urllib.error.URLError as e:
            if isinstance(e.reason, ssl.SSLCertVerificationError):
                return fetch_curl(url)
            raise


def motivo(error):
    """Por qué no se ha podido leer un sitio, en una frase."""
    razon = getattr(error, "reason", error)
    if isinstance(razon, OSError) and getattr(razon, "errno", None) in (8, -2, -3):  # nombre que no resuelve
        return "el nombre no resuelve (¿falta la VPN de la Universidad?)"
    return str(razon)


def alias(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def clean(text):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text))).strip()


def links(page, base):
    for href, text in re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', page, re.S):
        yield urllib.parse.urljoin(base, html.unescape(href)), clean(text)


def find(page, base, title):
    a = alias(title)
    for url, text in links(page, base):
        path = urllib.parse.urlparse(url).path
        if re.search(r"/\d+-" + re.escape(a) + r"/?$", path) or text == title:
            return url
    return None


def buscar_en(base, slug, title):
    home_url = f"{base}/{slug}"
    home = fetch(home_url)
    url = find(home, home_url, title)
    if url:
        return url
    # Páginas de actualidad: la de noticias de la Escuela (/actualidad-<slug>/noticias-<slug>), que es donde
    # aparece antes una noticia nueva, y las de actualidad enlazadas desde la portada (p. ej. /actualidad-etsii).
    candidates = [f"{base}/actualidad-{slug}/noticias-{slug}"]
    for u, _ in links(home, home_url):
        p = urllib.parse.urlparse(u)
        if p.netloc.endswith("urjc.es") and re.fullmatch(r"/actualidad[^/]*(/noticias[^/]*)?", p.path.rstrip("/")):
            if u not in candidates:
                candidates.append(u)
    for c in candidates:
        try:
            page = fetch(c)
        except urllib.error.HTTPError:
            continue  # una página de actualidad que no existe en esta Escuela
        url = find(page, c, title)
        if url:
            return url
    return None


def main():
    if len(sys.argv) != 3:
        raise SystemExit("uso: buscar-url-noticia.py <carpeta-noticia> <escuela.json>")
    noticia_md = os.path.join(sys.argv[1], "noticia.md")
    md = open(noticia_md, encoding="utf-8").read()
    title = re.search(r"^# (.+)$", md, re.M).group(1).strip()
    slug = json.load(open(sys.argv[2], encoding="utf-8"))["slugCMS"]

    url = None
    fallos = []
    for base in (BASE, "https://eris.urjc.es"):
        try:
            url = buscar_en(base, slug, title)
        except OSError as e:
            fallos.append(f"{urllib.parse.urlparse(base).netloc}: {motivo(e)}")
            continue  # se prueba la siguiente, pero se dice por qué
        if url:
            url = url.replace("https://eris.urjc.es", BASE)
            break
    if not url:
        print(f"No se encuentra «{title}» en {BASE}/{slug} ni en eris.urjc.es/{slug}, ni en sus páginas de actualidad",
              file=sys.stderr)
        for f in fallos:
            print(f"  no se pudo leer {f}", file=sys.stderr)
        sys.exit(1)

    # La página pública puede no estar aún en la caché de www: si no responde con el título, se comprueba en eris.
    try:
        page_title = clean(re.search(r"<title>(.*?)</title>", fetch(url), re.S).group(1))
    except (OSError, AttributeError):
        page_title = ""
    if not page_title.startswith(title):
        page_title = clean(re.search(r"<title>(.*?)</title>", fetch(url.replace(BASE, "https://eris.urjc.es")), re.S).group(1))
    if not page_title.startswith(title):
        print(f"La URL encontrada no coincide: {url} («{page_title}»)", file=sys.stderr)
        sys.exit(1)

    new_md, n = re.subn(r"(## Publicación en la web\s*\nURL:).*", lambda m: f"{m.group(1)} {url}", md)
    if not n:
        new_md = md.rstrip() + f"\n\n## Publicación en la web\nURL: {url}\n"
    with open(noticia_md, "w", encoding="utf-8") as f:
        f.write(new_md)
    print(url)


if __name__ == "__main__":
    main()
