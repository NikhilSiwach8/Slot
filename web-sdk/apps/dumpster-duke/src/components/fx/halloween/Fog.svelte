<!-- Low drifting fog: soft blobs (stacked translucent circles, no filter pass) in a few
     layers that slide sideways at different speeds and wrap around the screen. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';

	import { createClock } from '../timeline.svelte';

	type Props = { width: number; height: number; alpha?: number };
	const props: Props = $props();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const LAYERS = [
		{ y: 0.9, size: 0.2, speed: 9, color: 0x8a6bc4, count: 9 },
		{ y: 0.8, size: 0.15, speed: -14, color: 0x6fa58a, count: 10 },
		{ y: 0.97, size: 0.25, speed: 5, color: 0xb59ae0, count: 7 },
	];

	const blobs = (layer: (typeof LAYERS)[number], w: number, h: number) => (g: PIXI.Graphics) => {
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
			<Graphics x={x} y={props.height * layer.y} draw={blobs(layer, props.width, props.height)} />
		{/each}
	{/each}
</Container>
