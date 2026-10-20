# Votum Labs — web de prueba

Versión estática de la portada del tema WordPress de Votum Labs, para revisión interna.
No es la web oficial: los enlaces del menú y de productos apuntan a [votumlabs.com](https://votumlabs.com).

- `docs/` — sitio publicado con GitHub Pages (HTML, CSS, JS e imágenes; sin WordPress ni base de datos).
- `export.py` — regenera `docs/` desde el WordPress local.
- `paginas/` — contenido (`<main>`) de **B2B**, **Área inversores** y la **404**. `export.py` las monta con la cabecera y el pie de la portada.
- `docs/brand.css`, `docs/sections.css`, `docs/assets/js/sections.js`, `docs/assets/fonts/`, `docs/assets/img/og-votumlabs.jpg` — recursos hechos a mano; `export.py` los conserva al regenerar.

Para rehacer las páginas sin WordPress (por ejemplo, tras editar algo en `paginas/`):

```bash
python export.py --paginas
```

## Qué añade export.py a lo que sale de WordPress

- **Menú:** siempre **We are Votum · B2B · Área inversores** (aunque WordPress tenga otro), y en el pie «B2B» y «Área inversores» apuntan a las páginas propias.
- **Limpieza:** quita los estilos de bloques de WordPress que el tema no usa (la portada pasa de ~34 KB a ~18 KB).
- **Tipografía:** `brand.css` usa la fuente del sistema en Apple (SF Pro) e **Inter** en el resto, alojada en `docs/assets/fonts/` (licencia SIL OFL 1.1). Sin Google Fonts.
- **Compartir:** descripción y etiquetas Open Graph/Twitter en cada página, con `og-votumlabs.jpg` (1200×630). Si la web cambia de dominio, actualiza `SITE_URL` en `export.py`.
- **404:** `docs/404.html`, que GitHub Pages sirve en cualquier ruta inexistente (sus enlaces van con ruta absoluta `/votum-web/`).

## Catálogo B2B (PDF)

- `catalogo/build.py` genera el catálogo en español e inglés (`docs/assets/catalogo/*.pdf`) con Chromium o Chrome:

  ```bash
  python catalogo/build.py          # HTML + PDF
  python catalogo/build.py --html   # solo HTML, para revisarlo en el navegador
  ```

- Productos, textos y líneas están en las tablas `LINES` y `UI` de `catalogo/build.py`. Los datos salen de las fichas de votumlabs.com y sospets.es (octubre de 2026); las fotos están en `docs/assets/img/productos/`.
- Sin afirmaciones de salud: solo formato, concentración, ingredientes y modo de uso. Fichas técnicas y condiciones profesionales, bajo petición.
- La página B2B enlaza el PDF en la cabecera y en el bloque de contacto.

## Versión en inglés

- Páginas en `docs/en/`: `index.html`, `b2b.html` e `investors.html`. Su contenido está en `paginas/en/`; la cabecera, el pie y el panel de accesibilidad se traducen con la tabla `EN_SHELL` de `export.py`.
- El selector de idioma de la cabecera enlaza cada página con su equivalente, y cada página declara `hreflang` y `og:locale`.
- La portada en inglés (`paginas/en/index.html`) es una traducción a mano: **si cambias textos de la portada en WordPress, actualízala también**. Si cambia algún texto de la cabecera o el pie, `export.py --paginas` se detiene y dice cuál falta en `EN_SHELL`.
- Los textos de los scripts (carrusel, portal del socio) están en los dos idiomas en `docs/assets/js/sections.js` y se eligen según `<html lang>`.

## Área inversores: acceso de socios

GitHub Pages solo sirve archivos estáticos, así que **no puede validar un login de forma segura**. El formulario de email + PIN no comprueba credenciales y el botón «Ver una demostración del panel» enseña el diseño con **datos ficticios**. No guardes datos reales de socios en este repositorio (ni en CSV ni en JSON): serían públicos. Para activar el portal real hace falta un servidor (por ejemplo, Supabase, un backend propio o el portal de Odoo) que valide el acceso y devuelva solo los datos del socio autenticado.

## Actualizar la web publicada

Con WAMP arrancado y el tema activo:

```bash
python export.py
git add -A
git commit -m "Actualiza exportación"
git push
```

GitHub Pages republica en uno o dos minutos.
