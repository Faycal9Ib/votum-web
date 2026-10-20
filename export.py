"""Exporta la portada del WordPress local (tema Votum Labs) como sitio estático en ./docs.

Uso (con WAMP arrancado):
    python export.py
    python export.py --base http://localhost/wordpress/

Sin WordPress (solo rehace las páginas en español e inglés a partir de docs/index.html):
    python export.py --paginas

Después: git add -A && git commit -m "Actualiza exportación" && git push
"""
import argparse
import html as htmllib
import re
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'
PAGES_SRC = ROOT / 'paginas'
THEME_DIR = ROOT.parent / 'wp-content' / 'themes' / 'orbita'
THEME_PATH = 'wp-content/themes/orbita/'
SITE_URL = 'https://faycal9ib.github.io/votum-web/'
# Recursos hechos a mano (no vienen de WordPress): se conservan al regenerar docs/. Admite carpetas.
HANDMADE = [
    'brand.css', 'sections.css', 'assets/js/sections.js', 'assets/img/og-votumlabs.jpg',
    'assets/fonts', 'assets/img/productos', 'assets/catalogo',
]

MENU = '''<ul id="ob-menu" class="ob-menu"><li class="menu-item"><a href="https://votumlabs.com/we-are-votum/" data-vt-decode="hover">We are Votum</a></li>
<li class="menu-item"><a href="b2b.html" data-vt-decode="hover">B2B</a></li>
<li class="menu-item"><a href="inversores.html" data-vt-decode="hover">Área inversores</a></li>
'''

# Páginas: archivo en español, archivo en inglés (None = solo español), si usan sections.css/js,
# y título y descripción por idioma. La portada en español sale de WordPress; el resto, de paginas/.
PAGES = {
    'index': {
        'es': 'index.html', 'en': 'index.html', 'sections': False,
        'meta': {
            'es': ('Votum Labs &#8211; Laboratorio biotecnológico',
                   'Laboratorio biotecnológico: soluciones dermofarmacéuticas con CBD, de la farmacia al consumidor.'),
            'en': ('Votum Labs &#8211; Biotechnology laboratory',
                   'Biotechnology laboratory: dermopharmaceutical CBD solutions, from the pharmacy to the consumer.'),
        },
    },
    'b2b': {
        'es': 'b2b.html', 'en': 'b2b.html', 'sections': True,
        'meta': {
            'es': ('B2B &#8211; Votum Labs',
                   'Líneas de producto y desarrollo dermofarmacéutico de Votum Labs para farmacias, distribuidores y profesionales.'),
            'en': ('B2B &#8211; Votum Labs',
                   'Votum Labs product lines and dermopharmaceutical development for pharmacies, distributors and professionals.'),
        },
    },
    'inversores': {
        'es': 'inversores.html', 'en': 'investors.html', 'sections': True,
        'meta': {
            'es': ('Área inversores &#8211; Votum Labs',
                   'Perfil corporativo, rondas de capital y portal del socio de Votum Labs.'),
            'en': ('Investors &#8211; Votum Labs',
                   'Company profile, funding rounds and shareholder portal of Votum Labs.'),
        },
    },
    '404': {
        'es': '404.html', 'en': None, 'sections': False,
        'meta': {'es': ('Página no encontrada &#8211; Votum Labs', 'La página que buscas no existe en la web de Votum Labs.')},
    },
}

