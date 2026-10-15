<!-- A full-screen image that covers the canvas, picking the landscape or portrait
     version of a background by the canvas shape (the art is 3:2 and 2:3). -->
<script lang="ts">
	import { Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';

	type Props = { name: string };
	const props: Props = $props();

	const context = getContext();
	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const portrait = $derived(canvas.width / canvas.height < 1);
	const image = $derived(portrait ? { w: 1024, h: 1536 } : { w: 1536, h: 1024 });
	const scale = $derived(Math.max(canvas.width / image.w, canvas.height / image.h));
</script>

<Sprite
	key={`${props.name}_${portrait ? 'portrait' : 'landscape'}`}
	anchor={0.5}
	x={canvas.width / 2}
	y={canvas.height / 2}
	width={image.w * scale}
	height={image.h * scale}
/>
