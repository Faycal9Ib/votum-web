/**
 * Votum Labs: panel de accesibilidad.
 * Las preferencias se guardan en localStorage ('votumA11y') y se aplican como clases en <html>;
 * el script del <head> las restaura antes de pintar para evitar parpadeos.
 */
( () => {
	const KEY = 'votumA11y';
	const root = document.documentElement;
	const wrap = document.querySelector( '.ob-a11y' );
	if ( ! wrap ) return;

	const toggle = wrap.querySelector( '.ob-a11y__toggle' );
	const panel = wrap.querySelector( '.ob-a11y__panel' );
	const sizeBtns = [ ...wrap.querySelectorAll( '[data-a11y-text]' ) ];
	const switches = [ ...wrap.querySelectorAll( '[data-a11y]' ) ];

	const load = () => {
		try {
			return JSON.parse( localStorage.getItem( KEY ) || '{}' );
		} catch ( e ) {
			return {};
		}
	};
	const save = ( prefs ) => {
		try {
			localStorage.setItem( KEY, JSON.stringify( prefs ) );
		} catch ( e ) {}
	};

	let prefs = load();

	const apply = () => {
		root.classList.remove( 'a11y-text-1', 'a11y-text-2' );
		if ( prefs.text ) root.classList.add( `a11y-text-${ prefs.text }` );
		sizeBtns.forEach( ( b ) => b.setAttribute( 'aria-pressed', String( Number( b.dataset.a11yText ) === ( prefs.text || 0 ) ) ) );

		switches.forEach( ( b ) => {
			const on = !! prefs[ b.dataset.a11y ];
			root.classList.toggle( `a11y-${ b.dataset.a11y }`, on );
			b.setAttribute( 'aria-pressed', String( on ) );
		} );

		const active = Object.values( prefs ).some( Boolean );
		wrap.classList.toggle( 'has-prefs', active );
		document.dispatchEvent( new CustomEvent( 'votum:a11ychange', { detail: { ...prefs } } ) );
	};

	const update = ( change ) => {
		prefs = { ...prefs, ...change };
		Object.keys( prefs ).forEach( ( k ) => ! prefs[ k ] && delete prefs[ k ] );
		save( prefs );
		apply();
	};

	sizeBtns.forEach( ( b ) => b.addEventListener( 'click', () => update( { text: Number( b.dataset.a11yText ) } ) ) );
	switches.forEach( ( b ) => b.addEventListener( 'click', () => update( { [ b.dataset.a11y ]: ! prefs[ b.dataset.a11y ] } ) ) );
	wrap.querySelector( '[data-a11y-reset]' ).addEventListener( 'click', () => {
		prefs = {};
		save( prefs );
		apply();
	} );

	/* Abrir / cerrar */
	const setOpen = ( open, focusBack = false ) => {
		panel.hidden = ! open;
		toggle.setAttribute( 'aria-expanded', String( open ) );
		if ( open ) panel.querySelector( 'button' ).focus();
		else if ( focusBack ) toggle.focus();
	};
	toggle.addEventListener( 'click', () => setOpen( panel.hidden ) );
	document.addEventListener( 'keydown', ( e ) => {
		if ( e.key === 'Escape' && ! panel.hidden ) setOpen( false, true );
	} );
	document.addEventListener( 'click', ( e ) => {
		if ( ! panel.hidden && ! wrap.contains( e.target ) ) setOpen( false );
	} );

	apply();
} )();

/**
 * Selector de idioma de la cabecera.
 */
( () => {
	const lang = document.querySelector( '.ob-lang' );
	if ( ! lang ) return;
	const btn = lang.querySelector( '.ob-lang__toggle' );
	const list = lang.querySelector( '.ob-lang__list' );

	const setOpen = ( open, focusBack = false ) => {
		list.hidden = ! open;
		btn.setAttribute( 'aria-expanded', String( open ) );
		if ( ! open && focusBack ) btn.focus();
	};
	btn.addEventListener( 'click', () => setOpen( list.hidden ) );
	document.addEventListener( 'keydown', ( e ) => {
		if ( e.key === 'Escape' && ! list.hidden ) setOpen( false, true );
	} );
	document.addEventListener( 'click', ( e ) => {
		if ( ! list.hidden && ! lang.contains( e.target ) ) setOpen( false );
	} );
	lang.addEventListener( 'focusout', ( e ) => {
		if ( ! lang.contains( e.relatedTarget ) ) setOpen( false );
	} );
} )();
