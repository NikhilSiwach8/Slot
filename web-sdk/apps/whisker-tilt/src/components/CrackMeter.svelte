<!-- Off the Shelf: how close the round is to the max win (the only amount it can pay). -->
<script lang="ts">
	import { BitmapText, Container, Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { FRAME } from '../game/constants';

	const context = getContext();
	const layout = $derived(context.stateGameDerived.boardLayout());
	const boxHalf = $derived((FRAME.size * layout.scale) / 2);
	const crack = $derived(context.stateGame.crack);
	const FONT = { fontFamily: 'gold', fontSize: 30 };

	// beside the box on wide screens (where the tumble win sits in other modes), under it when stacked
	const position = $derived(
		context.stateLayoutDerived.isStacked()
			? { x: layout.x, y: layout.y + boxHalf + 40 }
			: { x: layout.x + boxHalf + 190, y: layout.y - layout.height * 0.25 },
	);
</script>

{#if crack !== null}
	<Container {...position}>
		<BitmapText anchor={0.5} y={-48} text="MAX WIN METER" style={FONT} />
		<Graphics
			draw={(g) => {
				g.roundRect(-160, -20, 320, 40, 20).fill({ color: 0x0f2547, alpha: 0.92 }).stroke({ color: 0xbfe3ff, width: 3 });
				if (crack > 0) g.roundRect(-155, -15, 310 * crack, 30, 15).fill({ color: 0x9fe6ff });
			}}
		/>
		<BitmapText anchor={0.5} text={`${Math.floor(crack * 100)}%`} style={FONT} />
	</Container>
{/if}
