<!-- A carved pumpkin with a flickering candle glow. Centered on (0, 0); `size` is its width. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';

	import { createClock } from '../timeline.svelte';

	type Props = { size: number; seed?: number; x?: number; y?: number; rotation?: number };
	const props: Props = $props();
	const clock = createClock();
	onDestroy(() => clock.stop());
	const seed = props.seed ?? 1;

	const flicker = $derived(
		0.75 + 0.15 * Math.sin(clock.seconds * 13 + seed) + 0.1 * Math.sin(clock.seconds * 31 + seed * 2.7),
	);

	const drawPumpkin = (g: PIXI.Graphics) => {
		const s = props.size / 100;
		// ribs, back to front
		g.ellipse(-26 * s, 4 * s, 30 * s, 38 * s).fill(0xc4560f).stroke({ color: 0x4a1a04, width: 3 * s });
		g.ellipse(26 * s, 4 * s, 30 * s, 38 * s).fill(0xc4560f).stroke({ color: 0x4a1a04, width: 3 * s });
		g.ellipse(-12 * s, 2 * s, 28 * s, 40 * s).fill(0xe8731a).stroke({ color: 0x4a1a04, width: 3 * s });
		g.ellipse(12 * s, 2 * s, 28 * s, 40 * s).fill(0xe8731a).stroke({ color: 0x4a1a04, width: 3 * s });
		g.ellipse(0, 0, 22 * s, 41 * s).fill(0xf58a2a).stroke({ color: 0x4a1a04, width: 3 * s });
		g.ellipse(-6 * s, -18 * s, 6 * s, 12 * s).fill({ color: 0xffd08a, alpha: 0.35 });
		// stem
		g.poly([-5 * s, -36 * s, -2 * s, -52 * s, 8 * s, -56 * s, 6 * s, -48 * s, 5 * s, -36 * s]).fill(0x4f6b1e).stroke({ color: 0x1d2a08, width: 2 * s });
	};
	const drawFace = (g: PIXI.Graphics) => {
		const s = props.size / 100;
		const color = 0xffd34a;
		g.poly([-24 * s, -6 * s, -10 * s, -6 * s, -17 * s, -20 * s]).fill(color);
		g.poly([10 * s, -6 * s, 24 * s, -6 * s, 17 * s, -20 * s]).fill(color);
		g.poly([-3 * s, 2 * s, 3 * s, 2 * s, 0, -5 * s]).fill(color);
		g.poly([
			-28 * s, 8 * s, -20 * s, 14 * s, -14 * s, 9 * s, -8 * s, 16 * s, -2 * s, 10 * s, 4 * s, 17 * s,
			10 * s, 10 * s, 16 * s, 16 * s, 22 * s, 9 * s, 28 * s, 8 * s, 22 * s, 24 * s, 0, 30 * s, -22 * s, 24 * s,
		]).fill(color);
	};
	const drawGlow = (g: PIXI.Graphics) => {
		const s = props.size / 100;
		for (let i = 6; i >= 1; i--) g.circle(0, 6 * s, (40 + i * 14) * s).fill({ color: 0xff8a1a, alpha: 0.05 });
	};
</script>

<Container x={props.x ?? 0} y={props.y ?? 0} rotation={props.rotation ?? 0}>
	<Graphics draw={drawGlow} blendMode="add" alpha={flicker} />
	<Graphics draw={drawPumpkin} />
	<Graphics draw={drawFace} alpha={0.55 + 0.45 * flicker} />
</Container>
