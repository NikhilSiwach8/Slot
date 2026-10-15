<script lang="ts" module>
	export type EmitterEventMaxBoost = { type: 'maxBoost'; fromWin: number; toWin: number };
</script>

<!--
	Max or Nothing: the single spin won, so its win is boosted to the max win. The spin's
	own win shows first, then a gold "MAX WIN" slams in over it with rays and a flash.
-->
<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';
	import { waitForResolve } from 'utils-shared/wait';

	import { getContext } from '../game/context';
	import Plaque from './fx/Plaque.svelte';
	import Rays from './fx/Rays.svelte';
	import { createClock, easeOutBack, type Clock } from './fx/timeline.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();
	const PANEL = { width: 1100, height: 640 };
	const SLAM = 1.1; // seconds before MAX WIN slams in

	let show = $state(false);
	let fromWin = $state(0);
	let toWin = $state(0);
	let clock = $state<Clock>();
	let oncomplete = $state(() => {});

	const t = $derived(clock?.seconds ?? 0);
	const intro = $derived(easeOutBack(Math.min(1, t / 0.45), 1.8));
	const slam = $derived(t < SLAM ? 0 : easeOutBack(Math.min(1, (t - SLAM) / 0.35), 3));
	const flash = $derived(t < SLAM ? 0 : Math.max(0, 1 - (t - SLAM) / 0.5));

	context.eventEmitter.subscribeOnMount({
		maxBoost: async (emitterEvent) => {
			fromWin = emitterEvent.fromWin;
			toWin = emitterEvent.toWin;
			show = true;
			clock?.stop();
			clock = createClock();
			context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
			setTimeout(() => context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_explosion_b' }), SLAM * 1000);
			await waitForResolve((resolve) => (oncomplete = resolve));
			clock?.stop();
			show = false;
		},
	});
</script>

<FadeContainer {show}>
	<CanvasSizeRectangle backgroundColor={0x000000} backgroundAlpha={0.6} />
	<MainContainer>
		<Container
			x={context.stateLayoutDerived.mainLayout().width * 0.5}
			y={context.stateLayoutDerived.mainLayout().height * 0.5}
			scale={intro}
		>
			<Rays radius={PANEL.width * (0.8 + slam * 0.3)} />
			<Plaque width={PANEL.width} height={PANEL.height} glow={1} />
			<BitmapText anchor={0.5} y={-PANEL.height * 0.32} text="MAX OR NOTHING" style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.12 }} />
			<BitmapText
				anchor={0.5}
				y={-PANEL.height * 0.1}
				alpha={1 - slam * 0.55}
				text={`SPIN WIN ${bookEventAmountToCurrencyString(fromWin)}`}
				style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.08 }}
			/>
			{#if t >= SLAM}
				<Container y={PANEL.height * 0.14} scale={slam}>
					<BitmapText anchor={0.5} y={-PANEL.height * 0.02} text="MAX WIN" style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.2 }} />
					<BitmapText anchor={0.5} y={PANEL.height * 0.17} text={bookEventAmountToCurrencyString(toWin)} style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.11 }} />
				</Container>
			{/if}
		</Container>
	</MainContainer>
	<CanvasSizeRectangle backgroundColor={0xffffff} backgroundAlpha={flash * 0.7} />

	{#if t >= SLAM + 0.4}
		<PressToContinue onpress={() => oncomplete()} />
	{/if}
</FadeContainer>
