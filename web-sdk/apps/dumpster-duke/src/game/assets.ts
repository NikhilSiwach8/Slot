// Every asset here is original to Dumpster Duke (no web-sdk sample assets).
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
		preload: true,
	},
	bg_raid_portrait: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/bg_raid_portrait.webp', import.meta.url).href,
		preload: true,
	},
	fs_splash_landscape: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_splash_landscape.webp', import.meta.url).href,
		preload: true,
	},
	fs_splash_portrait: {
		type: 'sprite',
		src: new URL('../../assets/sprites/dukeBackgrounds/fs_splash_portrait.webp', import.meta.url).href,
		preload: true,
	},
	dukeUi: {
		type: 'sprites',
		src: new URL('../../assets/sprites/dukeUi/dukeUi.json', import.meta.url).href,
		preload: true,
	},
	dukeSymbols: {
		type: 'sprites',
		src: new URL('../../assets/sprites/dukeSymbols/dukeSymbols.json', import.meta.url).href,
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
