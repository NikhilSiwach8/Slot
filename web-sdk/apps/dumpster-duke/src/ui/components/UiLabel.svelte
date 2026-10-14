<script lang="ts">
	import { BitmapText, Text } from 'pixi-svelte';
	import { WHITE } from 'constants-shared/colors';

	import UiArt from './UiArt.svelte';
	import { UI_BASE_FONT_SIZE } from '../constants';

	type Props = {
		label: string;
		value: string;
		tiled?: boolean;
		stacked?: boolean;
	};

	const props: Props = $props();

	const labelStyle = { fontFamily: 'gold', fontSize: UI_BASE_FONT_SIZE * 0.8 } as const;
	const valueStyle = {
		fontFamily: 'Arial Black, Arial, sans-serif',
		fontWeight: '900',
		fontSize: UI_BASE_FONT_SIZE,
		fill: WHITE,
	} as const;
	// the dark bet panel from the art sheet, stretched a little to fit long amounts
	const PANEL = { width: UI_BASE_FONT_SIZE * 7, height: UI_BASE_FONT_SIZE * 2.7 };
</script>

{#if props.stacked}
	{#if props.tiled}
		<UiArt name="bar_panel" stretch width={PANEL.width} height={PANEL.height} y={UI_BASE_FONT_SIZE * 0.95} />
	{/if}
	<BitmapText anchor={{ x: 0.5, y: 0 }} text={props.label.toUpperCase()} style={labelStyle} />
	<Text anchor={{ x: 0.5, y: 0 }} text={props.value} style={valueStyle} y={UI_BASE_FONT_SIZE * 0.85} />
{:else}
	{#if props.tiled}
		<UiArt
			name="bar_panel"
			stretch
			width={UI_BASE_FONT_SIZE * 12}
			height={UI_BASE_FONT_SIZE * 2}
			x={UI_BASE_FONT_SIZE * 5}
		/>
	{/if}
	<BitmapText anchor={{ x: 0, y: 0.5 }} text={props.label.toUpperCase()} style={labelStyle} />
	<Text anchor={{ x: 1, y: 0.5 }} text={props.value} style={valueStyle} x={UI_BASE_FONT_SIZE * 10} />
{/if}
