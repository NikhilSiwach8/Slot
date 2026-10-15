<script lang="ts" module>
	export type EmitterEventBoardFrame =
		| { type: 'boardFrameGlowShow' }
		| { type: 'boardFrameGlowHide' };
</script>

<!-- Code-drawn reel house: wooden frame with bronze trim and rivets around a dark
     glass window, plus separators between the reels. In the Haunted Raid the frame
     gets a pulsing purple glow. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE, BOARD_DIMENSIONS } from '../game/constants';
	import { createClock } from './fx/timeline.svelte';

	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());
	const glow = new Tween(0, { duration: 600 });

	context.eventEmitter.subscribeOnMount({
		boardFrameGlowShow: () => glow.set(1),
		boardFrameGlowHide: () => glow.set(0),
	});

	const PAD = SYMBOL_SIZE * 0.1;
	const BORDER = SYMBOL_SIZE * 0.16;

	const drawFrame = (g: PIXI.Graphics) => {
		const { width, height } = context.stateGameDerived.boardLayout();
		const w = width + PAD * 2;
		const h = height + PAD * 2;
		const r = SYMBOL_SIZE * 0.14;
		// window
		g.roundRect(-w / 2, -h / 2, w, h, r).fill({ color: 0x120822, alpha: 0.86 });
		// reel separators
		for (let i = 1; i < BOARD_DIMENSIONS.x; i++) {
			const x = -width / 2 + i * SYMBOL_SIZE;
			g.rect(x - 1, -height / 2 + 6, 2, height - 12).fill({ color: 0x8a5cc4, alpha: 0.18 });
		}
		// wooden frame with bronze trim
		g.roundRect(-w / 2 - BORDER, -h / 2 - BORDER, w + BORDER * 2, h + BORDER * 2, r + BORDER)
			.stroke({ color: 0x4a2414, width: BORDER, alignment: 0 });
		g.roundRect(-w / 2 - BORDER, -h / 2 - BORDER, w + BORDER * 2, h + BORDER * 2, r + BORDER)
			.stroke({ color: 0x1c0a06, width: 4, alignment: 1 });
		g.roundRect(-w / 2 - 3, -h / 2 - 3, w + 6, h + 6, r + 3).stroke({ color: 0xc8782a, width: 6 });
		g.roundRect(-w / 2 + 1, -h / 2 + 1, w - 2, h - 2, r).stroke({ color: 0xffc23a, width: 2, alpha: 0.5 });
		// rivets along the frame
		const rivet = (x: number, y: number) =>
			g.circle(x, y, BORDER * 0.22).fill(0xf0b45a).stroke({ color: 0x3a1a08, width: 2 });
		const ox = w / 2 + BORDER / 2;
		const oy = h / 2 + BORDER / 2;
		for (let i = 0; i <= 6; i++) {
			const x = -ox + (2 * ox * i) / 6;
			rivet(x, -oy);
			rivet(x, oy);
		}
		for (let i = 1; i < 5; i++) {
			const y = -oy + (2 * oy * i) / 5;
			rivet(-ox, y);
			rivet(ox, y);
		}
	};

	const drawGlow = (g: PIXI.Graphics) => {
		const { width, height } = context.stateGameDerived.boardLayout();
		const w = width + PAD * 2 + BORDER * 2;
		const h = height + PAD * 2 + BORDER * 2;
		for (let i = 1; i <= 6; i++) {
			g.roundRect(-w / 2 - i * 10, -h / 2 - i * 10, w + i * 20, h + i * 20, SYMBOL_SIZE * 0.3 + i * 10)
				.stroke({ color: 0xb46bff, width: 10, alpha: 0.12 - i * 0.015 });
		}
	};
</script>

<Container x={context.stateGameDerived.boardLayout().x} y={context.stateGameDerived.boardLayout().y}>
	{#if glow.current > 0}
		<Graphics
			draw={drawGlow}
			blendMode="add"
			alpha={glow.current * (0.75 + 0.25 * Math.sin(clock.seconds * 3))}
		/>
	{/if}
	<Graphics draw={drawFrame} />
</Container>
