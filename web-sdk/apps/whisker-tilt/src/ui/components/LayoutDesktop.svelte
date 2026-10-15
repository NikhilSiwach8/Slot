<script lang="ts">
	import { stateUi } from 'state-shared';
	import { BLACK } from 'constants-shared/colors';
	import { MainContainer } from 'components-layout';
	import { Container, Rectangle, anchorToPivot } from 'pixi-svelte';

	import UiArt from './UiArt.svelte';
	import artSizes from '../artSizes.json';
	import { DESKTOP_BASE_SIZE, UI_BASE_SIZE } from '../constants';
	import { getContext } from '../context';
	import type { LayoutUiProps } from '../types';

	const props: LayoutUiProps = $props();
	const context = getContext();

	// Bottom bar laid out like the art sheet:
	// [menu] [buy] [balance] [win]   [ − BET + ] [SPIN] [turbo] [auto]
	const BAR_WIDTH = 1764;
	const MID = DESKTOP_BASE_SIZE * 0.5;
	const FRAME_X = 1080;
	const FRAME_HEIGHT = UI_BASE_SIZE * 1.0;
	const frameScale = FRAME_HEIGHT / artSizes.bar_frame.height;
	// where the − / panel / + sit inside the frame art (art px from its centre)
	const MINUS_X = FRAME_X + (52 - artSizes.bar_frame.width / 2) * frameScale;
	const PLUS_X = FRAME_X + (299 - artSizes.bar_frame.width / 2) * frameScale;
	const PANEL_X = FRAME_X + (174 - artSizes.bar_frame.width / 2) * frameScale;
</script>

<Container x={20}>
	{@render props.gameName()}
</Container>

<Container x={context.stateLayoutDerived.canvasSizes().width - 20}>
	{@render props.logo()}
</Container>

<MainContainer standard alignVertical="bottom">
	<Container
		x={context.stateLayoutDerived.mainLayoutStandard().width * 0.5}
		y={context.stateLayoutDerived.mainLayoutStandard().height - DESKTOP_BASE_SIZE - 10}
		pivot={anchorToPivot({
			anchor: { x: 0.5, y: 0 },
			sizes: { height: DESKTOP_BASE_SIZE, width: BAR_WIDTH },
		})}
	>
		<Container y={MID} x={70} scale={0.8}>
			{@render props.buttonMenu({ anchor: 0.5 })}
		</Container>

		<Container y={MID} x={215} scale={0.8}>
			{@render props.buttonBuyBonus({ anchor: 0.5 })}
		</Container>

		<Container y={MID - 55} x={470} scale={0.85}>
			{@render props.amountBalance({ stacked: true })}
		</Container>

		<Container y={MID - 55} x={770} scale={0.85}>
			{@render props.amountWin({ stacked: true })}
		</Container>

		<!-- wooden frame holding − BET + -->
		<UiArt name="bar_frame" x={FRAME_X} y={MID} width={artSizes.bar_frame.width * frameScale} height={FRAME_HEIGHT} />

		<Container y={MID - 40} x={PANEL_X} scale={0.75}>
			{@render props.amountBet({ stacked: true, tiled: false })}
		</Container>

		<Container y={MID} x={MINUS_X} scale={0.52}>
			{@render props.buttonDecrease({ anchor: 0.5 })}
		</Container>

		<Container y={MID} x={PLUS_X} scale={0.52}>
			{@render props.buttonIncrease({ anchor: 0.5 })}
		</Container>

		<Container y={MID - 8} x={1405} scale={0.9}>
			{@render props.buttonBet({ anchor: 0.5 })}
		</Container>

		<Container y={MID} x={1560} scale={0.7}>
			{@render props.buttonTurbo({ anchor: 0.5 })}
		</Container>

		<Container y={MID} x={1680} scale={0.7}>
			{@render props.buttonAutoSpin({ anchor: 0.5 })}
		</Container>
	</Container>
</MainContainer>

{#if stateUi.menuOpen}
	<Rectangle
		eventMode="static"
		cursor="pointer"
		alpha={0.5}
		anchor={0.5}
		backgroundColor={BLACK}
		width={context.stateLayoutDerived.canvasSizes().width}
		height={context.stateLayoutDerived.canvasSizes().height}
		x={context.stateLayoutDerived.canvasSizes().width * 0.5}
		y={context.stateLayoutDerived.canvasSizes().height * 0.5}
		onpointerup={() => (stateUi.menuOpen = false)}
	/>

	<MainContainer standard alignVertical="bottom">
		<Container
			x={298}
			y={context.stateLayoutDerived.mainLayoutStandard().height - DESKTOP_BASE_SIZE - 10}
		>
			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5 - 150 - 170 * 3}>
				{@render props.buttonPayTable({ anchor: 0.5 })}
			</Container>

			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5 - 150 - 170 * 2}>
				{@render props.buttonGameRules({ anchor: 0.5 })}
			</Container>

			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5 - 150 - 170 * 1}>
				{@render props.buttonSettings({ anchor: 0.5 })}
			</Container>

			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5 - 150}>
				{@render props.buttonSoundSwitch({ anchor: 0.5 })}
			</Container>

			<Container scale={0.8} y={DESKTOP_BASE_SIZE * 0.5}>
				{@render props.buttonMenuClose({ anchor: 0.5 })}
			</Container>
		</Container>
	</MainContainer>
{/if}
