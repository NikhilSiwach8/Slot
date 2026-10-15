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
	import { MainContainer } from 'components-layout';

	import Plaque from './fx/Plaque.svelte';

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
	<!-- Snow Day / Super Snow Day splash: the free-spin scene with a title plaque -->
	<CoverImage name={context.stateGame.freeSpinKind === 'super' ? 'bg_super' : 'fs_splash'} />
	<MainContainer>
		{@const main = context.stateLayoutDerived.mainLayout()}
		{@const super_ = context.stateGame.freeSpinKind === 'super'}
		<Plaque x={main.width / 2} y={main.height * 0.45} width={620} height={300} glow={1} />
		<BitmapText
			anchor={0.5}
			x={main.width / 2}
			y={main.height * 0.45 - 70}
			text={super_ ? 'SUPER SNOW DAY' : 'SNOW DAY'}
			style={{ fontFamily: 'gold', fontSize: super_ ? 62 : 80 }}
		/>
		<BitmapText
			anchor={0.5}
			x={main.width / 2}
			y={main.height * 0.45 + 40}
			text={`${freeSpinsFromEvent} FREE SPINS`}
			style={{ fontFamily: 'gold', fontSize: 64 }}
		/>
		{#if super_}
			<BitmapText
				anchor={0.5}
				x={main.width / 2}
				y={main.height * 0.45 + 110}
				text="ALL KEEPERS START AT X5"
				style={{ fontFamily: 'gold', fontSize: 34 }}
			/>
		{/if}
	</MainContainer>

	<PressToContinue onpress={() => oncomplete()} />
</FadeContainer>
