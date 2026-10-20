# Votum Labs — web de prueba

Versión estática de la portada del tema WordPress de Votum Labs, para revisión interna.
No es la web oficial: los enlaces del menú y de productos apuntan a [votumlabs.com](https://votumlabs.com).

- `docs/` — sitio publicado con GitHub Pages (HTML, CSS, JS e imágenes; sin WordPress ni base de datos).
- `export.py` — regenera `docs/` desde el WordPress local.
- `docs/b2b.html`, `docs/inversores.html`, `docs/sections.css`, `docs/assets/js/sections.js` — páginas **B2B** y **Área inversores**, hechas a mano (no salen de WordPress). `export.py` las conserva al regenerar.

## Menú

El menú superior es **We are Votum · B2B · Área inversores**. Está editado en `docs/index.html` y copiado en las dos páginas nuevas; si vuelves a exportar desde WordPress, cambia también el menú allí (Apariencia → Menús) o la exportación lo sobrescribirá.

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
