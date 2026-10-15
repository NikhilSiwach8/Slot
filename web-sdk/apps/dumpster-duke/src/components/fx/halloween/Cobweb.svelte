<!-- A corner cobweb with a little spider bobbing on its thread. Drawn from the corner at
     (0, 0) into +x/+y; flip with scale to put it in other corners. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';

	import { createClock } from '../timeline.svelte';

	type Props = { size: number; spider?: boolean };
	const props: Props = $props();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const SPOKES = 6;
	const angle = (k: number) => (k / (SPOKES - 1)) * (Math.PI / 2);
	const drawWeb = (g: PIXI.Graphics) => {
		const r = props.size;
		for (let k = 0; k < SPOKES; k++) g.moveTo(0, 0).lineTo(Math.cos(angle(k)) * r, Math.sin(angle(k)) * r);
		g.stroke({ color: 0xe8e4f0, width: 2, alpha: 0.55 });
		for (const ring of [0.25, 0.45, 0.65, 0.85]) {
			for (let k = 0; k < SPOKES - 1; k++) {
				const a = angle(k);
				const b = angle(k + 1);
				const sag = ring * r * 0.82;
				g.moveTo(Math.cos(a) * ring * r, Math.sin(a) * ring * r).quadraticCurveTo(
					Math.cos((a + b) / 2) * sag,
					Math.sin((a + b) / 2) * sag,
					Math.cos(b) * ring * r,
					Math.sin(b) * ring * r,
				);
			}
		}
		g.stroke({ color: 0xe8e4f0, width: 1.5, alpha: 0.45 });
	};
	const drop = $derived(props.size * (0.75 + 0.12 * Math.sin(clock.seconds * 1.4)));
	const drawSpider = (g: PIXI.Graphics) => {
		const s = props.size / 120;
		for (const side of [-1, 1]) {
			for (const k of [0, 1, 2, 3]) {
				g.moveTo(0, 0).lineTo(side * 9 * s, (-4 + k * 3) * s).lineTo(side * 14 * s, (2 + k * 4) * s);
			}
		}
		g.stroke({ color: 0x120a1c, width: 2 * s });
		g.circle(0, 0, 6 * s).fill(0x120a1c);
		g.circle(0, -7 * s, 4 * s).fill(0x120a1c);
		g.circle(-1.5 * s, -8 * s, 1 * s).fill(0xff3b3b);
		g.circle(1.5 * s, -8 * s, 1 * s).fill(0xff3b3b);
	};
</script>

<Graphics draw={drawWeb} />
{#if props.spider}
	{@const x = props.size * 0.55}
	<Graphics draw={(g: PIXI.Graphics) => g.moveTo(x, props.size * 0.2).lineTo(x, drop).stroke({ color: 0xe8e4f0, width: 1, alpha: 0.6 })} />
	<Container {x} y={drop}>
		<Graphics draw={drawSpider} />
	</Container>
{/if}
