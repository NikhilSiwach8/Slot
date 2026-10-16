<script lang="ts" module>
	export type EmitterEventFreeSpinIntro =
		| { type: 'freeSpinIntroShow' }
		| { type: 'freeSpinIntroHide' }
		| { type: 'freeSpinIntroUpdate'; totalFreeSpins: number };
</script>

<script lang="ts">
	import { CanvasSizeRectangle } from 'components-layout';
	import { FadeContainer } from 'components-pixi';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { Container } from 'pixi-svelte';
	import { ResponsiveBitmapText } from 'components-pixi';

	import { getContext } from '../game/context';
	import { introSplash, type SplashName } from '../game/splashes';
	import { createTween01, easeOutBack } from './fx/timeline.svelte';
	import PressToContinue from './PressToContinue.svelte';
	import Splash from './Splash.svelte';

	const context = getContext();

	let show = $state(false);
	let freeSpinsFromEvent = $state(0);
	let oncomplete = $state(() => {});
	let splash = $state<SplashName>('raid');
	let pop = $state(createTween01(1));

	context.eventEmitter.subscribeOnMount({
		freeSpinIntroShow: () => {
			// Haunted Raid, Super Bonus or Mystery Bonus art, by the round's bet mode
			splash = introSplash();
			show = true;
		},
		freeSpinIntroHide: () => (show = false),
		freeSpinIntroUpdate: async (emitterEvent) => {
			// if (emitterEvent.extraSpins) {
			// 	context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_fs_respins' });
			// }
			// freeSpinsFromEvent = emitterEvent.extraSpins ?? emitterEvent.totalFreeSpins;
			freeSpinsFromEvent = emitterEvent.totalFreeSpins;
			pop = createTween01(1);
			// the count slams onto the plaque once the art has lunged in
			waitForTimeout(650).then(() => (pop = createTween01(450)));
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

<FadeContainer {show}>
	<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.5} />
	<!-- bonus splash: the art carries the title; the spin count goes on its blank plaque -->
	<Splash name={splash}>
		{#snippet children({ plaque })}
			<Container x={plaque.x} y={plaque.y} scale={easeOutBack(Math.min(1, pop.t), 2.2)}>
				<ResponsiveBitmapText
					anchor={0.5}
					text={`${freeSpinsFromEvent} FREE SPINS`}
					style={{ fontFamily: 'gold', fontSize: plaque.height * 0.6 }}
					maxWidth={plaque.width * 0.88}
				/>
			</Container>
		{/snippet}
	</Splash>

	<PressToContinue onpress={() => oncomplete()} />
</FadeContainer>
