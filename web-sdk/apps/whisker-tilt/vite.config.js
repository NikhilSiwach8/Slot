// @ts-ignore
import config from 'config-vite';
import { mergeConfig } from 'vite';
import { fileURLToPath } from 'node:url';

export default mergeConfig(config(), {
	resolve: {
		alias: {
			// no external font loading (Typekit) — see src/webfontloader-local.js
			webfontloader: fileURLToPath(new URL('./src/webfontloader-local.js', import.meta.url)),
		},
	},
});