# Cabecera, pie y panel de accesibilidad en inglés. Cada texto debe existir en la portada:
# si WordPress lo cambia, la exportación avisa en lugar de dejarlo a medias.
EN_SHELL = [
    ('<html lang="es">', '<html lang="en">'),
    ('>Saltar al contenido<', '>Skip to content<'),
    ('aria-label="Buscar"', 'aria-label="Search"'),
    ('>Buscar</label>', '>Search</label>'),
    ('aria-label="Mi cuenta"', 'aria-label="My account"'),
    ('aria-label="Tienda"', 'aria-label="Shop"'),
    ('aria-label="Menú"', 'aria-label="Menu"'),
    ('href="inversores.html"', 'href="investors.html"'),
    ('>Área inversores<', '>Investors<'),
    ('Somos B Corp: una de las 280 empresas reconocidas en España.', 'We are a B Corp: one of 280 certified companies in Spain.'),
    ('>Descúbrelo<', '>Find out more<'),
    ('aria-label="Pie de página"', 'aria-label="Footer"'),
    ('>Política de envíos, devoluciones y cancelación de pedidos<', '>Shipping, returns and cancellation policy<'),
    ('>Todas las noticias<', '>All news<'),
    ('>Somos B Corp<', '>We are a B Corp<'),
    ('>¿Qué es el CBD?<', '>What is CBD?<'),
    ('Lorquí, Murcia, España', 'Lorquí, Murcia, Spain'),
    ('>Síguenos<', '>Follow us<'),
    ('alt="Empresa B Corp certificada"', 'alt="Certified B Corporation"'),
    ('>Proyecto financiado por:<', '>Project funded by:<'),
    ('Todos los derechos reservados.', 'All rights reserved.'),
    ('>Política de privacidad<', '>Privacy policy<'),
    ('>Política de cookies<', '>Cookie policy<'),
    ('>Política de igualdad<', '>Equality policy<'),
    ('>Política de calidad<', '>Quality policy<'),
    ('>Aviso legal<', '>Legal notice<'),
    ('>Opciones de accesibilidad<', '>Accessibility options<'),
    ('>Accesibilidad<', '>Accessibility<'),
    ('aria-label="Tamaño del texto"', 'aria-label="Text size"'),
    ('<span>Tamaño del texto</span>', '<span>Text size</span>'),
    ('aria-label="Texto normal"', 'aria-label="Normal text"'),
    ('aria-label="Texto grande"', 'aria-label="Large text"'),
    ('aria-label="Texto muy grande"', 'aria-label="Extra large text"'),
    ('>Alto contraste<', '>High contrast<'),
    ('>Subrayar enlaces<', '>Underline links<'),
    ('>Fuente legible<', '>Readable font<'),
    ('>Detener animaciones<', '>Stop animations<'),
    ('>Restablecer<', '>Reset<'),
]


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
    return postprocess(html), leftovers


def postprocess(html):
    """Ajustes del sitio estático. Idempotente: se puede aplicar sobre un index.html ya procesado."""
    # Estilos de bloques de WordPress que el tema no usa, y la precarga de rutas /wordpress/.
    for style_id in ('wp-img-auto-sizes-contain-inline-css', 'wp-block-library-inline-css',
                     'classic-theme-styles-inline-css', 'global-styles-inline-css'):
        html = re.sub(rf'\s*<style id="{style_id}">.*?</style>', '', html, flags=re.S)
    html = re.sub(r'\s*<script type="speculationrules">.*?</script>', '', html, flags=re.S)

    # Menú superior y enlaces del pie hacia las páginas propias.
    start = html.index('<ul id="ob-menu" class="ob-menu">')
    end = html.index('</ul>', html.index('</li>', start))
    while html.count('<ul', start + 1, end) > html.count('</ul>', start, end):  # submenús anidados
        end = html.index('</ul>', end + 1)
    html = html[:start] + MENU + html[end:]
    html = html.replace('<a href="https://votumlabs.com/b2b/">B2B</a>', '<a href="b2b.html">B2B</a>')
    html = html.replace('<a href="https://votumlabs.com/investor-relations/">Investor Relations</a>',
                        '<a href="inversores.html">Área inversores</a>')

    # Tipografía de marca.
    if 'votum-brand-css' not in html:
        html = re.sub(r"(<link rel='stylesheet' id='orbita-css'[^>]*>)",
                      r"\1\n<link rel='stylesheet' id='votum-brand-css' href='brand.css?ver=1.0.0' media='all' />", html, count=1)
    return html


