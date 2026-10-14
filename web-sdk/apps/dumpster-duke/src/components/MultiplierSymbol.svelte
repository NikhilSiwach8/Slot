<script lang="ts">
	import Symbol from './Symbol.svelte';
	import type { MultiplierSymbol } from '../game/stateGame.svelte';

	type Props = {
		reelIndex: number;
		multiplierSymbol: MultiplierSymbol;
	};

	const props: Props = $props();
</script>

<Symbol
	state={props.multiplierSymbol.symbolState}
	rawSymbol={props.multiplierSymbol.rawSymbol}
	x={props.multiplierSymbol.symbolX.current}
	y={props.multiplierSymbol.symbolY.current}
	oncomplete={props.multiplierSymbol.oncomplete}
/>
