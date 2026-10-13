#!/usr/bin/env python3
"""
Busca en la web pública de la Escuela la URL de una noticia ya guardada en el CMS, a partir del título de su
noticia.md, la comprueba (responde y el <title> coincide) y la anota en la sección «Publicación en la web» de
noticia.md.

Joomla/K2 publica cada ítem en .../<id>-<alias>, donde el alias es el título en minúsculas, sin acentos y con
guiones. Se busca un enlace con ese alias (o con el título como texto) en la portada de la Escuela
(urjc.es/<slugCMS>) y, si no está, en las páginas de actualidad enlazadas desde ella.

Solo usa la biblioteca estándar. Imprime la URL; sale con código 1 si no la encuentra (en ese caso, pídesela
al usuario: puede que la noticia no se haya guardado, que no se haya cerrado el formulario o que aún no
aparezca en los listados).

Ejemplo:
    python3 buscar-url-noticia.py "<carpeta-noticia>" ~/.config/noticia-urjc/etsii/escuela.json
"""
import html
import json
import os
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

BASE = "https://www.urjc.es"
USER_AGENT = "Mozilla/5.0 (noticia-urjc; busqueda de URL de noticia)"


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


def main():
    if len(sys.argv) != 3:
        raise SystemExit("uso: buscar-url-noticia.py <carpeta-noticia> <escuela.json>")
    noticia_md = os.path.join(sys.argv[1], "noticia.md")
    md = open(noticia_md, encoding="utf-8").read()
    title = re.search(r"^# (.+)$", md, re.M).group(1).strip()
    slug = json.load(open(sys.argv[2], encoding="utf-8"))["slugCMS"]

    home_url = f"{BASE}/{slug}"
    home = fetch(home_url)
    url = find(home, home_url, title)
    if not url:
        # Páginas de actualidad enlazadas desde la portada (p. ej. /actualidad-etsii).
        candidates = []
        for u, _ in links(home, home_url):
            p = urllib.parse.urlparse(u)
            if p.netloc.endswith("urjc.es") and re.fullmatch(r"/actualidad[^/]*", p.path.rstrip("/")):
                if u not in candidates:
                    candidates.append(u)
        for c in candidates:
            url = find(fetch(c), c, title)
            if url:
                break
    if not url:
        print(f"No se encuentra «{title}» en {home_url} ni en sus páginas de actualidad", file=sys.stderr)
        sys.exit(1)

    page_title = clean(re.search(r"<title>(.*?)</title>", fetch(url), re.S).group(1))
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
