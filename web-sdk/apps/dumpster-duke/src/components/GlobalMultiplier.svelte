<script lang="ts" module>
	export type EmitterEventGlobalMultiplier =
		| { type: 'globalMultiplierShow' }
		| { type: 'globalMultiplierHide' }
		| { type: 'globalMultiplierUpdate'; multiplier: number };
</script>

<!-- The Loot Bag (persistent free-spin multiplier): a plaque above the reels whose
     value pops and glows each time bottle caps are added. -->
<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { waitForTimeout } from 'utils-shared/wait';

	import BoardContainer from './BoardContainer.svelte';
	import Plaque from './fx/Plaque.svelte';
	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { createTween01, type Tween01, easeOutBack } from './fx/timeline.svelte';

	const PANEL = { width: SYMBOL_SIZE * 1.25, height: SYMBOL_SIZE * 0.62 };
	const context = getContext();
	const scale = $derived(context.stateLayoutDerived.isStacked() ? 1.28 : 1);
	const position = $derived({
		x: context.stateGameDerived.boardLayout().width - PANEL.width * 0.62,
		y: -SYMBOL_SIZE * 0.5,
	});

	let show = $state(false);
	let multiplier = $state(1);
	let pop = $state<Tween01 | null>(null);
	const popScale = $derived(pop ? 1 + 0.45 * Math.sin(Math.min(1, pop.t) * Math.PI) * (1 - pop.t * 0.3) : 1);

	context.eventEmitter.subscribeOnMount({
		globalMultiplierShow: () => (show = true),
		globalMultiplierHide: () => (show = false),
		globalMultiplierUpdate: async (emitterEvent) => {
			if (emitterEvent.multiplier === multiplier) return;
			const growing = emitterEvent.multiplier > multiplier;
			if (growing) context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_update' });
			else context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_reset' });
			multiplier = emitterEvent.multiplier;
			pop = createTween01(growing ? 450 : 200);
			await pop.done;
			await waitForTimeout(80);
		},
	});
</script>

<FadeContainer {show}>
	<BoardContainer>
		<Container {...position} {scale}>
			<Plaque width={PANEL.width} height={PANEL.height} glow={pop ? 1 - pop.t : 0} />
			<BitmapText
				anchor={0.5}
				y={-PANEL.height * 0.78}
				text="LOOT BAG"
				style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.17 }}
			/>
			<Container scale={popScale * (pop ? easeOutBack(Math.min(1, pop.t * 2)) * 0.2 + 0.8 : 1)}>
				<BitmapText anchor={0.5} text={`${multiplier}x`} style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.4 }} />
			</Container>
		</Container>
	</BoardContainer>
</FadeContainer>
