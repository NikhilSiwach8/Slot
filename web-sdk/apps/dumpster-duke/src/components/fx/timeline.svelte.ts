// Tiny rAF animation clocks for code-driven effects.
export const easeOutBack = (u: number, s = 1.70158) => 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2;
export const easeOutCubic = (u: number) => 1 - (1 - u) ** 3;
export const easeInCubic = (u: number) => u ** 3;
export const clamp01 = (u: number) => Math.max(0, Math.min(1, u));

/** Seconds since creation, updated every animation frame (reactive). Call stop() on destroy. */
export const createClock = () => {
	let seconds = $state(0);
	const start = performance.now();
	let frame = requestAnimationFrame(function step(now) {
		seconds = (now - start) / 1000;
		frame = requestAnimationFrame(step);
	});
	return {
		get seconds() {
			return seconds;
		},
		stop: () => cancelAnimationFrame(frame),
	};
};
export type Clock = ReturnType<typeof createClock>;

/** Runs 0 → 1 over `ms` (reactive `t`); `done` resolves at the end. */
export const createTween01 = (ms: number) => {
	let t = $state(0);
	const start = performance.now();
	let frame = 0;
	const done = new Promise<void>((resolve) => {
		frame = requestAnimationFrame(function step(now) {
			t = clamp01((now - start) / ms);
			if (t < 1) frame = requestAnimationFrame(step);
			else resolve();
		});
	});
	return {
		get t() {
			return t;
		},
		done,
		stop: () => cancelAnimationFrame(frame),
	};
};
export type Tween01 = ReturnType<typeof createTween01>;
