import { bgLayerAssets } from './bgLayers';
import { splashLayerAssets } from './splashLayers';

// Every asset here is original to Dumpster Duke (no web-sdk sample assets).
// preload: only what the loading screen shows (base background, UI sheet, font), so it
// appears at once; everything else loads behind it and drives the loading bar.
export default {
	bg_base_landscape: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/bg_base_landscape.webp', import.meta.url).href,
		preload: true,
	},
	bg_base_portrait: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/bg_base_portrait.webp', import.meta.url).href,
		preload: true,
	},
	bg_raid_landscape: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/bg_raid_landscape.webp', import.meta.url).href,
		preload: false,
	},
	bg_raid_portrait: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/bg_raid_portrait.webp', import.meta.url).href,
		preload: false,
	},
	// moving parts of the bonus splashes (art/make_splash_layers.py) and backgrounds (make_bg_layers.py)
	...splashLayerAssets,
	...bgLayerAssets,
	// bonus splashes: Haunted Raid, Super Bonus, Mystery Bonus intros and the raid-complete outro
	fs_raid_landscape: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_raid_landscape.webp', import.meta.url).href,
		preload: false,
	},
	fs_raid_portrait: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_raid_portrait.webp', import.meta.url).href,
		preload: false,
	},
	fs_super_landscape: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_super_landscape.webp', import.meta.url).href,
		preload: false,
	},
	fs_super_portrait: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_super_portrait.webp', import.meta.url).href,
		preload: false,
	},
	fs_mystery_landscape: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_mystery_landscape.webp', import.meta.url).href,
		preload: false,
	},
	fs_mystery_portrait: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_mystery_portrait.webp', import.meta.url).href,
		preload: false,
	},
	fs_outro_landscape: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_outro_landscape.webp', import.meta.url).href,
		preload: false,
	},
	fs_outro_portrait: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_outro_portrait.webp', import.meta.url).href,
		preload: false,
	},
	// full DUMPSTER DUKE logo (the Duke on his sign) for the intro screen
	duke_logo: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeLogo/duke_logo.webp', import.meta.url).href,
		preload: false,
	},
	dukeUi: {
		type: 'sprites',
		src: new URL('../../assets/sprites/dukeUi/dukeUi.json', import.meta.url).href,
		preload: true,
	},
	dukeSymbols: {
		type: 'sprites',
		src: new URL('../../assets/sprites/dukeSymbols/dukeSymbols.json', import.meta.url).href,
		preload: false,
	},
	goldFont: {
		type: 'font',
		src: new URL('../../assets/fonts/goldFont/duke_gold.xml', import.meta.url).href,
		preload: true, // the loading screen uses it
	},
	sound: {
		type: 'audio',
		src: new URL('../../assets/audio/sounds.json', import.meta.url).href,
		preload: false,
	},
} as const;
