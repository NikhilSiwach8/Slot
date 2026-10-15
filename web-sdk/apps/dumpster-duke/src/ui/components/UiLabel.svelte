<!--
	HUD amount label: a small gold-framed tag with the name ("BALANCE", "BET", "WIN") and the
	amount underneath in big white type with a dark outline, so it reads on any background.
	`stacked` puts the amount under the tag (default HUD); otherwise tag and amount sit side by side.
-->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { BitmapText, Graphics, Text } from 'pixi-svelte';
	import { WHITE } from 'constants-shared/colors';

	import { socialText } from '../../game/social';
	import { UI_BASE_FONT_SIZE } from '../constants';

	type Props = {
		label: string;
		value: string;
		/** kept for API compatibility; the tag style has no separate panel */
		tiled?: boolean;
		stacked?: boolean;
	};

	const props: Props = $props();

	const TAG_FONT = UI_BASE_FONT_SIZE * 0.72;
	const TAG_H = TAG_FONT * 1.5;
	const text = $derived(socialText(props.label).toUpperCase());
	const tagWidth = $derived(text.length * TAG_FONT * 0.64 + TAG_FONT * 1.4);
	const valueStyle = {
		fontFamily: 'Arial Black, Arial, sans-serif',
		fontWeight: '900',
		fontSize: UI_BASE_FONT_SIZE * 1.2,
		fill: WHITE,
		stroke: { color: 0x1a0b06, width: UI_BASE_FONT_SIZE * 0.2, join: 'round' },
		dropShadow: { color: 0x000000, alpha: 0.5, distance: 3, blur: 2, angle: Math.PI / 2 },
	} as const;

	const drawTag = (g: PIXI.Graphics) => {
		g.roundRect(-tagWidth / 2, -TAG_H / 2, tagWidth, TAG_H, TAG_H * 0.32)
			.fill(0x1d1033)
			.stroke({ color: 0xf2b33d, width: 3 });
	};
</script>

{#if props.stacked}
	<Graphics draw={drawTag} y={TAG_H / 2} />
	<BitmapText anchor={0.5} y={TAG_H / 2} {text} style={{ fontFamily: 'gold', fontSize: TAG_FONT }} />
	<Text anchor={{ x: 0.5, y: 0 }} text={props.value} style={valueStyle} y={TAG_H * 1.05} />
{:else}
	<Graphics draw={drawTag} x={tagWidth / 2} />
	<BitmapText anchor={0.5} x={tagWidth / 2} {text} style={{ fontFamily: 'gold', fontSize: TAG_FONT }} />
	<Text anchor={{ x: 0, y: 0.5 }} text={props.value} style={valueStyle} x={tagWidth + UI_BASE_FONT_SIZE * 0.4} />
{/if}
