"""Exporta la portada del WordPress local (tema Votum Labs) como sitio estático en ./docs.

Uso (con WAMP arrancado):
    python export.py
    python export.py --base http://localhost/wordpress/

Después: git add -A && git commit -m "Actualiza exportación" && git push
"""
import argparse
import re
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'
THEME_DIR = ROOT.parent / 'wp-content' / 'themes' / 'orbita'
THEME_PATH = 'wp-content/themes/orbita/'


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8')


def clean_html(html, base):
    theme_url = base + THEME_PATH

    # Quitar lo que solo tiene sentido con WordPress funcionando (API, XML-RPC, emojis, versión).
    html = re.sub(r'<link rel="https://api\.w\.org/"[^>]*>\s*', '', html)
    html = re.sub(r'<link rel="EditURI"[^>]*>\s*', '', html)
    html = re.sub(r'<link rel="(?:alternate|shortlink)"[^>]*>\s*', '', html)
    html = re.sub(r'<meta name="generator"[^>]*>\s*', '', html)
    html = re.sub(r'<style id="wp-emoji-styles-inline-css">.*?</style>\s*', '', html, flags=re.S)
    html = re.sub(r'<script\b[^>]*>(?:(?!</script>).)*?(?:wpemoji|wp-emoji)(?:(?!</script>).)*</script>\s*', '', html, flags=re.S | re.I)

    # Web de prueba: que los buscadores no la indexen.
    html = re.sub(r"<meta name=['\"]robots['\"][^>]*>", '<meta name="robots" content="noindex, nofollow">', html)
    if 'name="robots"' not in html:
        html = html.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n<meta name="robots" content="noindex, nofollow">', 1)

    # El buscador no existe en estático: se envía al buscador de votumlabs.com.
    html = re.sub(r'(<form[^>]*role="search"[^>]*action=")[^"]*(")', r'\1https://votumlabs.com/\2', html)

    # Rutas absolutas de localhost -> relativas.
    html = html.replace(theme_url, '')
    html = html.replace(base, './')

    leftovers = sorted(set(re.findall(r'localhost[^"\'\s<>)]*', html)))
    return html, leftovers


def copy_assets(html):
    used = set(re.findall(r'(?:src|href)=["\']((?:assets/[^"\'?]+)|style\.css)', html))
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    for rel in sorted(used):
        src = THEME_DIR / rel
        dst = DOCS / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://localhost/wordpress/')
    base = ap.parse_args().base.rstrip('/') + '/'

    html, leftovers = clean_html(fetch(base), base)
    used = copy_assets(html)
    (DOCS / 'index.html').write_text(html, encoding='utf-8')
    (DOCS / '.nojekyll').write_text('', encoding='utf-8')  # GitHub Pages: servir tal cual, sin Jekyll

    print(f'docs/index.html ({len(html)} bytes) + {len(used)} recursos')
    if leftovers:
        print('AVISO: quedan referencias a localhost:', *leftovers, sep='\n  ')
        sys.exit(1)


if __name__ == '__main__':
    main()
