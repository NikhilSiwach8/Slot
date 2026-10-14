<script lang="ts">
	import { Container } from 'pixi-svelte';
	import { MainContainer } from 'components-layout';

	import { getContext } from '../game/context';
	import type { WinLevelAlias } from '../game/winLevelMap';
	import CoinShower from './fx/CoinShower.svelte';

	type Props = {
		emit?: boolean;
		levelAlias?: WinLevelAlias;
	};

	const props: Props = $props();
	const context = getContext();
	// more coins for bigger tiers; small wins get none
	const COUNT: Partial<Record<WinLevelAlias, number>> = { big: 28, superwin: 36, mega: 44, epic: 52, max: 64 };
	const count = $derived(props.levelAlias ? COUNT[props.levelAlias] : undefined);
</script>

{#if count}
	<MainContainer>
		<Container x={context.stateGameDerived.boardLayout().x} y={context.stateGameDerived.boardLayout().y}>
			<CoinShower
				{count}
				active={!!props.emit}
				width={context.stateGameDerived.boardLayout().width * 1.6}
				height={context.stateGameDerived.boardLayout().height * 1.8}
			/>
		</Container>
	</MainContainer>
{/if}
