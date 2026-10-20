"""Genera el catálogo B2B de Votum Labs en PDF (español e inglés).

Uso:
    python catalogo/build.py            # HTML + PDF (necesita Chromium o Chrome)
    python catalogo/build.py --html     # solo el HTML, para revisarlo en el navegador

Salida: docs/assets/catalogo/votum-labs-catalogo-b2b.pdf y votum-labs-b2b-catalogue.pdf
Los datos salen de las fichas publicadas en votumlabs.com y sospets.es (octubre de 2026).
"""
import argparse
import shutil
import subprocess
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / 'docs'
OUT = DOCS / 'assets' / 'catalogo'
EDITION = '2026'

# Textos fijos por idioma.
UI = {
	'es': {
		'file': 'votum-labs-catalogo-b2b', 'lang': 'es', 'title': 'Catálogo B2B',
		'subtitle': 'Productos dermofarmacéuticos con CBD para farmacias, distribuidores y profesionales',
		'about_h': 'Quiénes somos',
		'about': 'VOTUM LABS es un laboratorio biotecnológico especializado en soluciones terapéuticas avanzadas basadas en principios activos vanguardistas, con un enfoque integral que abarca desde la formulación hasta la validación preclínica de sus productos.',
		'facts': [('2021', 'Año de fundación'), ('B Corp', 'Empresa certificada'), ('Lorquí', 'Murcia, España')],
		'how_h': 'Cómo trabajamos',
		'steps': [('Investigación', 'Principios activos vanguardistas e ingredientes bioactivos de alta pureza.'),
		          ('Diseño molecular', 'Formulación orientada a cada objetivo de cuidado y bienestar.'),
		          ('Desarrollo galénico', 'Aceites, bálsamos, cremas y tópicos con tecnologías de liberación progresiva.'),
		          ('Validación funcional', 'Validación preclínica antes de llegar a la farmacia y al consumidor.')],
		'brands_h': 'Nuestras marcas',
		'format': 'Formato', 'active': 'Activo', 'ingredients': 'Ingredientes', 'use': 'Uso',
		'custom_h': 'Desarrollo a medida',
		'custom': 'Investigación, diseño molecular, desarrollo galénico y validación funcional dentro de un mismo ecosistema científico. Cuéntanos tu proyecto: formulamos, desarrollamos y validamos productos dermofarmacéuticos para tu marca o tu canal.',
		'contact_h': 'Contacto profesional',
		'hours': 'Lunes a viernes, 9:00 – 18:00',
		'address': 'Calle Río Turia 1, 30564 Lorquí, Murcia, España',
		'ask': 'Fichas técnicas, certificados de análisis, formatos y condiciones profesionales, bajo petición.',
		'legal': 'Información orientativa basada en las fichas de producto publicadas en votumlabs.com y sospets.es (octubre de 2026). Las imágenes pueden no reflejar el envase vigente.',
		'page': 'Página',
	},
	'en': {
		'file': 'votum-labs-b2b-catalogue', 'lang': 'en', 'title': 'B2B Catalogue',
		'subtitle': 'Dermopharmaceutical CBD products for pharmacies, distributors and professionals',
		'about_h': 'About us',
		'about': 'VOTUM LABS is a biotechnology laboratory specialising in advanced therapeutic solutions based on cutting-edge active ingredients, with an end-to-end approach that runs from formulation to the preclinical validation of its products.',
		'facts': [('2021', 'Year founded'), ('B Corp', 'Certified company'), ('Lorquí', 'Murcia, Spain')],
		'how_h': 'How we work',
		'steps': [('Research', 'Cutting-edge active ingredients and high-purity bioactive compounds.'),
		          ('Molecular design', 'Formulation built around each care and wellbeing goal.'),
		          ('Galenic development', 'Oils, balms, creams and topicals with progressive-release technologies.'),
		          ('Functional validation', 'Preclinical validation before reaching the pharmacy and the consumer.')],
		'brands_h': 'Our brands',
		'format': 'Format', 'active': 'Active', 'ingredients': 'Ingredients', 'use': 'Use',
		'custom_h': 'Bespoke development',
		'custom': 'Research, molecular design, galenic development and functional validation within a single scientific ecosystem. Tell us about your project: we formulate, develop and validate dermopharmaceutical products for your brand or channel.',
		'contact_h': 'Trade enquiries',
		'hours': 'Monday to Friday, 9:00 – 18:00 (CET)',
		'address': 'Calle Río Turia 1, 30564 Lorquí, Murcia, Spain',
		'ask': 'Technical data sheets, certificates of analysis, formats and trade terms available on request.',
		'legal': 'Indicative information based on the product pages published on votumlabs.com and sospets.es (October 2026). Images may not reflect current packaging.',
		'page': 'Page',
	},
}

