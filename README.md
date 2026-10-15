# Votum Labs — web de prueba

Versión estática de la portada del tema WordPress de Votum Labs, para revisión interna.
No es la web oficial: los enlaces del menú y de productos apuntan a [votumlabs.com](https://votumlabs.com).

- `docs/` — sitio publicado con GitHub Pages (HTML, CSS, JS e imágenes; sin WordPress ni base de datos).
- `export.py` — regenera `docs/` desde el WordPress local.

## Actualizar la web publicada

Con WAMP arrancado y el tema activo:

```bash
python export.py
git add -A
git commit -m "Actualiza exportación"
git push
```

GitHub Pages republica en uno o dos minutos.
