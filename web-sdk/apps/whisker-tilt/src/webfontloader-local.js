// Local stand-in for the 'webfontloader' package (wired up via a Vite alias in
// vite.config.js). The shared pixi-svelte package preloads fonts from Adobe
// Typekit, an external origin, which Stake's strict policy forbids. Here we just
// wait for the bundled fonts (see src/fonts.css) and report success.
const FAMILIES = ['proxima-nova', 'Lilita One'];

const load = (config = {}) => {
	const done = () => config.active?.();
	if (typeof document === 'undefined' || !document.fonts) return done();
	Promise.all(FAMILIES.map((family) => document.fonts.load(`1em "${family}"`).catch(() => undefined)))
		.then(done, done);
};

export default { load };
