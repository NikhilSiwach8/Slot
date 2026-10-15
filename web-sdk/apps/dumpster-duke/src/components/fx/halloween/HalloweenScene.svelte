<!-- Halloween atmosphere. layer "back" (behind the reels): dark purple vignette, fog banks over
     the whole screen plus thick ground fog, drifting ghosts and rising sparks. layer "front"
     (over the reels, under the HUD): a thin fog veil kept light so symbols stay readable, bats
     and the odd lightning flicker. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { Graphics } from 'pixi-svelte';

	import { getContext } from '../../../game/context';
	import Fog from './Fog.svelte';
	import Embers from './Embers.svelte';
	import Bats from './Bats.svelte';
	import Ghosts from './Ghosts.svelte';
	import Lightning from './Lightning.svelte';

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
	<Fog width={canvas.width} height={canvas.height} variant="full" alpha={0.9} />
	<Ghosts width={canvas.width} height={canvas.height} />
	<Fog width={canvas.width} height={canvas.height} variant="ground" alpha={0.9} />
	<Embers width={canvas.width} height={canvas.height} />
{:else}
	<Fog width={canvas.width} height={canvas.height} variant="veil" alpha={0.55} />
	<Bats width={canvas.width} height={canvas.height} />
	<Lightning width={canvas.width} height={canvas.height} />
{/if}
