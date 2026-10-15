<!-- A piece of Dumpster Duke UI art (from art/slice_ui.py), fitted inside a box
     without distortion unless `stretch` is set. -->
<script lang="ts" module>
	import artSizes from '../artSizes.json';

	export type ArtName = keyof typeof artSizes;
</script>

<script lang="ts">
	import { Sprite } from 'pixi-svelte';

	type Props = {
		name: ArtName;
		width: number;
		height: number;
		x?: number;
		y?: number;
		stretch?: boolean;
		tint?: number;
		alpha?: number;
	};

	const props: Props = $props();
	const natural = $derived(artSizes[props.name]);
	const fit = $derived(Math.min(props.width / natural.width, props.height / natural.height));
</script>

<Sprite
	key={`ui_${props.name}.png`}
	anchor={0.5}
	x={props.x ?? 0}
	y={props.y ?? 0}
	width={props.stretch ? props.width : natural.width * fit}
	height={props.stretch ? props.height : natural.height * fit}
	tint={props.tint ?? 0xffffff}
	alpha={props.alpha ?? 1}
/>