# Líneas y productos. Cada texto: {'es': ..., 'en': ...}; None = no se muestra.
LINES = [
	{
		'name': 'V. Sport', 'grad': 'linear-gradient(135deg,#9a7be6,#5fb7e6 55%,#a8e0ec)',
		'intro': {'es': 'Recuperación y activación muscular con CBD. Cuatro fórmulas tópicas con 2000 mg de Full Spectrum y menos del 0,2 % de THC.',
		          'en': 'Muscle recovery and activation with CBD. Four topical formulas with 2000 mg Full Spectrum and less than 0.2% THC.'},
		'web': 'votumlabs.com',
		'products': [
			{'name': 'Thera.Pain Balm', 'img': 'thera-pain-balm',
			 'claim': {'es': 'Bálsamo de CBD para músculos y articulaciones.', 'en': 'CBD balm for muscles and joints.'},
			 'format': {'es': 'Tarro de 100 ml', 'en': '100 ml jar'},
			 'active': {'es': '2000 mg Full Spectrum (CBD, CBG, CBN, CBC)', 'en': '2000 mg Full Spectrum (CBD, CBG, CBN, CBC)'},
			 'ingredients': {'es': 'Aceite de coco orgánico, lavanda, eucalipto, cera de abejas y aceites esenciales.',
			                 'en': 'Organic coconut oil, lavender, eucalyptus, beeswax and essential oils.'},
			 'use': {'es': 'Sobre piel limpia y seca, masajear hasta su absorción; 3–4 veces al día.',
			         'en': 'Apply to clean, dry skin and massage until absorbed; 3–4 times a day.'}},
			{'name': 'Muscle.Ice Cream', 'img': 'muscle-ice-cream',
			 'claim': {'es': 'Crema de efecto frío para después del entrenamiento.', 'en': 'Cooling cream for after training.'},
			 'format': {'es': 'Tubo de 100 ml', 'en': '100 ml tube'},
			 'active': {'es': '2000 mg Full Spectrum (CBD, CBG, CBN, CBC)', 'en': '2000 mg Full Spectrum (CBD, CBG, CBN, CBC)'},
			 'ingredients': {'es': 'Aceite de coco orgánico, aceite de aguacate, vitamina E y mentol. Vegana.',
			                 'en': 'Organic coconut oil, avocado oil, vitamin E and menthol. Vegan.'},
			 'use': {'es': 'Tras la actividad física, sobre las zonas cargadas.', 'en': 'After physical activity, on tired areas.'}},
			{'name': 'Muscle.Warm Cream', 'img': 'muscle-warm-cream',
			 'claim': {'es': 'Crema de efecto calor para activar el músculo antes de entrenar.', 'en': 'Warming cream to activate muscles before training.'},
			 'format': {'es': 'Tubo de 100 ml', 'en': '100 ml tube'},
			 'active': {'es': '2000 mg Full Spectrum (CBD, CBG, CBN, CBC)', 'en': '2000 mg Full Spectrum (CBD, CBG, CBN, CBC)'},
			 'ingredients': {'es': 'Aceite de coco orgánico, aceite de aguacate, vitamina E y nicotinato de metilo. Vegana.',
			                 'en': 'Organic coconut oil, avocado oil, vitamin E and methyl nicotinate. Vegan.'},
			 'use': {'es': 'Antes del ejercicio, sobre las zonas que se quieren activar.', 'en': 'Before exercise, on the areas to activate.'}},
			{'name': 'Muscle.Recovery Cream', 'img': 'muscle-recovery-cream',
			 'claim': {'es': 'Crema recuperadora para después del ejercicio.', 'en': 'Recovery cream for after exercise.'},
			 'format': {'es': 'Tubo de 100 ml', 'en': '100 ml tube'},
			 'active': {'es': '2000 mg Full Spectrum (CBD, CBG, CBN, CBC)', 'en': '2000 mg Full Spectrum (CBD, CBG, CBN, CBC)'},
			 'ingredients': {'es': 'Aceite de coco orgánico, aceite de aguacate, vitamina E, alcanfor y árnica.',
			                 'en': 'Organic coconut oil, avocado oil, vitamin E, camphor and arnica.'},
			 'use': {'es': 'Tras el ejercicio, sobre las zonas con fatiga muscular.', 'en': 'After exercise, on areas with muscle fatigue.'}},
		],
	},
	{
		'name': 'V. Liquids', 'grad': 'linear-gradient(135deg,#f1e2b4,#b9c6f0 50%,#9a7be6)',
		'intro': {'es': 'Gotas de CBD para dormir, concentrarse y equilibrarse. Frascos de 30 ml con cuentagotas anatómico y dosis ajustable.',
		          'en': 'CBD drops to sleep, focus and find balance. 30 ml bottles with an anatomical dropper and adjustable dose.'},
		'web': 'votumlabs.com',
		'products': [
			{'name': 'Sleep.Drops Oil', 'img': 'sleep-drops-oil',
			 'claim': {'es': 'Aceite de CBD para la rutina de descanso.', 'en': 'CBD oil for a bedtime routine.'},
			 'format': {'es': 'Frasco de 30 ml con cuentagotas', 'en': '30 ml dropper bottle'},
			 'active': {'es': 'Hasta 9000 mg Full Spectrum (CBD, CBG, CBN), < 0,2 % THC', 'en': 'Up to 9000 mg Full Spectrum (CBD, CBG, CBN), < 0.2% THC'},
			 'ingredients': {'es': 'Aceite MCT orgánico, extracto de menta y melatonina. Vegano.',
			                 'en': 'Organic MCT oil, mint extract and melatonin. Vegan.'},
			 'use': {'es': 'Sublingual: mantener 30–40 s antes de tragar, antes de dormir.', 'en': 'Sublingual: hold for 30–40 s before swallowing, at bedtime.'}},
			{'name': 'Focus.Drops Oil', 'img': 'focus-drops-oil',
			 'claim': {'es': 'Aceite de CBD para días de estudio o trabajo intenso.', 'en': 'CBD oil for intense study or work days.'},
			 'format': {'es': 'Frasco de 30 ml con cuentagotas', 'en': '30 ml dropper bottle'},
			 'active': {'es': 'Hasta 3000 mg Broad Spectrum', 'en': 'Up to 3000 mg Broad Spectrum'},
			 'ingredients': None,
			 'use': {'es': 'Sublingual, con dosis ajustable.', 'en': 'Sublingual, adjustable dose.'}},
			{'name': 'Intimate.Drops Oil', 'img': 'intimate-drops-oil',
			 'claim': {'es': 'Aceite de CBD con canela para el ciclo menstrual.', 'en': 'CBD oil with cinnamon for the menstrual cycle.'},
			 'format': {'es': 'Frasco de 30 ml con cuentagotas', 'en': '30 ml dropper bottle'},
			 'active': {'es': 'Hasta 3000 mg Full Spectrum (CBD, CBG, CBN), < 0,2 % THC', 'en': 'Up to 3000 mg Full Spectrum (CBD, CBG, CBN), < 0.2% THC'},
			 'ingredients': {'es': 'Aceite MCT orgánico y extracto de canela. Vegano.', 'en': 'Organic MCT oil and cinnamon extract. Vegan.'},
			 'use': {'es': 'Sublingual, 1–2 veces al día, antes y durante el periodo.', 'en': 'Sublingual, 1–2 times a day, before and during the period.'}},
			{'name': 'Balance.Drops Oil', 'img': 'balance-drops-oil',
			 'claim': {'es': 'Aceite de CBD sin THC para el equilibrio diario.', 'en': 'THC-free CBD oil for everyday balance.'},
			 'format': {'es': 'Frasco de 30 ml con cuentagotas', 'en': '30 ml dropper bottle'},
			 'active': {'es': 'Hasta 9000 mg Broad Spectrum, sin THC', 'en': 'Up to 9000 mg Broad Spectrum, THC-free'},
			 'ingredients': {'es': 'Aceite MCT orgánico.', 'en': 'Organic MCT oil.'},
			 'use': {'es': 'Sublingual, 1–2 veces al día.', 'en': 'Sublingual, 1–2 times a day.'}},
		],
	},
	{
		'name': 'SOS Pets', 'grad': 'linear-gradient(135deg,#ffb4a8,#f1e2b4 55%,#a8e0ec)',
		'intro': {'es': 'Bienestar con CBD para perros y gatos, con ingredientes naturales y tecnología con ciclodextrina para una absorción más rápida.',
		          'en': 'CBD wellbeing for dogs and cats, with natural ingredients and cyclodextrin technology for faster absorption.'},
		'web': 'sospets.es',
		'products': [
			{'name': 'SOS Spray', 'img': 'sos-spray',
			 'claim': {'es': 'Spray calmante para situaciones de estrés: petardos, viajes o visitas al veterinario.',
			           'en': 'Calming spray for stressful moments: fireworks, travel or vet visits.'},
			 'format': {'es': 'Spray', 'en': 'Spray'}, 'active': None, 'ingredients': None,
			 'use': {'es': 'Perros y gatos de todas las edades y tamaños.', 'en': 'Dogs and cats of all ages and sizes.'}},
			{'name': 'SOS Aceite', 'name_en': 'SOS Oil', 'img': 'sos-aceite',
			 'claim': {'es': 'Aceite para el bienestar diario en momentos de cambio o situaciones poco habituales.',
			           'en': 'Oil for everyday wellbeing during changes or unusual situations.'},
			 'format': {'es': 'Frasco con cuentagotas; disponible con salmón', 'en': 'Dropper bottle; also available with salmon'},
			 'active': None, 'ingredients': None,
			 'use': {'es': 'Perros y gatos.', 'en': 'Dogs and cats.'}},
			{'name': 'SOS Dol', 'img': 'sos-dol',
			 'claim': {'es': 'Crema de masaje para el cuidado localizado.', 'en': 'Massage cream for targeted care.'},
			 'format': {'es': 'Tubo dosificador de 5 ml', 'en': '5 ml dispenser tube'},
			 'active': {'es': '330 mg Broad Spectrum (CBD, CBG, CBN) + 170 mg de árnica', 'en': '330 mg Broad Spectrum (CBD, CBG, CBN) + 170 mg arnica'},
			 'ingredients': None,
			 'use': {'es': 'Cada clic dispensa 0,05 ml, adecuado para 5 kg de peso.', 'en': 'Each click dispenses 0.05 ml, suitable for 5 kg of body weight.'}},
		],
	},
]

