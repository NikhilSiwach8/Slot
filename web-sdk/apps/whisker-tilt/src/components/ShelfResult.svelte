<script lang="ts" module>
	export type EmitterEventShelf = { type: 'shelfResult'; shattered: boolean };
</script>

<!-- Off the Shelf: the end of the round. The box either shatters (max win) or holds. -->
<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';

	import { getContext } from '../game/context';
	import { animate, easeOutBack } from '../game/tiltBoard.svelte';

	const context = getContext();
	const main = $derived(context.stateLayoutDerived.mainLayout());

	let show = $state(false);
	let shattered = $state(false);
	let t = $state(0);

	context.eventEmitter.subscribeOnMount({
		shelfResult: async (event) => {
			shattered = event.shattered;
			show = true;
			context.eventEmitter.broadcast({
				type: 'soundOnce',
				name: shattered ? 'sfx_multiplier_explosion_c' : 'sfx_winlevel_end',
			});
			await animate(1600, (u) => (t = u));
			show = false;
		},
	});
</script>

{#if show}
	<CanvasSizeRectangle backgroundColor={shattered ? 0xffffff : 0x000000} backgroundAlpha={shattered ? 0.6 * (1 - t) : 0.45} />
	<MainContainer>
		<Container x={main.width / 2} y={main.height * 0.45} scale={easeOutBack(Math.min(1, t / 0.3), 1.5)}>
			<BitmapText
				anchor={0.5}
				text={shattered ? 'THE BOX SHATTERED!' : 'THE BOX HELD'}
				style={{ fontFamily: 'gold', fontSize: 90 }}
			/>
			{#if !shattered}
				<BitmapText anchor={0.5} y={90} text="ONLY THE MAX WIN PAYS" style={{ fontFamily: 'gold', fontSize: 44 }} />
			{/if}
		</Container>
	</MainContainer>
{/if}
