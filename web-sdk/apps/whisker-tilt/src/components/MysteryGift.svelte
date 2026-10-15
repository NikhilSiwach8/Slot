<script lang="ts" module>
	export type EmitterEventMysteryGift = { type: 'mysteryGiftReveal'; kind: 'free' | 'super'; spins: number };
</script>

<!-- Mitten's Gift: the present drops, wobbles, bursts open and shows what's inside. -->
<script lang="ts">
	import { BitmapText, Container, Sprite } from 'pixi-svelte';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';

	import { getContext } from '../game/context';
	import { animate, easeOutBack } from '../game/tiltBoard.svelte';
	import Rays from './fx/Rays.svelte';

	const context = getContext();
	const main = $derived(context.stateLayoutDerived.mainLayout());

	let show = $state(false);
	let drop = $state(0);
	let wobble = $state(0);
	let opened = $state(0);
	let gift = $state<{ kind: 'free' | 'super'; spins: number }>({ kind: 'free', spins: 0 });

	context.eventEmitter.subscribeOnMount({
		mysteryGiftReveal: async ({ kind, spins }) => {
			gift = { kind, spins };
			drop = wobble = opened = 0;
			show = true;
			context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_scatter_reveal' });
			await animate(450, (t) => (drop = easeOutBack(t, 1.4)));
			await animate(700, (t) => (wobble = Math.sin(t * Math.PI * 6) * (1 - t)));
			context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_superfreespin' });
			await animate(450, (t) => (opened = t));
			await animate(1500, () => {});
			show = false;
		},
	});
</script>

{#if show}
	<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.55} />
	<MainContainer>
		<Container x={main.width / 2} y={main.height * 0.42}>
			{#if opened > 0}
				<Rays radius={420 * opened} colour={0xffd36b} alpha={0.6} />
			{/if}
			<Container y={-500 * (1 - drop)} rotation={wobble * 0.12}>
				<Sprite
					key={opened > 0 ? 'gift_open' : 'gift_closed'}
					anchor={{ x: 0.5, y: 0.6 }}
					width={opened > 0 ? 304 * 0.9 : 377 * 0.9}
					height={420 * 0.9}
				/>
			</Container>
			{#if opened > 0}
				<Container y={230} scale={easeOutBack(opened, 1.6)}>
					<BitmapText
						anchor={0.5}
						text={gift.kind === 'super' ? 'SUPER SNOW DAY' : 'SNOW DAY'}
						style={{ fontFamily: 'gold', fontSize: gift.kind === 'super' ? 70 : 84 }}
					/>
					<BitmapText anchor={0.5} y={78} text={`${gift.spins} FREE SPINS`} style={{ fontFamily: 'gold', fontSize: 58 }} />
				</Container>
			{/if}
		</Container>
	</MainContainer>
{/if}
