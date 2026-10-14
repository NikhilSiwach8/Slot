<script lang="ts">
	import DukeSymbol, { type DukeSymbolInfo } from './DukeSymbol.svelte';
	import { getSymbolInfo } from '../game/utils';
	import type { SymbolState, RawSymbol } from '../game/types';

	type Props = {
		x?: number;
		y?: number;
		state: SymbolState;
		rawSymbol: RawSymbol;
		oncomplete?: () => void;
		loop?: boolean;
		dimmed?: boolean;
	};

	const props: Props = $props();
	const symbolInfo = $derived(getSymbolInfo({ rawSymbol: props.rawSymbol, state: props.state }));
</script>

<DukeSymbol
	symbolInfo={symbolInfo as DukeSymbolInfo}
	x={props.x}
	y={props.y}
	oncomplete={props.oncomplete}
	loop={props.loop}
	dimmed={props.dimmed}
/>
