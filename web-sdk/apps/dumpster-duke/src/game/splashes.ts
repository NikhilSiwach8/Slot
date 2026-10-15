// Full-screen bonus splashes (built by art/make_fs_splashes.py from 2:3 portrait art,
// placed full height and centred in a 1920x1080 / 1080x1440 image over a blurred fill).
import { stateBet } from 'state-shared';

export type SplashName = 'raid' | 'super' | 'mystery' | 'outro';
export type Rect = { x: number; y: number; width: number; height: number };

/** The blank plaque on each piece of art, as fractions of the 2:3 art (x, y = centre). */
export const SPLASH_PLAQUE: Record<SplashName, Rect> = {
	raid: { x: 0.503, y: 0.482, width: 0.498, height: 0.078 },
	super: { x: 0.503, y: 0.557, width: 0.537, height: 0.085 },
	mystery: { x: 0.503, y: 0.814, width: 0.615, height: 0.091 },
	outro: { x: 0.503, y: 0.651, width: 0.596, height: 0.117 },
};

const ART_ASPECT = 2 / 3;
export const SPLASH_IMAGE = { landscape: { w: 1920, h: 1080 }, portrait: { w: 1080, h: 1440 } };

/** Which intro splash the current bonus gets (bet mode stays set for the whole round). */
export const introSplash = (): SplashName => {
	const mode = stateBet.activeBetModeKey.toUpperCase();
	if (mode === 'SUPER') return 'super';
	if (mode === 'MYSTERY') return 'mystery';
	return 'raid';
};

/** Where a splash's plaque lands on a canvas the image covers (see Splash.svelte). */
export const plaqueOnCanvas = (name: SplashName, canvas: { width: number; height: number }): Rect => {
	const portrait = canvas.width / canvas.height < 1;
	const image = portrait ? SPLASH_IMAGE.portrait : SPLASH_IMAGE.landscape;
	const scale = Math.max(canvas.width / image.w, canvas.height / image.h);
	const artWidth = image.h * ART_ASPECT;
	const plaque = SPLASH_PLAQUE[name];
	return {
		x: canvas.width / 2 + (plaque.x - 0.5) * artWidth * scale,
		y: canvas.height / 2 + (plaque.y - 0.5) * image.h * scale,
		width: plaque.width * artWidth * scale,
		height: plaque.height * image.h * scale,
	};
};
