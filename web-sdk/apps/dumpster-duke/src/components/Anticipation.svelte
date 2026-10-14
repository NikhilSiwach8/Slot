<!-- Scatter tease on a reel still spinning: a pulsing gold column with rising
     sparks. Removed by <Anticipations> when the reel stops. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';

	import { getContext } from '../game/context';
	import type { Reel } from '../game/stateGame.svelte';
	import { REEL_PADDING, SYMBOL_SIZE, BOARD_DIMENSIONS } from '../game/constants';
	import { createClock } from './fx/timeline.svelte';

	type Props = {
		reel: Reel;
		oncomplete: () => void;
	};

	const props: Props = $props();
	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());
	const strength = new Tween(0, { duration: 250 });
	strength.set(1);
	// the parent unmounts this when the reel stops (reelState.anticipating = false)

	const H = SYMBOL_SIZE * BOARD_DIMENSIONS.y;
	const draw = (t: number) => (g: PIXI.Graphics) => {
		const w = SYMBOL_SIZE;
		for (let i = 0; i < 4; i++) {
			const grow = i * 7;
			g.roundRect(-w / 2 - grow, -grow, w + grow * 2, H + grow * 2, 18 + grow).stroke({
				color: i === 0 ? 0xffe27a : 0xffb02e,
				width: i === 0 ? 5 : 7,
				alpha: (i === 0 ? 0.9 : 0.35 - i * 0.07) * (0.7 + 0.3 * Math.sin(t * 9)),
			});
		}
		for (let k = 0; k < 10; k++) {
			const phase = (t * 0.9 + k / 10) % 1;
			const x = Math.sin(k * 12.9898) * w * 0.42;
			g.circle(x, H * (1 - phase), 4 + (k % 3) * 2).fill({ color: k % 2 ? 0x6fd6ff : 0xffd34d, alpha: 1 - phase });
		}
	};
</script>

<Container
	x={context.stateGameDerived.boardLayout().x -
		context.stateGameDerived.boardLayout().width * 0.5 +
		(props.reel.reelIndex + REEL_PADDING) * SYMBOL_SIZE}
	y={context.stateGameDerived.boardLayout().y - H / 2}
	alpha={strength.current}
>
	<Graphics draw={draw(clock.seconds)} blendMode="add" />
</Container>
