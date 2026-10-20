/**
 * Páginas B2B y Área inversores: carrusel de líneas, contadores de rondas y portal del socio.
 *
 * Patrones observados con REA y reimplementados sin dependencias:
 *  - carrusel de tarjetas con flechas y paginación por puntos (neftislaboratorios.com, Swiper)
 *  - portal del socio con acceso por email + PIN y panel de participaciones (thebeeminelab.org/socio/)
 *
 * El portal de referencia valida el PIN en el navegador contra un CSV público: cualquiera puede
 * descargar la lista de socios. Aquí no se hace eso. En GitHub Pages no hay servidor, así que el
 * formulario no valida credenciales y solo ofrece una demostración con datos ficticios.
 */
( () => {
	const doc = document.documentElement;
	const EN = doc.lang.startsWith( 'en' );
	const T = EN
		? {
			slide: 'slide', of: 'of', group: ( i, n ) => `Go to group ${ i } of ${ n }`, locale: 'en-GB',
			missing: 'Enter your email and your PIN code.',
			pending: 'Private access will be enabled once the portal is connected to a secure server. In the meantime, write to us at info@votumlabs.com.',
			demoShow: 'See a demo of the dashboard', demoHide: 'Hide the demo',
		}
		: {
			slide: 'diapositiva', of: 'de', group: ( i, n ) => `Ir al grupo ${ i } de ${ n }`, locale: 'es-ES',
			missing: 'Introduce tu email y tu código PIN.',
			pending: 'El acceso privado se activará cuando el portal esté conectado a un servidor seguro. Mientras tanto, escríbenos a info@votumlabs.com.',
			demoShow: 'Ver una demostración del panel', demoHide: 'Ocultar la demostración',
		};
	const reduceMotion = () =>
		doc.classList.contains( 'a11y-reduce-motion' ) || window.matchMedia( '(prefers-reduced-motion: reduce)' ).matches;

	/* ---------- Carrusel de líneas ---------- */
	document.querySelectorAll( '[data-vt-carousel]' ).forEach( ( root ) => {
		const track = root.querySelector( '.vt-lines__track' );
		const slides = Array.from( track.children );
		const prev = root.querySelector( '[data-vt-prev]' );
		const next = root.querySelector( '[data-vt-next]' );
		const dotsBox = root.querySelector( '.vt-lines__dots' );
		let pages = [];

		slides.forEach( ( slide, i ) => {
			slide.setAttribute( 'role', 'group' );
			slide.setAttribute( 'aria-roledescription', T.slide );
			slide.setAttribute( 'aria-label', `${ i + 1 } ${ T.of } ${ slides.length }` );
		} );

		const step = () => slides[ 1 ] ? slides[ 1 ].offsetLeft - slides[ 0 ].offsetLeft : track.clientWidth;
		const perPage = () => Math.max( 1, Math.floor( ( track.clientWidth + 16 ) / step() ) );
		const maxScroll = () => track.scrollWidth - track.clientWidth;
		const scrollToX = ( x ) => track.scrollTo( { left: x, behavior: reduceMotion() ? 'auto' : 'smooth' } );

		// Una página por grupo de tarjetas visibles; la última se ajusta al final del carril.
		const buildDots = () => {
			const n = Math.ceil( slides.length / perPage() );
			pages = Array.from( { length: n }, ( _, i ) => Math.min( i * perPage() * step(), maxScroll() ) );
			dotsBox.replaceChildren(
				...pages.map( ( x, i ) => {
					const dot = document.createElement( 'button' );
					dot.type = 'button';
					dot.className = 'vt-lines__dot';
					dot.setAttribute( 'aria-label', T.group( i + 1, n ) );
					dot.addEventListener( 'click', () => scrollToX( x ) );
					return dot;
				} )
			);
			dotsBox.hidden = n < 2;
			update();
		};

		const update = () => {
			const x = track.scrollLeft;
			let current = 0;
			pages.forEach( ( p, i ) => {
				if ( x >= p - 8 ) current = i;
			} );
			dotsBox.querySelectorAll( 'button' ).forEach( ( dot, i ) => dot.setAttribute( 'aria-current', String( i === current ) ) );
			prev.disabled = x <= 4;
			next.disabled = x >= maxScroll() - 4;
		};

		prev.addEventListener( 'click', () => scrollToX( track.scrollLeft - perPage() * step() ) );
		next.addEventListener( 'click', () => scrollToX( track.scrollLeft + perPage() * step() ) );
		track.addEventListener( 'scroll', () => window.requestAnimationFrame( update ), { passive: true } );
		track.addEventListener( 'keydown', ( e ) => {
			if ( e.target !== track ) return;
			if ( e.key === 'ArrowRight' ) { e.preventDefault(); scrollToX( track.scrollLeft + step() ); }
			if ( e.key === 'ArrowLeft' ) { e.preventDefault(); scrollToX( track.scrollLeft - step() ); }
		} );
		window.addEventListener( 'resize', buildDots );
		buildDots();
	} );

	/* ---------- Contadores de las rondas ---------- */
	// El valor final ya está en el HTML (se lee sin JavaScript); aquí solo se anima desde 0.
	const counters = document.querySelectorAll( '[data-vt-count]' );
	const format = ( el, v ) => {
		const decimals = Number( el.dataset.decimals || 0 );
		el.textContent = ( el.dataset.prefix || '' ) + v.toLocaleString( T.locale, { minimumFractionDigits: decimals, maximumFractionDigits: decimals } ) + ( el.dataset.suffix || '' );
	};
	const animate = ( el ) => {
		const to = Number( el.dataset.vtCount );
		const start = performance.now();
		const tick = ( now ) => {
			const t = Math.min( 1, ( now - start ) / 1600 );
			format( el, to * ( 1 - Math.pow( 1 - t, 3 ) ) );
			if ( t < 1 ) window.requestAnimationFrame( tick );
		};
		window.requestAnimationFrame( tick );
	};
	if ( counters.length && 'IntersectionObserver' in window && ! reduceMotion() ) {
		const io = new IntersectionObserver( ( entries ) => {
			entries.forEach( ( entry ) => {
				if ( entry.isIntersecting ) {
					animate( entry.target );
					io.unobserve( entry.target );
				}
			} );
		}, { threshold: 0.6 } );
		counters.forEach( ( el ) => io.observe( el ) );
	}

	/* ---------- Portal del socio ---------- */
	const form = document.getElementById( 'vt-login' );
	const status = document.getElementById( 'vt-login-status' );
	const panel = document.getElementById( 'vt-panel' );
	const demoBtn = document.querySelector( '[data-vt-demo]' );

	form?.addEventListener( 'submit', ( e ) => {
		e.preventDefault();
		const email = form.elements.email.value.trim();
		const pin = form.elements.pin.value.trim();
		if ( ! email || ! pin ) {
			status.textContent = T.missing;
			return;
		}
		// Sin servidor no hay validación segura posible: no se comprueba nada en el navegador.
		form.reset();
		status.textContent = T.pending;
	} );

	demoBtn?.addEventListener( 'click', () => {
		const open = panel.hidden;
		panel.hidden = ! open;
		demoBtn.setAttribute( 'aria-expanded', String( open ) );
		demoBtn.textContent = open ? T.demoHide : T.demoShow;
		if ( open ) {
			panel.scrollIntoView( { behavior: reduceMotion() ? 'auto' : 'smooth', block: 'start' } );
			panel.querySelector( 'h2' )?.focus( { preventScroll: true } );
		}
	} );
} )();
