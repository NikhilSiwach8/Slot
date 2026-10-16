<script lang="ts" module>
	import type { WinLevelData } from '../game/winLevelMap';

	export type EmitterEventFreeSpinOutro =
		| { type: 'freeSpinOutroShow' }
		| { type: 'freeSpinOutroHide' }
		| { type: 'freeSpinOutroCountUp'; amount: number; winLevelData: WinLevelData };
</script>

<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { FadeContainer, WinCountUpProvider, ResponsiveBitmapText } from 'components-pixi';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';
	import { waitForResolve, waitForTimeout } from 'utils-shared/wait';
	import { CanvasSizeRectangle } from 'components-layout';
	import { OnMount } from 'components-shared';

	import { getContext } from '../game/context';
	import { createTween01, type Tween01, easeOutBack } from './fx/timeline.svelte';
	import PressToContinue from './PressToContinue.svelte';
	import Splash from './Splash.svelte';
	import WinCoins from './WinCoins.svelte';

	const context = getContext();

	let show = $state(true);
	let intro = $state(createTween01(1));
	let amount = $state(0);
	let winLevelData = $state<WinLevelData>();
	let oncomplete = $state(() => {});
	let onCountUpComplete = $state(() => {});

	context.eventEmitter.subscribeOnMount({
		freeSpinOutroShow: () => (show = true),
		freeSpinOutroHide: async () => (show = false),
		freeSpinOutroCountUp: async (emitterEvent) => {
			amount = emitterEvent.amount;
			winLevelData = emitterEvent.winLevelData;
			intro = createTween01(1);
			// the win slams onto the plaque once the art has lunged in
			waitForTimeout(650).then(() => (intro = createTween01(500)));
			await waitForResolve((resolve) => (oncomplete = resolve));
		},
	});
</script>

<FadeContainer {show}>
	{#if winLevelData}
		{@const duration = winLevelData.presentDuration}
		{@const isBigWin = winLevelData.type === 'big'}
		<WinCountUpProvider {amount} {duration} oncomplete={() => onCountUpComplete()}>
			{#snippet children({ countUpAmount, startCountUp, finishCountUp, countUpCompleted })}
				<OnMount onmount={() => startCountUp()} />

				<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.5} />

				<!-- RAID COMPLETE splash: the total win counts up on its blank plaque -->
				<Splash name="outro">
					{#snippet children({ plaque })}
						<Container x={plaque.x} y={plaque.y} scale={easeOutBack(Math.min(1, intro.t), 1.8)}>
							<BitmapText anchor={0.5} y={-plaque.height * 0.27} text="TOTAL WIN" style={{ fontFamily: 'gold', fontSize: plaque.height * 0.22 }} />
							<ResponsiveBitmapText
								anchor={0.5}
								y={plaque.height * 0.13}
								style={{ fontFamily: 'gold', fontSize: plaque.height * (isBigWin ? 0.5 : 0.44) }}
								text={bookEventAmountToCurrencyString(countUpAmount)}
								maxWidth={plaque.width * 0.88}
							/>
						</Container>
					{/snippet}
				</Splash>

				<WinCoins emit={!countUpCompleted} levelAlias={winLevelData?.alias} />

				<PressToContinue onpress={() => (countUpCompleted ? oncomplete() : finishCountUp())} />
			{/snippet}
		</WinCountUpProvider>
	{/if}
</FadeContainer>
