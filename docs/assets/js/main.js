/**
 * Orbita: comportamiento de la cabecera y animaciones de entrada.
 *
 * Reproduce los patrones observados en el estudio:
 *  - flyouts de la navegación global (hover con retardo, foco, Escape, aria-expanded, fondo difuminado)
 *  - evento de cambio de breakpoint (S ≤734, M 735–1068, L ≥1069) en document
 *  - aparición de los bloques al entrar en viewport
 */
( () => {
	const doc = document.documentElement;
	const nav = document.getElementById( 'ob-globalnav' );
	const menu = document.getElementById( 'ob-menu' );
	const BREAKPOINTS = {
		small: '(max-width: 734px)',
		medium: '(min-width: 735px) and (max-width: 1068px)',
		large: '(min-width: 1069px)',
	};
	const isSmall = () => window.matchMedia( BREAKPOINTS.small ).matches;

	/* ---------- Flyouts ---------- */
	if ( nav && menu ) {
		const items = Array.from( menu.querySelectorAll( ':scope > li.menu-item-has-children' ) );
		let openItem = null;
		let timer = 0;

		const close = ( item ) => {
			if ( ! item ) return;
			item.classList.remove( 'is-open' );
			item.querySelector( '.ob-menu__toggle' )?.setAttribute( 'aria-expanded', 'false' );
			if ( openItem === item ) openItem = null;
			if ( ! openItem ) doc.classList.remove( 'flyout-open' );
		};
		const open = ( item ) => {
			if ( openItem && openItem !== item ) close( openItem );
			item.classList.add( 'is-open' );
			item.querySelector( '.ob-menu__toggle' )?.setAttribute( 'aria-expanded', 'true' );
			openItem = item;
			if ( ! isSmall() ) doc.classList.add( 'flyout-open' );
		};

		items.forEach( ( item ) => {
			const toggle = item.querySelector( '.ob-menu__toggle' );

			toggle?.addEventListener( 'click', () => ( item.classList.contains( 'is-open' ) ? close( item ) : open( item ) ) );

			item.addEventListener( 'mouseenter', () => {
				if ( isSmall() ) return;
				clearTimeout( timer );
				timer = setTimeout( () => open( item ), openItem ? 0 : 120 );
			} );
			item.addEventListener( 'mouseleave', () => {
				if ( isSmall() ) return;
				clearTimeout( timer );
				timer = setTimeout( () => close( item ), 200 );
			} );
			item.addEventListener( 'focusout', ( e ) => {
				if ( ! item.contains( e.relatedTarget ) ) close( item );
			} );
		} );

		document.addEventListener( 'keydown', ( e ) => {
			if ( e.key !== 'Escape' ) return;
			if ( openItem ) {
				const toggle = openItem.querySelector( '.ob-menu__toggle' );
				close( openItem );
				toggle?.focus();
			}
			if ( doc.classList.contains( 'menu-open' ) ) setMobileMenu( false );
		} );

		document.querySelector( '.ob-backdrop' )?.addEventListener( 'click', () => close( openItem ) );

		/* Menú móvil */
		const trigger = nav.querySelector( '.ob-menu-trigger' );
		const setMobileMenu = ( state ) => {
			doc.classList.toggle( 'menu-open', state );
			trigger?.setAttribute( 'aria-expanded', String( state ) );
			document.body.style.overflow = state ? 'hidden' : '';
		};
		trigger?.addEventListener( 'click', () => setMobileMenu( ! doc.classList.contains( 'menu-open' ) ) );

		document.addEventListener( 'orbita:breakpointchange', () => {
			close( openItem );
			if ( ! isSmall() ) setMobileMenu( false );
		} );
	}

	/* ---------- Búsqueda ---------- */
	const searchBtn = document.querySelector( '[data-ob-search]' );
	const searchForm = document.getElementById( 'ob-search' );
	searchBtn?.addEventListener( 'click', () => {
		searchForm?.classList.toggle( 'screen-reader-text' );
		searchForm?.querySelector( 'input' )?.focus();
	} );

	/* ---------- Evento de cambio de breakpoint ---------- */
	Object.entries( BREAKPOINTS ).forEach( ( [ name, query ] ) => {
		window.matchMedia( query ).addEventListener( 'change', ( e ) => {
			if ( e.matches ) {
				document.dispatchEvent( new CustomEvent( 'orbita:breakpointchange', { detail: { name, query } } ) );
			}
		} );
	} );

	/* ---------- Aparición al hacer scroll ---------- */
	const revealables = document.querySelectorAll( '.ob-reveal' );
	if ( ! ( 'IntersectionObserver' in window ) || window.matchMedia( '(prefers-reduced-motion: reduce)' ).matches ) {
		revealables.forEach( ( el ) => el.classList.add( 'is-visible' ) );
		return;
	}
	const io = new IntersectionObserver(
		( entries ) => {
			entries.forEach( ( entry ) => {
				if ( entry.isIntersecting ) {
					entry.target.classList.add( 'is-visible' );
					io.unobserve( entry.target );
				}
			} );
		},
		{ rootMargin: '0px 0px -10% 0px', threshold: 0.15 }
	);
	revealables.forEach( ( el ) => io.observe( el ) );
} )();
