<script lang="ts">
	import { onMount } from 'svelte';

	import { EnablePixiExtension } from 'components-pixi';
	import { EnableHotkey } from 'components-shared';
	import { MainContainer } from 'components-layout';
	import { App, BitmapText, REM } from 'pixi-svelte';
	import { stateModal } from 'state-shared';

	import { UI, UiGameName } from '../ui';
	import { GameVersion } from 'components-ui-html';
	import GameModals from './GameModals.svelte';

	import { getContext } from '../game/context';
	import EnableSound from './EnableSound.svelte';
	import EnableGameActor from './EnableGameActor.svelte';
	import ResumeBet from './ResumeBet.svelte';
	import Sound from './Sound.svelte';
	import Background from './Background.svelte';
	import LoadingScreen from './LoadingScreen.svelte';
	import TiltBoard from './TiltBoard.svelte';
	import Mitten from './Mitten.svelte';
	import WinLabels from './WinLabels.svelte';
	import MysteryGift from './MysteryGift.svelte';
	import ShelfResult from './ShelfResult.svelte';
	import TumbleWinAmount from './TumbleWinAmount.svelte';
	import Win from './Win.svelte';
	import FreeSpinIntro from './FreeSpinIntro.svelte';
	import FreeSpinCounter from './FreeSpinCounter.svelte';
	import FreeSpinOutro from './FreeSpinOutro.svelte';
	import Transition from './Transition.svelte';

	const context = getContext();

	onMount(() => (context.stateLayout.showLoadingScreen = true));

	context.eventEmitter.subscribeOnMount({
		buyBonusConfirm: () => {
			stateModal.modal = { name: 'buyBonusConfirm' };
		},
	});
</script>

<App>
	<EnableSound />
	<EnableHotkey />
	<EnableGameActor />
	<EnablePixiExtension />

	<Background />

	{#if context.stateLayout.showLoadingScreen}
		<LoadingScreen onloaded={() => (context.stateLayout.showLoadingScreen = false)} />
	{:else}
		<ResumeBet />
		<!--
			The reason why <Sound /> is rendered after clicking the loading screen:
			"Autoplay with sound is allowed if: The user has interacted with the domain (click, tap, etc.)."
			Ref: https://developer.chrome.com/blog/autoplay
		-->
		<Sound />

		<MainContainer>
			<Mitten />
			<TiltBoard />
			<WinLabels />
			<TumbleWinAmount />
		</MainContainer>

		<UI>
			{#snippet gameName()}
				<UiGameName name="" />
			{/snippet}
			{#snippet logo()}
				<!-- until the logo plate art arrives: the title in the game font -->
				<BitmapText anchor={{ x: 1, y: 0 }} y={8} text="WHISKER TILT" style={{ fontFamily: 'gold', fontSize: Math.min(REM * 2.2, context.stateLayoutDerived.canvasSizes().width * 0.04) }} />
			{/snippet}
		</UI>
		<Win />
		<FreeSpinIntro />
		{#if ['desktop', 'landscape'].includes(context.stateLayoutDerived.layoutType())}
			<FreeSpinCounter />
		{/if}
		<FreeSpinOutro />
		<MysteryGift />
		<ShelfResult />
		<Transition />

	{/if}
</App>

<GameModals>
	{#snippet version()}
		<GameVersion version="1.0.0" />
	{/snippet}
</GameModals>
