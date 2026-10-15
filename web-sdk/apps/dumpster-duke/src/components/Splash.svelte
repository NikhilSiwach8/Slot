<!-- A full-screen bonus splash covering the canvas. The art has a blank plaque; the
     children snippet gets its rectangle in canvas px to draw the spin count / win on. -->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { plaqueOnCanvas, SPLASH_IMAGE, type Rect, type SplashName } from '../game/splashes';

	type Props = { name: SplashName; children?: Snippet<[{ plaque: Rect }]> };
	const props: Props = $props();

	const context = getContext();
	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const portrait = $derived(canvas.width / canvas.height < 1);
	const image = $derived(portrait ? SPLASH_IMAGE.portrait : SPLASH_IMAGE.landscape);
	const scale = $derived(Math.max(canvas.width / image.w, canvas.height / image.h));
	const plaque = $derived(plaqueOnCanvas(props.name, canvas));
</script>

<Sprite
	key={`fs_${props.name}_${portrait ? 'portrait' : 'landscape'}`}
	anchor={0.5}
	x={canvas.width / 2}
	y={canvas.height / 2}
	width={image.w * scale}
	height={image.h * scale}
/>
{@render props.children?.({ plaque })}
