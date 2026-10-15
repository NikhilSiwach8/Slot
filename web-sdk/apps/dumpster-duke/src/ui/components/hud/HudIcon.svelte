<!-- Simple drawn icons for the HUD (white with a dark outline, or gold). Centered on (0, 0). -->
<script lang="ts" module>
	export type HudIconName = 'spin' | 'menu' | 'close' | 'bolt' | 'left' | 'right' | 'auto';
</script>

<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { Graphics } from 'pixi-svelte';

	type Props = { name: HudIconName; size: number; color?: number; outline?: number };
	const props: Props = $props();

	const arrowHead = (g: PIXI.Graphics, x: number, y: number, angle: number, s: number) => {
		const a = (t: number) => ({ x: x + Math.cos(angle + t) * s, y: y + Math.sin(angle + t) * s });
		const p1 = a(0);
		const p2 = a((2 * Math.PI) / 3);
		const p3 = a((-2 * Math.PI) / 3);
		g.poly([p1.x, p1.y, p2.x, p2.y, p3.x, p3.y]);
	};

	const draw = (g: PIXI.Graphics) => {
		const s = props.size;
		const color = props.color ?? 0xffffff;
		const outline = props.outline ?? 0x1a0b06;
		const strokes = (width: number, path: (g: PIXI.Graphics) => void) => {
			path(g);
			g.stroke({ color: outline, width: width + s * 0.07, cap: 'round', join: 'round' });
			path(g);
			g.stroke({ color, width, cap: 'round', join: 'round' });
		};
		switch (props.name) {
			case 'spin':
			case 'auto': {
				const r = s * 0.36;
				const w = s * (props.name === 'auto' ? 0.1 : 0.12);
				for (const start of [0.15, Math.PI + 0.15]) {
					strokes(w, (gg) => gg.arc(0, 0, r, start, start + Math.PI * 0.72));
					const end = start + Math.PI * 0.72;
					arrowHead(g, Math.cos(end) * r, Math.sin(end) * r, end + Math.PI / 2, w * 1.5);
					g.fill(color).stroke({ color: outline, width: s * 0.03 });
				}
				if (props.name === 'auto') g.circle(0, 0, s * 0.08).fill(color);
				break;
			}
			case 'menu':
				for (const y of [-0.24, 0, 0.24]) strokes(s * 0.11, (gg) => gg.moveTo(-s * 0.28, y * s).lineTo(s * 0.28, y * s));
				break;
			case 'close':
				strokes(s * 0.12, (gg) => gg.moveTo(-s * 0.25, -s * 0.25).lineTo(s * 0.25, s * 0.25));
				strokes(s * 0.12, (gg) => gg.moveTo(s * 0.25, -s * 0.25).lineTo(-s * 0.25, s * 0.25));
				break;
			case 'bolt':
				g.poly([0.08, -0.42, -0.26, 0.06, -0.02, 0.06, -0.1, 0.42, 0.26, -0.08, 0.02, -0.08].map((v) => v * s))
					.fill(color)
					.stroke({ color: outline, width: s * 0.05, join: 'round' });
				break;
			case 'left':
				strokes(s * 0.16, (gg) => gg.moveTo(s * 0.15, -s * 0.32).lineTo(-s * 0.15, 0).lineTo(s * 0.15, s * 0.32));
				break;
			case 'right':
				strokes(s * 0.16, (gg) => gg.moveTo(-s * 0.15, -s * 0.32).lineTo(s * 0.15, 0).lineTo(-s * 0.15, s * 0.32));
				break;
		}
	};
</script>

<Graphics {draw} />
