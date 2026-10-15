<!-- Code-drawn plaque in the game's style: dark ice-blue face, bronze/wood border,
     gold inner line and rivets. Used for banners, counters and popups. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { Graphics } from 'pixi-svelte';

	type Props = { width: number; height: number; x?: number; y?: number; glow?: number; alpha?: number };
	const props: Props = $props();

	const draw = (g: PIXI.Graphics) => {
		const w = props.width;
		const h = props.height;
		const r = Math.min(w, h) * 0.18;
		const border = Math.max(6, Math.min(w, h) * 0.07);
		if (props.glow) {
			for (let i = 4; i >= 1; i--) {
				g.roundRect(-w / 2 - i * 6, -h / 2 - i * 6, w + i * 12, h + i * 12, r + i * 6).fill({
					color: 0x8fd3ff,
					alpha: 0.07 * props.glow,
				});
			}
		}
		// outer wood
		g.roundRect(-w / 2, -h / 2, w, h, r).fill(0x4a2414).stroke({ color: 0x1c0a06, width: 4 });
		// bronze band
		g.roundRect(-w / 2 + border * 0.35, -h / 2 + border * 0.35, w - border * 0.7, h - border * 0.7, r * 0.85)
			.stroke({ color: 0xc8782a, width: border * 0.35 });
		// face
		g.roundRect(-w / 2 + border, -h / 2 + border, w - border * 2, h - border * 2, r * 0.6).fill(0x14305c);
		// gold inner line
		g.roundRect(-w / 2 + border + 3, -h / 2 + border + 3, w - border * 2 - 6, h - border * 2 - 6, r * 0.5)
			.stroke({ color: 0xffc23a, width: 2, alpha: 0.65 });
		// rivets
		const inset = border * 0.55;
		for (const [x, y] of [[-1, -1], [1, -1], [-1, 1], [1, 1]]) {
			g.circle(x * (w / 2 - inset), y * (h / 2 - inset), border * 0.28).fill(0xf0b45a).stroke({ color: 0x3a1a08, width: 2 });
		}
	};
</script>

<Graphics x={props.x ?? 0} y={props.y ?? 0} alpha={props.alpha ?? 1} {draw} />
