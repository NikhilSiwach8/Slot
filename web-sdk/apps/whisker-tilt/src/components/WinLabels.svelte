<script lang="ts" module>
	export type WinLabel = { reel: number; row: number; amount: number; mult: number };
	export type EmitterEventWinLabels = { type: 'winLabelsShow'; labels: WinLabel[] };
</script>

<!-- Each winning cluster's pay at its centre, with the Edge Keeper multiplier when one applied. -->
<script lang="ts">
	import { BitmapText, Container, Graphics } from 'pixi-svelte';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE, BOARD_SIZES } from '../game/constants';
	import { animate, easeOutBack, cellX, cellY } from '../game/tiltBoard.svelte';

	const context = getContext();
	const layout = $derived(context.stateGameDerived.boardLayout());

	let labels = $state<WinLabel[]>([]);
	let t = $state(0);

	context.eventEmitter.subscribeOnMount({
		winLabelsShow: async ({ labels: next }) => {
			labels = next;
			await animate(1000, (u) => (t = u));
			labels = [];
		},
	});

	const toMain = (reel: number, row: number) => ({
		x: layout.x + (cellX(reel) - BOARD_SIZES.width / 2) * layout.scale,
		y: layout.y + (cellY(row) - BOARD_SIZES.height / 2) * layout.scale,
	});
</script>

{#each labels as label, i (i)}
	{@const p = toMain(label.reel, label.row)}
	{@const pop = easeOutBack(Math.min(1, t / 0.3), 1.6)}
	<Container x={p.x} y={p.y - t * 20} scale={pop} alpha={t < 0.8 ? 1 : (1 - t) / 0.2}>
		<Graphics
			draw={(g) => g.roundRect(-90, -30, 180, 60, 26).fill({ color: 0x0f2547, alpha: 0.82 }).stroke({ color: 0xffd36b, width: 3 })}
		/>
		<BitmapText
			anchor={0.5}
			y={label.mult > 1 ? -8 : 0}
			text={bookEventAmountToCurrencyString(label.amount)}
			style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.36 }}
		/>
		{#if label.mult > 1}
			<BitmapText anchor={0.5} y={19} text={`KEEPERS X${label.mult}`} style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.2 }} />
		{/if}
	</Container>
{/each}
