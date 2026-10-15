/**
 * Votum Labs: efectos interactivos.
 *
 * 1. Descifrado de texto ([data-vt-decode]): las letras aparecen de izquierda a derecha y,
 *    antes de fijarse, cada posición «baraja» 2–3 glifos de laboratorio en color de acento.
 *    - data-vt-decode            → al entrar en pantalla (una vez)
 *    - data-vt-decode="hover"    → al pasar el ratón (cada vez)
 * 2. Rastro de laboratorio: un pool de cuadros de 20 px sigue al cursor sobre una rejilla,
 *    cada uno con un color iridiscente y un glifo científico. Solo sobre zonas sin texto.
 *
 * Basado en el análisis de los componentes TextUnscramble/Eyebrow y CursorTrailAnimation
 * de githubuniverse.com (REA), reimplementado sin dependencias.
 */
( () => {
	const reducedMotion = window.matchMedia( '(prefers-reduced-motion: reduce)' );
	const finePointer = window.matchMedia( '(hover: hover) and (pointer: fine)' );
	// Respeta la preferencia del sistema y la opción «Detener animaciones» del panel de accesibilidad.
	const noMotion = () => reducedMotion.matches || document.documentElement.classList.contains( 'a11y-reduce-motion' );

	/* =========================================================
	 * 1. Descifrado de texto
	 * ======================================================= */
	const DECODE_GLYPHS = 'ACGTCBD0123456789+-=*/<>[]{}#%&·°µΔ';
	const SWAP_MS = 45;        // tiempo que dura cada glifo aleatorio
	const MAX_TOTAL_MS = 1100; // los textos largos se aceleran para no pasar de ~1 s

	const randomGlyph = () => DECODE_GLYPHS.charAt( Math.floor( Math.random() * DECODE_GLYPHS.length ) );
	const escapeHtml = ( s ) => s.replace( /[&<>"]/g, ( c ) => ( { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ c ] ) );

	/**
	 * Prepara el elemento: el texto real queda en un span para lectores de pantalla y la
	 * animación se dibuja en un span aria-hidden, así nunca se lee el texto «barajado».
	 */
	function prepare( el ) {
		if ( el.vtText !== undefined ) return true;
		if ( el.children.length ) return false; // solo elementos de texto plano
		const text = el.textContent.replace( /\s+/g, ' ' ).trim();
		if ( ! text ) return false;

		el.vtText = text;
		el.textContent = '';
		const sr = document.createElement( 'span' );
		sr.className = 'vt-sr';
		sr.textContent = text;
		const anim = document.createElement( 'span' );
		anim.className = 'vt-anim';
		anim.setAttribute( 'aria-hidden', 'true' );
		anim.textContent = text;
		el.append( sr, anim );
		el.vtAnim = anim;
		return true;
	}

	function decode( el ) {
		if ( ! prepare( el ) || el.vtRunning ) return;
		if ( noMotion() ) {
			el.vtAnim.textContent = el.vtText;
			return;
		}
		const text = el.vtText;
		const n = text.length;
		const step = Math.min( 45, MAX_TOTAL_MS / Math.max( n, 1 ) );

		// Plan determinista por posición: cuándo empieza y qué glifos mostrará.
		const plan = Array.from( text, ( ch, i ) => ( {
			start: i * step,
			glyphs: ch === ' ' ? [] : Array.from( { length: 2 + Math.floor( Math.random() * 2 ) }, randomGlyph ),
		} ) );
		const end = plan[ n - 1 ].start + 3 * SWAP_MS;

		el.vtRunning = true;
		el.classList.add( 'is-decoding' );
		const t0 = performance.now();
		let last = '';

		const frame = ( now ) => {
			const t = now - t0;
			let html = '';
			let ghost = '';
			for ( let i = 0; i < n; i++ ) {
				const p = plan[ i ];
				if ( t < p.start ) {
					ghost += text[ i ]; // aún oculto: ocupa su sitio para que el texto no salte de línea
					continue;
				}
				if ( ghost ) {
					html += `<span class="vt-ghost">${ escapeHtml( ghost ) }</span>`;
					ghost = '';
				}
				const j = Math.floor( ( t - p.start ) / SWAP_MS );
				html += j < p.glyphs.length
					? `<span class="vt-glyph">${ escapeHtml( p.glyphs[ j ] ) }</span>`
					: escapeHtml( text[ i ] );
			}
			if ( ghost ) html += `<span class="vt-ghost">${ escapeHtml( ghost ) }</span>`;

			if ( html !== last ) {
				el.vtAnim.innerHTML = html;
				last = html;
			}
			if ( t < end ) {
				requestAnimationFrame( frame );
			} else {
				el.vtAnim.textContent = text;
				el.vtRunning = false;
				el.classList.remove( 'is-decoding' );
			}
		};
		requestAnimationFrame( frame );
	}

	function initDecode() {
		const all = document.querySelectorAll( '[data-vt-decode]' );
		if ( noMotion() ) return;

		const onView = [];
		all.forEach( ( el ) => {
			if ( el.dataset.vtDecode === 'hover' ) {
				const target = el.closest( 'a, button' ) || el;
				target.addEventListener( 'mouseenter', () => decode( el ) );
				target.addEventListener( 'focus', () => decode( el ) );
			} else if ( prepare( el ) ) {
				el.vtAnim.innerHTML = `<span class="vt-ghost">${ escapeHtml( el.vtText ) }</span>`;
				onView.push( el );
			}
		} );

		if ( ! onView.length ) return;
		if ( ! ( 'IntersectionObserver' in window ) ) {
			onView.forEach( decode );
			return;
		}
		const io = new IntersectionObserver(
			( entries ) => {
				entries.forEach( ( entry ) => {
					if ( entry.isIntersecting ) {
						// Pequeño retardo para que coincida con la aparición (.ob-reveal) del bloque.
						setTimeout( () => decode( entry.target ), 150 );
						io.unobserve( entry.target );
					}
				} );
			},
			{ rootMargin: '0px 0px -12% 0px', threshold: 0 }
		);
		onView.forEach( ( el ) => io.observe( el ) );
	}

	/* =========================================================
	 * 2. Rastro de laboratorio bajo el cursor
	 * ======================================================= */
	const CELL = 20;
	const POOL = 12;
	const COLORS = [ '#9a7be6', '#5fb7e6', '#a8e0ec', '#f1e2b4', '#b9c6f0', '#c7a4ff' ];
	const TRAIL_GLYPHS = [ '+', '−', '=', '·', '°', 'µ', 'Δ', '%', 'C', 'B', 'D', 'A', 'G', 'T', '/' ];
	const DARK_TEXT_ON = new Set( [ '#a8e0ec', '#f1e2b4', '#b9c6f0' ] );

	function initTrail() {
		if ( ! finePointer.matches ) return;

		const zones = document.querySelectorAll( '[data-vt-trail]' );
		if ( ! zones.length ) return;

		const layer = document.createElement( 'div' );
		layer.className = 'vt-trail';
		layer.setAttribute( 'aria-hidden', 'true' );
		const blocks = Array.from( { length: POOL }, () => {
			const b = document.createElement( 'div' );
			b.className = 'vt-trail__block';
			b.innerHTML = '<span class="vt-trail__cell"></span>';
			layer.appendChild( b );
			return { el: b, cell: b.firstChild, timer: 0 };
		} );
		document.body.appendChild( layer );

		let lastX = -1;
		let lastY = -1;
		let next = 0;
		let paused = false;

		const isTextTarget = ( target ) => {
			if ( target.closest( 'a, button, input, textarea, select, label, [data-vt-no-trail]' ) ) return true;
			// Igual que el original: un elemento «hoja» con texto es texto; uno vacío o contenedor no.
			return target.children.length === 0 && target.textContent.trim() !== '';
		};

		const onMove = ( e ) => {
			if ( paused || noMotion() || isTextTarget( e.target ) ) return;
			const x = CELL * Math.floor( e.clientX / CELL );
			const y = CELL * Math.floor( e.clientY / CELL );
			if ( x === lastX && y === lastY ) return;
			lastX = x;
			lastY = y;

			const b = blocks[ next ];
			next = ( next + 1 ) % POOL;
			const color = COLORS[ Math.floor( Math.random() * COLORS.length ) ];

			clearTimeout( b.timer );
			b.el.style.transform = `translate(${ x }px, ${ y }px)`;
			b.cell.style.backgroundColor = color;
			b.cell.style.color = DARK_TEXT_ON.has( color ) ? '#000' : '#fff';
			b.cell.textContent = Math.random() < 0.3 ? '' : TRAIL_GLYPHS[ Math.floor( Math.random() * TRAIL_GLYPHS.length ) ];
			b.el.classList.remove( 'is-active' );
			void b.el.offsetWidth; // reinicia la transición si el cuadro se reutiliza antes de apagarse
			b.el.classList.add( 'is-active' );
			b.timer = setTimeout( () => b.el.classList.remove( 'is-active' ), 140 + Math.random() * 320 );
		};

		zones.forEach( ( z ) => z.addEventListener( 'mousemove', onMove, { passive: true } ) );
		document.querySelectorAll( '[data-vt-no-trail]' ).forEach( ( z ) => {
			z.addEventListener( 'mouseenter', () => ( paused = true ) );
			z.addEventListener( 'mouseleave', () => ( paused = false ) );
		} );
		// Al hacer scroll la rejilla se mueve con la página: se apagan los cuadros visibles.
		window.addEventListener( 'scroll', () => blocks.forEach( ( b ) => b.el.classList.remove( 'is-active' ) ), { passive: true } );
	}

	document.addEventListener( 'votum:a11ychange', () => {
		if ( ! noMotion() ) return;
		document.querySelectorAll( '[data-vt-decode]' ).forEach( ( el ) => {
			if ( el.vtAnim ) el.vtAnim.textContent = el.vtText;
		} );
		document.querySelectorAll( '.vt-trail__block' ).forEach( ( b ) => b.classList.remove( 'is-active' ) );
	} );

	initDecode();
	initTrail();
} )();
