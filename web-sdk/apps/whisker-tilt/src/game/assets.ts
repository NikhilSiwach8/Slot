// Every asset here is original to Whisker Tilt (built by art/whisker_tilt/build_web_assets.py).
// Paths are written out in full: Vite only rewrites literal `new URL(...)` paths.
const sprite = (src: string) => ({ type: 'sprite' as const, src, preload: true });

export default {
	bg_base_landscape: sprite(new URL('../../assets/sprites/wtBackgrounds/bg_base_landscape.webp', import.meta.url).href),
	bg_base_portrait: sprite(new URL('../../assets/sprites/wtBackgrounds/bg_base_portrait.webp', import.meta.url).href),
	bg_snowday_landscape: sprite(new URL('../../assets/sprites/wtBackgrounds/bg_snowday_landscape.webp', import.meta.url).href),
	bg_snowday_portrait: sprite(new URL('../../assets/sprites/wtBackgrounds/bg_snowday_portrait.webp', import.meta.url).href),
	bg_super_landscape: sprite(new URL('../../assets/sprites/wtBackgrounds/bg_super_landscape.webp', import.meta.url).href),
	bg_super_portrait: sprite(new URL('../../assets/sprites/wtBackgrounds/bg_super_portrait.webp', import.meta.url).href),
	// the free-spin intro splash reuses the Snow Day scene
	fs_splash_landscape: sprite(new URL('../../assets/sprites/wtBackgrounds/bg_snowday_landscape.webp', import.meta.url).href),
	fs_splash_portrait: sprite(new URL('../../assets/sprites/wtBackgrounds/bg_snowday_portrait.webp', import.meta.url).href),
	keeper_south: sprite(new URL('../../assets/sprites/wtProps/keeper_south.webp', import.meta.url).href),
	keeper_west: sprite(new URL('../../assets/sprites/wtProps/keeper_west.webp', import.meta.url).href),
	keeper_north: sprite(new URL('../../assets/sprites/wtProps/keeper_north.webp', import.meta.url).href),
	keeper_east: sprite(new URL('../../assets/sprites/wtProps/keeper_east.webp', import.meta.url).href),
	mitten: sprite(new URL('../../assets/sprites/wtProps/mitten.webp', import.meta.url).href),
	mitten_paw: sprite(new URL('../../assets/sprites/wtProps/mitten_paw.webp', import.meta.url).href),
	box_frame: sprite(new URL('../../assets/sprites/wtProps/box_frame.webp', import.meta.url).href),
	gift_closed: sprite(new URL('../../assets/sprites/wtProps/gift_closed.webp', import.meta.url).href),
	gift_open: sprite(new URL('../../assets/sprites/wtProps/gift_open.webp', import.meta.url).href),
	crack_overlay: sprite(new URL('../../assets/sprites/wtProps/crack_overlay.webp', import.meta.url).href),
	logo_plate: sprite(new URL('../../assets/sprites/wtProps/logo_plate.webp', import.meta.url).href),
	dukeUi: {
		// UI frames keep their Dumpster Duke names (ui_btn_spin.png, ...) in the recoloured sheet
		type: 'sprites',
		src: new URL('../../assets/sprites/wtUi/wtUi.json', import.meta.url).href,
		preload: true,
	},
	wtSymbols: {
		type: 'sprites',
		src: new URL('../../assets/sprites/wtSymbols/wtSymbols.json', import.meta.url).href,
		preload: true,
	},
	goldFont: {
		type: 'font',
		src: new URL('../../assets/fonts/goldFont/duke_gold.xml', import.meta.url).href,
		preload: true, // the loading screen uses it
	},
	sound: {
		type: 'audio',
		src: new URL('../../assets/audio/sounds.json', import.meta.url).href,
		preload: true,
	},
} as const;