CSS = '''
@font-face { font-family: "Inter"; font-weight: 100 900; src: url("../docs/assets/fonts/inter-latin-wght-normal.woff2") format("woff2"); }
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { font-family: "Inter", "Helvetica Neue", Arial, sans-serif; color: #000; font-size: 9.5pt; line-height: 1.45;
	-webkit-print-color-adjust: exact; print-color-adjust: exact; }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden; page-break-after: always; break-after: page;
	padding: 18mm 16mm 20mm; display: flex; flex-direction: column; }
.page:last-child { page-break-after: auto; break-after: auto; }
h1, h2, h3 { font-weight: 400; letter-spacing: -.02em; margin: 0; }
.eyebrow { font-size: 8pt; text-transform: uppercase; letter-spacing: .14em; color: #5c5c66; margin: 0 0 3mm; }
.grad-text { background: linear-gradient(90deg,#7b5ce0,#3f97cf,#b98a2e); -webkit-background-clip: text; background-clip: text; color: transparent; }
.rule { height: 1.4mm; width: 34mm; border-radius: 1mm; background: linear-gradient(90deg,#7b5ce0,#3f97cf,#b98a2e); margin: 6mm 0; }
.folio { position: absolute; left: 16mm; right: 16mm; bottom: 9mm; display: flex; justify-content: space-between; font-size: 7.5pt; color: #8a8a94; }

/* Portada */
.cover { padding: 0; color: #000; }
.cover__bg { position: absolute; inset: 0; background: url("../docs/assets/img/hero-october-votumlabs.webp") 62% center / cover; }
.cover__card { position: absolute; left: 14mm; right: 14mm; bottom: 16mm; background: rgba(255,255,255,.9); border-radius: 9mm; padding: 14mm 14mm 13mm; }
.cover__brand { display: flex; align-items: center; gap: 3mm; font-size: 11pt; letter-spacing: .12em; text-transform: uppercase; }
.cover__brand img { width: 7mm; height: 8mm; }
.cover h1 { font-size: 46pt; line-height: 1; margin: 9mm 0 4mm; }
.cover p { font-size: 13pt; line-height: 1.35; margin: 0; max-width: 140mm; color: #222; }
.cover__edition { position: absolute; top: 14mm; right: 14mm; background: #000; color: #fff; border-radius: 99px; padding: 2.4mm 5mm; font-size: 9pt; letter-spacing: .08em; }

/* Quiénes somos */
.lead { font-size: 15pt; line-height: 1.35; font-weight: 300; margin: 0; }
.facts { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; margin: 9mm 0 11mm; }
.fact { border-radius: 6mm; padding: 6mm; background: linear-gradient(110deg,#c7a4ff,#a8e0ec,#f1e2b4); }
.fact strong { display: block; font-size: 20pt; font-weight: 400; letter-spacing: -.02em; }
.fact span { font-size: 8.5pt; color: #2b2b33; }
h2.section { font-size: 22pt; margin: 0 0 5mm; }
.steps { display: grid; grid-template-columns: repeat(2, 1fr); gap: 4mm; counter-reset: s; }
.step { border-radius: 6mm; background: #f4f4f7; padding: 5.5mm 6mm; counter-increment: s; }
.step::before { content: counter(s, decimal-leading-zero); display: block; color: #7b5ce0; font-size: 8.5pt; margin-bottom: 2.5mm; }
.step h3 { font-size: 12pt; margin-bottom: 1.5mm; }
.step p { margin: 0; color: #333; }
.brands-block { margin-top: auto; }
.brands { display: flex; gap: 5mm; }
.brand { flex: 1; height: 24mm; border-radius: 6mm; background: #f4f4f7; display: flex; align-items: center; justify-content: center; }
.brand img { max-height: 11mm; max-width: 60%; }

/* Línea de producto */
.line-head { display: flex; gap: 7mm; align-items: center; margin-bottom: 7mm; }
.line-orb { flex: none; width: 24mm; height: 24mm; border-radius: 50%; box-shadow: inset -5mm -6mm 12mm rgba(255,255,255,.5); }
.line-head h2 { font-size: 30pt; line-height: 1; }
.line-head p { margin: 2.5mm 0 0; color: #333; font-size: 10pt; max-width: 125mm; }
.grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5mm; flex: 1; align-content: start; }
.grid--3 { grid-template-columns: 1fr; gap: 4.5mm; }
.card { border: .3mm solid #e3e3ea; border-radius: 6mm; overflow: hidden; display: flex; flex-direction: column; break-inside: avoid; }
.card__media { position: relative; height: 40mm; display: flex; align-items: center; justify-content: center; }
.card__media::before { content: ""; position: absolute; inset: 0; background: var(--grad); opacity: .45; }
.card__media img { position: relative; max-height: 35mm; max-width: 70%; object-fit: contain; filter: drop-shadow(0 2mm 3mm rgba(40,30,90,.18)); }
.card__body { padding: 4mm 5mm 4.5mm; }
.card h3 { font-size: 13.5pt; margin: 0 0 1mm; }
.card .claim { margin: 0 0 3mm; color: #222; }
.card dl { margin: 0; display: grid; grid-template-columns: 19mm 1fr; gap: 1.4mm 2mm; font-size: 8pt; }
.card dt { color: #6a6a74; }
.card dd { margin: 0; color: #111; }
.grid--3 .card { flex-direction: row; min-height: 62mm; }
.grid--3 .card__media { width: 66mm; height: auto; flex: none; }
.grid--3 .card__media img { max-height: 50mm; max-width: 80%; }
.grid--3 .card__body { padding: 6mm 7mm; align-self: center; }
.grid--3 .card h3 { font-size: 16pt; }

/* Cierre */
.custom { border-radius: 8mm; padding: 10mm; background: linear-gradient(110deg,#c7a4ff,#a8e0ec,#f1e2b4); margin-bottom: 9mm; }
.custom h2 { font-size: 24pt; margin-bottom: 3mm; }
.custom p { margin: 0; font-size: 11pt; line-height: 1.45; color: #1a1a22; }
.contact { border-radius: 8mm; padding: 10mm; background: #000; color: #fff; }
.contact h2 { font-size: 24pt; margin-bottom: 6mm; }
.contact .rows { display: grid; grid-template-columns: repeat(2, 1fr); gap: 5mm 8mm; }
.contact .label { font-size: 7.5pt; text-transform: uppercase; letter-spacing: .12em; opacity: .6; margin-bottom: 1mm; }
.contact .value { font-size: 12pt; }
.contact a { color: #fff; text-decoration: none; }
.ask { margin: 8mm 0 0; font-size: 10.5pt; }
.legal { margin-top: auto; font-size: 7.5pt; color: #6a6a74; }
.badges { display: flex; align-items: center; gap: 7mm; margin: 8mm 0 5mm; font-size: 8pt; color: #5c5c66; }
.badges img { height: 13mm; }
'''


