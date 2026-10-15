// URL of a file in static/assets, resolved against the page (index.html) so it works
// wherever the game folder is hosted. (new URL('../../../assets/…', import.meta.url) from a
// file nested three folders deep climbs one level above the game folder once bundled,
// which only happens to work when the game is served from the site root.)
export const staticAsset = (path: string) =>
	typeof document === 'undefined' ? `./assets/${path}` : new URL(`assets/${path}`, document.baseURI).href;
