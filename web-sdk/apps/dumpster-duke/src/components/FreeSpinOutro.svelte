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
	import { waitForResolve } from 'utils-shared/wait';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { OnMount } from 'components-shared';

	import { getContext } from '../game/context';
	import Plaque from './fx/Plaque.svelte';
	import Rays from './fx/Rays.svelte';
	import { createTween01, type Tween01, easeOutBack } from './fx/timeline.svelte';
	import PressToContinue from './PressToContinue.svelte';
	import WinCoins from './WinCoins.svelte';

	const context = getContext();

	let show = $state(true);
	const PANEL = { width: 1100, height: 620 };
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
			intro = createTween01(500);
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

				<!-- end of the Haunted Raid: total win on a plaque over gold rays -->
				<MainContainer>
					<Container
						x={context.stateLayoutDerived.mainLayout().width * 0.5}
						y={context.stateLayoutDerived.mainLayout().height * 0.5}
						scale={easeOutBack(Math.min(1, intro.t), 1.8)}
					>
						<Rays radius={PANEL.width * 0.95} />
						<Plaque width={PANEL.width} height={PANEL.height} glow={1} />
						<BitmapText anchor={0.5} y={-PANEL.height * 0.3} text="HAUNTED RAID" style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.16 }} />
						<BitmapText anchor={0.5} y={-PANEL.height * 0.12} text="TOTAL WIN" style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.11 }} />
						<ResponsiveBitmapText
							anchor={0.5}
							y={PANEL.height * 0.14}
							style={{ fontFamily: 'gold', fontSize: PANEL.height * (isBigWin ? 0.28 : 0.24) }}
							text={bookEventAmountToCurrencyString(countUpAmount)}
							maxWidth={PANEL.width * 0.85}
						/>
					</Container>
				</MainContainer>

				<WinCoins emit={!countUpCompleted} levelAlias={winLevelData?.alias} />

				<PressToContinue onpress={() => (countUpCompleted ? oncomplete() : finishCountUp())} />
			{/snippet}
		</WinCountUpProvider>
	{/if}
</FadeContainer>
