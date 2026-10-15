<!--
	Rounded HUD card in the Dumpster Duke style: dark purple face, thick gold frame on a
	dark-wood edge, soft drop shadow, and an optional name tab on the top edge
	("SPIN", "BONUS"). Drawn in code so it stays crisp at every size. Centered on (0, 0).
-->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { BitmapText, Container, Graphics } from 'pixi-svelte';

	type Props = {
		width: number;
		height: number;
		tab?: string;
		/** "on" state: brighter frame and a warm glow */
		active?: boolean;
		/** lighter face for the small utility buttons */
		face?: number;
	};
	const props: Props = $props();

	const tabFont = $derived(Math.min(props.width, props.height) * 0.16);
	const tabWidth = $derived(props.tab ? props.tab.length * tabFont * 0.62 + tabFont * 1.4 : 0);

	const draw = (g: PIXI.Graphics) => {
		const w = props.width;
		const h = props.height;
		const r = Math.min(w, h) * 0.2;
		const edge = Math.max(4, Math.min(w, h) * 0.05);
		if (props.active) {
			for (let i = 4; i >= 1; i--) {
				g.roundRect(-w / 2 - i * 5, -h / 2 - i * 5, w + i * 10, h + i * 10, r + i * 5).fill({ color: 0xffb02e, alpha: 0.09 });
			}
		}
		// drop shadow
		g.roundRect(-w / 2, -h / 2 + h * 0.05, w, h, r).fill({ color: 0x000000, alpha: 0.45 });
		// dark wood edge + gold frame
		g.roundRect(-w / 2, -h / 2, w, h, r).fill(0x2a1208);
		g.roundRect(-w / 2 + edge * 0.4, -h / 2 + edge * 0.4, w - edge * 0.8, h - edge * 0.8, r * 0.92)
			.stroke({ color: props.active ? 0xffe27a : 0xf2b33d, width: edge * 0.8 });
		// face with a lighter top half for a little volume
		const inset = edge * 1.25;
		g.roundRect(-w / 2 + inset, -h / 2 + inset, w - inset * 2, h - inset * 2, r * 0.75).fill(props.face ?? 0x1d1033);
		g.roundRect(-w / 2 + inset, -h / 2 + inset, w - inset * 2, (h - inset * 2) * 0.45, r * 0.75).fill({ color: 0xffffff, alpha: 0.06 });
		// tab on the top edge
		if (props.tab) {
			const th = tabFont * 1.45;
			g.roundRect(-tabWidth / 2, -h / 2 - th * 0.55, tabWidth, th, th * 0.35)
				.fill(0x1d1033)
				.stroke({ color: 0xf2b33d, width: Math.max(2, edge * 0.45) });
		}
	};
</script>

<Graphics {draw} />
{#if props.tab}
	<Container y={-props.height / 2 - tabFont * 1.45 * 0.05}>
		<BitmapText anchor={0.5} text={props.tab} style={{ fontFamily: 'gold', fontSize: tabFont }} />
	</Container>
{/if}
