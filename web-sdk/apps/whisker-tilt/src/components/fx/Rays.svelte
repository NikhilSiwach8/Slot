<!-- Slowly rotating golden light rays behind big moments. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { Graphics } from 'pixi-svelte';

	import { createClock } from './timeline.svelte';

	type Props = { radius: number; x?: number; y?: number; alpha?: number; count?: number; colour?: number };
	const props: Props = $props();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const count = props.count ?? 14;
	const draw = (g: PIXI.Graphics) => {
		const r = props.radius;
		const half = Math.PI / count / 2;
		for (let i = 0; i < count; i++) {
			const a = (i / count) * Math.PI * 2;
			g.poly([0, 0, Math.cos(a - half) * r, Math.sin(a - half) * r, Math.cos(a + half) * r, Math.sin(a + half) * r])
				.fill({ color: props.colour ?? 0xffc84a, alpha: 0.22 });
		}
		g.circle(0, 0, r * 0.35).fill({ color: props.colour ?? 0xffc84a, alpha: 0.25 });
	};
</script>

<Graphics
	x={props.x ?? 0}
	y={props.y ?? 0}
	rotation={clock.seconds * 0.35}
	alpha={props.alpha ?? 1}
	blendMode="add"
	{draw}
/>
