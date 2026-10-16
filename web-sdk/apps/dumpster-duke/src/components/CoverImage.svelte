<!-- A full-screen image that covers the canvas, picking the landscape or portrait
     version of a Dumpster Duke background by the canvas shape. The mine backgrounds
     (bg_base, bg_raid) loop small animations on parts cut out by art/make_bg_layers.py:
     lanterns sway on their chains and flicker, crystals pulse, the gold in the cart
     shimmers and the tunnel's far exit breathes. -->
<script lang="ts">
	import { onDestroy } from 'svelte';
	import { Container, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BG_LAYERS } from '../game/bgLayers';
	import { nightGrade } from './fx/halloween/grade';
	import { createClock } from './fx/timeline.svelte';

	type Props = { name: string };
	const props: Props = $props();

	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const portrait = $derived(canvas.width / canvas.height < 1);
	const orientation = $derived(portrait ? 'portrait' : 'landscape');
	const image = $derived(portrait ? { w: 1080, h: 1440 } : { w: 1920, h: 1080 });
	const scale = $derived(Math.max(canvas.width / image.w, canvas.height / image.h));
	const variant = $derived(props.name === 'bg_base' ? 'base' : props.name === 'bg_raid' ? 'raid' : undefined);
	const t = $derived(clock.seconds);

	// motion of one part; offsets in image px, phase-shifted per part
	const motion = (anim: string, ph: number) => {
		switch (anim) {
			case 'lantern': {
				const flicker = Math.abs(Math.sin(t * 11 + ph) * Math.sin(t * 6.7 + ph * 2));
				return { rotation: Math.sin(t * 1.1 + ph) * 0.045, scale: 1, glow: 0.18 + flicker * 0.35 };
			}
			case 'crystal':
				return { rotation: 0, scale: 1 + Math.sin(t * 1.6 + ph) * 0.02, glow: 0.12 + (Math.sin(t * 1.6 + ph) + 1) * 0.16 };
			case 'gold': {
				// a sheen sweeping over the gold every few seconds
				const p = (t % 4.5) / 4.5;
				return { rotation: 0, scale: 1, glow: 0.08 + Math.max(0, 1 - Math.abs(p - 0.25) / 0.12) * 0.35 };
			}
			case 'portal':
				return { rotation: 0, scale: 1 + Math.sin(t * 0.8) * 0.04, glow: 0.15 + (Math.sin(t * 0.8) + 1) * 0.15 };
		}
		return { rotation: 0, scale: 1, glow: 0 };
	};
</script>

<Container x={canvas.width / 2} y={canvas.height / 2} scale={scale} filters={[nightGrade]}>
	<Sprite key={`${props.name}_${orientation}`} anchor={0.5} width={image.w} height={image.h} />
	{#if variant}
		{#each BG_LAYERS[orientation] as layer, i}
			{@const m = motion(layer.anim, i * 1.9)}
			{@const key = `bg_${variant}_${orientation}_${layer.id}`}
			<Container x={(layer.px - 0.5) * image.w} y={(layer.py - 0.5) * image.h} rotation={m.rotation} scale={m.scale}>
				<Sprite
					{key}
					anchor={0.5}
					x={(layer.x - layer.px) * image.w}
					y={(layer.y - layer.py) * image.h}
					width={layer.w * image.w}
					height={layer.h * image.h}
				/>
				<Sprite
					{key}
					anchor={0.5}
					x={(layer.x - layer.px) * image.w}
					y={(layer.y - layer.py) * image.h}
					width={layer.w * image.w}
					height={layer.h * image.h}
					alpha={m.glow}
					blendMode="add"
				/>
			</Container>
		{/each}
	{/if}
</Container>
