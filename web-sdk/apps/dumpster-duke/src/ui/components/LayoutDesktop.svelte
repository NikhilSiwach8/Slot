<script lang="ts">
	import { MainContainer } from 'components-layout';
	import { Container } from 'pixi-svelte';

	import { getContext } from '../context';
	import type { LayoutUiProps } from '../types';

	const props: LayoutUiProps = $props();
	const context = getContext();

	// HUD in two corner clusters either side of the board (board spans x ±456 around the
	// centre and ends ~170 px above the bottom of the 1920 x 1080 layout):
	//   left:  [menu pill] [BONUS card]        right: [SPIN card] [turbo / auto]
	//                      BALANCE                       ‹ BET ›
	//   centre, under the board: WIN
	const CARD_Y = -310;
	const LABEL_Y = -168;
	const LEFT = -680;
	const RIGHT = 680;
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
		y={context.stateLayoutDerived.mainLayoutStandard().height}
	>
		<!-- left cluster -->
		<Container x={LEFT - 185} y={CARD_Y}>
			{@render props.buttonMenu({ anchor: 0.5 })}
		</Container>
		<Container x={LEFT} y={CARD_Y}>
			{@render props.buttonBuyBonus({ anchor: 0.5 })}
		</Container>
		<Container x={LEFT} y={LABEL_Y}>
			{@render props.amountBalance({ stacked: true })}
		</Container>

		<!-- centre -->
		<Container x={0} y={LABEL_Y + 10}>
			{@render props.amountWin({ stacked: true })}
		</Container>

		<!-- right cluster -->
		<Container x={RIGHT} y={CARD_Y}>
			{@render props.buttonBet({ anchor: 0.5 })}
		</Container>
		<Container x={RIGHT + 192} y={CARD_Y - 58}>
			{@render props.buttonAutoSpin({ anchor: 0.5 })}
		</Container>
		<Container x={RIGHT + 192} y={CARD_Y + 58}>
			{@render props.buttonTurbo({ anchor: 0.5 })}
		</Container>
		<Container x={RIGHT} y={LABEL_Y}>
			{@render props.amountBet({ stacked: true })}
		</Container>
		<Container x={RIGHT - 215} y={LABEL_Y + 72}>
			{@render props.buttonDecrease({ anchor: 0.5 })}
		</Container>
		<Container x={RIGHT + 215} y={LABEL_Y + 72}>
			{@render props.buttonIncrease({ anchor: 0.5 })}
		</Container>
	</Container>
</MainContainer>