def t(value, lang):
	return None if value is None else value[lang]


def product_card(p, grad, lang, ui):
	name = p.get('name_en', p['name']) if lang == 'en' else p['name']
	rows = [(ui['format'], t(p['format'], lang)), (ui['active'], t(p['active'], lang)),
	        (ui['ingredients'], t(p['ingredients'], lang)), (ui['use'], t(p['use'], lang))]
	dl = ''.join(f'<dt>{escape(k)}</dt><dd>{escape(v)}</dd>' for k, v in rows if v)
	return (f'<article class="card"><div class="card__media" style="--grad:{grad}">'
	        f'<img src="../docs/assets/img/productos/{p["img"]}.webp" alt=""></div>'
	        f'<div class="card__body"><h3>{escape(name)}</h3><p class="claim">{escape(t(p["claim"], lang))}</p><dl>{dl}</dl></div></article>')


def build_html(lang):
	ui = UI[lang]
	folio = lambda n: f'<div class="folio"><span>Votum Labs · {ui["title"]} {EDITION}</span><span>{ui["page"]} {n}</span></div>'
	pages = [f'''
<section class="page cover">
	<div class="cover__bg"></div>
	<div class="cover__edition">{ui["title"].upper()} · {EDITION}</div>
	<div class="cover__card">
		<div class="cover__brand"><img src="../docs/assets/img/votumlabs-fav.svg" alt="">Votum Labs</div>
		<h1>{ui["title"]}</h1>
		<p>{ui["subtitle"]}</p>
	</div>
</section>''', f'''
<section class="page">
	<p class="eyebrow">Votum Labs</p>
	<h2 class="section">{ui["about_h"]}</h2>
	<p class="lead">{ui["about"]}</p>
	<div class="facts">{''.join(f'<div class="fact"><strong>{a}</strong><span>{b}</span></div>' for a, b in ui["facts"])}</div>
	<h2 class="section">{ui["how_h"]}</h2>
	<div class="steps">{''.join(f'<div class="step"><h3>{a}</h3><p>{b}</p></div>' for a, b in ui["steps"])}</div>
	<div class="brands-block">
		<p class="eyebrow">{ui["brands_h"]}</p>
		<div class="brands">
			<div class="brand"><img src="../docs/assets/img/SOS-LOGO-ROJO.png" alt="SOS Pets"></div>
			<div class="brand"><img src="../docs/assets/img/logo-cronidol.svg" alt="Cronidol"></div>
			<div class="brand"><img src="../docs/assets/img/vezelay-logo.svg" alt="Vezelay Lab"></div>
		</div>
	</div>
	{folio(2)}
</section>''']
	for i, line in enumerate(LINES):
		cards = ''.join(product_card(p, line['grad'], lang, ui) for p in line['products'])
		grid = 'grid grid--3' if len(line['products']) == 3 else 'grid'
		pages.append(f'''
<section class="page">
	<div class="line-head"><div class="line-orb" style="background:{line["grad"]}"></div>
		<div><p class="eyebrow">{ui["title"]} · {line["web"]}</p><h2>{line["name"]}</h2><p>{escape(t(line["intro"], lang))}</p></div></div>
	<div class="{grid}">{cards}</div>
	{folio(3 + i)}
</section>''')
	pages.append(f'''
<section class="page">
	<div class="custom"><p class="eyebrow">B2B</p><h2>{ui["custom_h"]}</h2><p>{ui["custom"]}</p></div>
	<div class="contact">
		<h2>{ui["contact_h"]}</h2>
		<div class="rows">
			<div><div class="label">Email</div><div class="value"><a href="mailto:info@votumlabs.com">info@votumlabs.com</a></div></div>
			<div><div class="label">Tel. / WhatsApp</div><div class="value"><a href="https://wa.me/+34633862669">+34 633 86 26 69</a></div></div>
			<div><div class="label">{'Horario' if lang == 'es' else 'Hours'}</div><div class="value">{ui["hours"]}</div></div>
			<div><div class="label">Web</div><div class="value"><a href="https://votumlabs.com">votumlabs.com</a> · <a href="https://sospets.es">sospets.es</a></div></div>
			<div style="grid-column:1/-1"><div class="label">{'Dirección' if lang == 'es' else 'Address'}</div><div class="value">{ui["address"]}</div></div>
		</div>
	</div>
	<p class="ask">{ui["ask"]}</p>
	<div class="badges"><img src="../docs/assets/img/LogoESPTagESP_Estandares_Negro-1.png" alt="B Corp"><span>{'Empresa B Corp certificada' if lang == 'es' else 'Certified B Corporation'}</span></div>
	<p class="legal">{ui["legal"]}</p>
	{folio(3 + len(LINES))}
</section>''')
	return f'''<!doctype html>
<html lang="{ui["lang"]}"><head><meta charset="utf-8"><title>Votum Labs · {ui["title"]} {EDITION}</title>
<style>{CSS}</style></head><body>{''.join(pages)}
</body></html>'''


def find_browser():
	for name in ('chromium', 'chromium-browser', 'google-chrome', 'chrome'):
		path = shutil.which(name)
		if path:
			return path
	raise SystemExit('No se encuentra Chromium/Chrome para generar el PDF (usa --html para revisar el HTML).')


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument('--html', action='store_true', help='solo generar el HTML')
	args = ap.parse_args()
	OUT.mkdir(parents=True, exist_ok=True)
	browser = None if args.html else find_browser()
	for lang in ('es', 'en'):
		html_path = ROOT / 'catalogo' / f'{UI[lang]["file"]}.html'
		html_path.write_text(build_html(lang), encoding='utf-8')
		print('HTML:', html_path.relative_to(ROOT))
		if browser:
			pdf = OUT / f'{UI[lang]["file"]}.pdf'
			subprocess.run([browser, '--headless', '--disable-gpu', '--no-pdf-header-footer',
			                '--run-all-compositor-stages-before-draw', '--virtual-time-budget=4000',
			                f'--print-to-pdf={pdf}', html_path.as_uri()],
			               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
			print('PDF: ', pdf.relative_to(ROOT), f'{pdf.stat().st_size // 1024} KB')


if __name__ == '__main__':
	main()
