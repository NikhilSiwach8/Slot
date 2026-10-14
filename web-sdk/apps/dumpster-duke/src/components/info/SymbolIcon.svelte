<script lang="ts">
	import { SHEET_ORDER, SHEET_COLUMNS, SHEET_ROWS } from '../../game/rules';

	type Props = { symbol: string; size?: string };
	const props: Props = $props();

	const sheet = new URL('../../../assets/sprites/dukeSymbols/dukeSymbols.webp', import.meta.url).href;
	const index = $derived(SHEET_ORDER.indexOf(props.symbol));
	const col = $derived(index % SHEET_COLUMNS);
	const row = $derived(Math.floor(index / SHEET_COLUMNS));
</script>

<span
	class="icon"
	style="--size: {props.size ?? '4rem'}; background-image: url({sheet});
		background-size: {SHEET_COLUMNS * 100}% {SHEET_ROWS * 100}%;
		background-position: {(col / (SHEET_COLUMNS - 1)) * 100}% {(row / (SHEET_ROWS - 1)) * 100}%;"
	role="img"
	aria-label={props.symbol}
></span>

<style>
	.icon {
		display: inline-block;
		width: var(--size);
		height: var(--size);
		flex-shrink: 0;
		background-repeat: no-repeat;
	}
</style>
