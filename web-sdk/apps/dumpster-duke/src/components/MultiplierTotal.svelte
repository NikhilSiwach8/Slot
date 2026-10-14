<script lang="ts" module>
	export type EmitterEventMultiplierTotal =
		| { type: 'multiplierTotalShow' }
		| { type: 'multiplierTotalHide' }
		| { type: 'multiplierTotalUpdate'; totalMultiplier: number }
		| { type: 'multiplierTotalAnimate' };
</script>

<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import Rays from './fx/Rays.svelte';
	import { createTween01, type Tween01, easeOutBack } from './fx/timeline.svelte';
	import { stateBetDerived } from 'state-shared';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import BoardContainer from './BoardContainer.svelte';


	const context = getContext();

	let show = $state(false);
	let slam = $state<Tween01 | null>(null);
	let totalMultiplier = $state(0);

	context.eventEmitter.subscribeOnMount({
		multiplierTotalShow: () => (show = true),
		multiplierTotalHide: () => (show = false),
		multiplierTotalUpdate: (emitterEvent) => (totalMultiplier = emitterEvent.totalMultiplier),
		multiplierTotalAnimate: async () => {
			slam = createTween01(900 / stateBetDerived.timeScale());
			await slam.done;
		},
	});
</script>

<!-- total bottle-cap multiplier: slams onto the middle of the board over gold rays -->
{#if show}
	<BoardContainer>
		<Container
			x={context.stateGameDerived.boardLayout().width * 0.5}
			y={context.stateGameDerived.boardLayout().height * 0.5}
			alpha={slam ? Math.min(1, slam.t * 4) * (slam.t > 0.8 ? (1 - slam.t) * 5 : 1) : 1}
		>
			<Rays radius={SYMBOL_SIZE * 2.2} count={12} />
			<Container scale={slam ? 1.8 - 0.8 * easeOutBack(Math.min(1, slam.t * 2.5), 2.5) : 1}>
				<BitmapText
					anchor={0.5}
					text={`${totalMultiplier}x`}
					style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 1.6 }}
				/>
			</Container>
		</Container>
	</BoardContainer>
{/if}
