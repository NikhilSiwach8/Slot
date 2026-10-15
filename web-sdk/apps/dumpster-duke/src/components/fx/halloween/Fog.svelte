<!-- Drifting fog: soft blobs (stacked translucent circles, no filter pass) in layers that
     slide sideways at different speeds, breathe slowly and wrap around the screen.
     variant "ground": thick fog along the bottom. "full": banks across the whole height.
     "veil": thin wisps meant to drift in front of the reels. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';

	import { createClock } from '../timeline.svelte';

	type Props = { width: number; height: number; alpha?: number; variant?: 'ground' | 'full' | 'veil' };
	const props: Props = $props();
	const clock = createClock();
	onDestroy(() => clock.stop());

	type Layer = { y: number; size: number; speed: number; color: number; count: number };
	const VARIANTS: Record<string, Layer[]> = {
		ground: [
			{ y: 0.9, size: 0.2, speed: 9, color: 0x8a6bc4, count: 9 },
			{ y: 0.8, size: 0.15, speed: -14, color: 0x6fa58a, count: 10 },
			{ y: 0.97, size: 0.25, speed: 5, color: 0xb59ae0, count: 7 },
		],
		full: [
			{ y: 0.12, size: 0.14, speed: -6, color: 0x7d63b8, count: 8 },
			{ y: 0.32, size: 0.16, speed: 8, color: 0x6a8fb0, count: 8 },
			{ y: 0.52, size: 0.17, speed: -11, color: 0x8a6bc4, count: 9 },
			{ y: 0.72, size: 0.18, speed: 7, color: 0x6fa58a, count: 9 },
		],
		veil: [
			{ y: 0.3, size: 0.12, speed: 12, color: 0xcfc2ee, count: 6 },
			{ y: 0.62, size: 0.14, speed: -9, color: 0xb9d8c8, count: 6 },
			{ y: 0.86, size: 0.16, speed: 15, color: 0xcfc2ee, count: 7 },
		],
	};
	const LAYERS = VARIANTS[props.variant ?? 'ground'];

	const blobs = (layer: Layer, w: number, h: number) => (g: PIXI.Graphics) => {
		for (let i = 0; i < layer.count; i++) {
			const x = (i + 0.5) * (w / layer.count) + Math.sin(i * 7.3) * w * 0.03;
			const y = Math.cos(i * 3.1) * h * 0.03;
			const r = h * layer.size * (0.75 + 0.5 * Math.abs(Math.sin(i * 1.7)));
			for (let k = 6; k >= 1; k--) g.ellipse(x, y, r * (k / 6) * 1.8, r * (k / 6)).fill({ color: layer.color, alpha: 0.045 });
		}
	};
</script>

<Container alpha={props.alpha ?? 1}>
	{#each LAYERS as layer}
		{@const offset = ((clock.seconds * layer.speed) % props.width + props.width) % props.width}
		{#each [offset - props.width, offset] as x}
			<Graphics
				{x}
				y={props.height * layer.y + Math.sin(clock.seconds * 0.25 + layer.y * 9) * props.height * 0.02}
				alpha={0.75 + 0.25 * Math.sin(clock.seconds * 0.4 + layer.y * 13)}
				draw={blobs(layer, props.width, props.height)}
			/>
		{/each}
	{/each}
</Container>
