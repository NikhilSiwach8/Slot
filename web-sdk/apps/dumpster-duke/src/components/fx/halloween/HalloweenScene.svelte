<!-- Halloween atmosphere over the background art (behind the reels): a dark purple vignette,
     drifting fog and rising sparks. `layer="front"` draws the bats instead (above the reels). -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { Graphics } from 'pixi-svelte';

	import { getContext } from '../../../game/context';
	import Fog from './Fog.svelte';
	import Embers from './Embers.svelte';
	import Bats from './Bats.svelte';

	type Props = { layer?: 'back' | 'front' };
	const props: Props = $props();
	const context = getContext();
	const canvas = $derived(context.stateLayoutDerived.canvasSizes());

	const drawVignette = (g: PIXI.Graphics) => {
		const { width: w, height: h } = canvas;
		const steps = 14;
		for (let i = 0; i < steps; i++) {
			const inset = (i / steps) * Math.min(w, h) * 0.35;
			g.rect(inset, inset, w - inset * 2, h - inset * 2).stroke({
				color: 0x14061f,
				width: Math.min(w, h) * 0.35 / steps + 1,
				alpha: 0.075 * (1 - i / steps),
				alignment: 1,
			});
		}
		// a cold moonlit wash from the top
		g.rect(0, 0, w, h * 0.35).fill({ color: 0x3b2a7a, alpha: 0.12 });
	};
</script>

{#if (props.layer ?? 'back') === 'back'}
	<Graphics draw={drawVignette} />
	<Fog width={canvas.width} height={canvas.height} alpha={0.55} />
	<Embers width={canvas.width} height={canvas.height} />
{:else}
	<Bats width={canvas.width} height={canvas.height} />
{/if}