def page_url(slug, lang):
    name = PAGES[slug][lang]
    path = '' if name == 'index.html' else name
    return SITE_URL + ('en/' if lang == 'en' else '') + path


def page_head(head, slug, lang):
    """Título, descripción, idiomas alternativos y etiquetas para compartir de cada página."""
    page = PAGES[slug]
    title, desc = page['meta'][lang]
    plain = htmllib.unescape(title)
    alt = 'Votum Labs, biotechnology laboratory: science that goes from the pharmacy to the consumer' if lang == 'en' else \
        'Votum Labs, laboratorio biotecnológico: ciencia que llega de la farmacia al consumidor'
    lines = [f'<meta name="description" content="{desc}">']
    if page['en']:
        lines += [f'<link rel="alternate" hreflang="es" href="{page_url(slug, "es")}">',
                  f'<link rel="alternate" hreflang="en" href="{page_url(slug, "en")}">',
                  f'<link rel="alternate" hreflang="x-default" href="{page_url(slug, "es")}">']
    lines += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="Votum Labs">',
        f'<meta property="og:locale" content="{"en_GB" if lang == "en" else "es_ES"}">',
    ]
    if page['en']:
        lines.append(f'<meta property="og:locale:alternate" content="{"es_ES" if lang == "en" else "en_GB"}">')
    lines += [
        f'<meta property="og:title" content="{plain}">',
        f'<meta property="og:description" content="{desc}">',
        f'<meta property="og:url" content="{page_url(slug, lang)}">',
        f'<meta property="og:image" content="{SITE_URL}assets/img/og-votumlabs.jpg">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{alt}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    meta = '<!-- votum:meta -->\n\t' + '\n\t'.join(lines) + '\n\t<!-- /votum:meta -->'
    head = re.sub(r'\s*<!-- votum:meta -->.*?<!-- /votum:meta -->', '', head, flags=re.S)
    head = re.sub(r'<title>.*?</title>', lambda m: f'<title>{title}</title>\n\t{meta}', head, count=1, flags=re.S)
    if page['sections']:
        head = head.replace("href='brand.css?ver=1.0.0' media='all' />",
                            "href='brand.css?ver=1.0.0' media='all' />\n<link rel='stylesheet' id='votum-sections-css' href='sections.css?ver=1.0.0' media='all' />")
    return head


def lang_switcher(html, slug, lang):
    """Selector de idioma: el idioma actual marcado y el otro enlazado a la misma página."""
    page = PAGES[slug]
    es_item = '<span class="ob-lang__item is-current" aria-current="true" lang="es">Español</span>'
    en_item = '<span class="ob-lang__item is-current" aria-current="true" lang="en">English</span>'
    if lang == 'es' and page['en']:
        en_item = f'<a class="ob-lang__item" href="en/{"" if page["en"] == "index.html" else page["en"]}" lang="en" hreflang="en">English</a>'
    elif lang == 'es':
        en_item = '<a class="ob-lang__item" href="en/" lang="en" hreflang="en">English</a>'
    else:
        es_item = f'<a class="ob-lang__item" href="../{"" if page["es"] == "index.html" else page["es"]}" lang="es" hreflang="es">Español</a>'
    items = f'\n\t\t\t<li>{es_item}</li>\n\t\t\t<li>{en_item}</li>\n\t\t'
    html = re.sub(r'(<ul class="ob-lang__list" id="ob-lang-list" hidden>).*?(</ul>)', lambda m: m.group(1) + items + m.group(2), html, count=1, flags=re.S)
    if lang == 'en':
        html = html.replace('<span class="screen-reader-text">Idioma: Español</span>', '<span class="screen-reader-text">Language: English</span>')
        html = html.replace('<span class="ob-lang__code" aria-hidden="true">ES</span>', '<span class="ob-lang__code" aria-hidden="true">EN</span>')
    return html


def to_english(html):
    for es, en in EN_SHELL:
        if es not in html:
            raise SystemExit(f'Traducción: no se encuentra «{es}» en la portada. Actualiza EN_SHELL en export.py.')
        html = html.replace(es, en)
    # Las páginas en inglés viven en docs/en/: los recursos compartidos están un nivel más arriba.
    return re.sub(r'''((?:href|src)=["'])(assets/|style\.css|brand\.css|sections\.css)''', r'\1../\2', html)


def root_relative(html):
    """La 404 se sirve en cualquier ruta: sus enlaces relativos pasan a absolutos desde la raíz del sitio."""
    root = '/' + SITE_URL.split('/', 3)[3]
    return re.sub(r'''((?:href|src)=["'])(?![a-z][a-z0-9+.-]*:|/|#)''', rf'\g<1>{root}', html)


def build_pages():
    """Genera las páginas en español e inglés a partir de docs/index.html y de paginas/."""
    index = postprocess((DOCS / 'index.html').read_text(encoding='utf-8'))
    head, rest = index.split('</head>', 1)
    body_open = rest[:rest.index('<main')]
    main = rest[rest.index('<main'):rest.index('</main>') + len('</main>')]
    tail = rest[rest.index('</main>') + len('</main>'):]
    (DOCS / 'en').mkdir(exist_ok=True)
    built = []

    for slug, page in PAGES.items():
        for lang in ('es', 'en'):
            name = page[lang]
            if not name:
                continue
            h = page_head(head, slug, lang)
            b, t = body_open, tail
            if slug != 'index':
                b = b.replace('<body class="home blog wp-theme-orbita">', f'<body class="page page-{slug} wp-theme-orbita">')
                b = b.replace(f'<a href="{page["es"]}" data-vt-decode="hover">', f'<a href="{page["es"]}" data-vt-decode="hover" aria-current="page">')
            if page['sections']:
                t = t.replace('</body>', '<script defer id="votum-sections-js" src="assets/js/sections.js?ver=1.0.0"></script>\n</body>')
            if slug == 'index' and lang == 'es':
                content = main
            else:
                src = PAGES_SRC / ('en' if lang == 'en' else '') / name
                content = src.read_text(encoding='utf-8').rstrip('\n')
            out = lang_switcher(h + '</head>' + b + content + t, slug, lang)
            if lang == 'en':
                out = to_english(out)
            if slug == '404':
                out = root_relative(out)
            dest = DOCS / ('en' if lang == 'en' else '') / name
            dest.write_text(out, encoding='utf-8')
            built.append(str(dest.relative_to(DOCS)))
    print('docs/:', ', '.join(built))


def copy_assets(html):
    used = set(re.findall(r'(?:src|href)=["\']((?:assets/[^"\'?]+)|style\.css)', html))
    kept = {}
    for rel in HANDMADE:
        path = DOCS / rel
        files = [p for p in path.rglob('*') if p.is_file()] if path.is_dir() else [path] if path.exists() else []
        kept.update({p.relative_to(DOCS).as_posix(): p.read_bytes() for p in files})
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir()
    for rel, data in kept.items():
        (DOCS / rel).parent.mkdir(parents=True, exist_ok=True)
        (DOCS / rel).write_bytes(data)
    for rel in sorted(used):
        src = THEME_DIR / rel
        dst = DOCS / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://localhost/wordpress/')
    ap.add_argument('--paginas', action='store_true', help='solo rehacer las páginas desde docs/index.html (sin WordPress)')
    args = ap.parse_args()
    if args.paginas:
        build_pages()
        return
    base = args.base.rstrip('/') + '/'

    html, leftovers = clean_html(fetch(base), base)
    used = copy_assets(html)
    (DOCS / 'index.html').write_text(html, encoding='utf-8')
    (DOCS / '.nojekyll').write_text('', encoding='utf-8')  # GitHub Pages: servir tal cual, sin Jekyll
    build_pages()

    print(f'docs/index.html ({len(html)} bytes) + {len(used)} recursos')
    if leftovers:
        print('AVISO: quedan referencias a localhost:', *leftovers, sep='\n  ')
        sys.exit(1)


if __name__ == '__main__':
    main()
