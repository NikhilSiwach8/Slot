<script lang="ts" module>
	export type EmitterEventFreeSpinIntro =
		| { type: 'freeSpinIntroShow' }
		| { type: 'freeSpinIntroHide' }
		| { type: 'freeSpinIntroUpdate'; totalFreeSpins: number };
</script>

<script lang="ts">
	import { CanvasSizeRectangle } from 'components-layout';
	import { FadeContainer } from 'components-pixi';
	import { waitForResolve } from 'utils-shared/wait';
	import { BitmapText } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import PressToContinue from './PressToContinue.svelte';
	import CoverImage from './CoverImage.svelte';


	const context = getContext();

	let show = $state(false);
	let freeSpinsFromEvent = $state(0);
	let oncomplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		freeSpinIntroShow: () => (show = true),
		freeSpinIntroHide: () => (show = false),
		freeSpinIntroUpdate: async (emitterEvent) => {
			// if (emitterEvent.extraSpins) {
			// 	context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_fs_respins' });
			// }
			// freeSpinsFromEvent = emitterEvent.extraSpins ?? emitterEvent.totalFreeSpins;
			freeSpinsFromEvent = emitterEvent.totalFreeSpins;
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

<FadeContainer {show}>
	<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.5} />
	<!-- Haunted Raid splash: the art carries the FREE SPINS sign; we add the spin count. -->
	<CoverImage name="fs_splash" />
	{@const canvas = context.stateLayoutDerived.canvasSizes()}
	{@const height = Math.max(canvas.height, (canvas.width / 1920) * 1080)}
	<BitmapText
		anchor={0.5}
		x={canvas.width / 2}
		y={canvas.height / 2 + height * 0.07}
		text={`${freeSpinsFromEvent} SPINS`}
		style={{ fontFamily: 'gold', fontSize: height * 0.09 }}
	/>

	<PressToContinue onpress={() => oncomplete()} />
</FadeContainer>
