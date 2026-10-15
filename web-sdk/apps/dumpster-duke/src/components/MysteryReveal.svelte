<script lang="ts" module>
	export type EmitterEventMysteryReveal = { type: 'mysteryReveal'; spins: number; lootBag: number };
</script>

<!--
	Mystery Bonus: before the raid starts, the Duke's chest "rolls" the number of free spins
	and the starting Trick-or-Treat Bag like two slot reels, then lands them one after the other.
-->
<script lang="ts">
	import { BitmapText, Container } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { CanvasSizeRectangle, MainContainer } from 'components-layout';
	import { waitForResolve } from 'utils-shared/wait';

	import { getContext } from '../game/context';
	import Plaque from './fx/Plaque.svelte';
	import Rays from './fx/Rays.svelte';
	import { createClock, createTween01, easeOutBack, type Clock } from './fx/timeline.svelte';
	import PressToContinue from './PressToContinue.svelte';

	const context = getContext();
	const PANEL = { width: 1100, height: 660 };
	// values the chest can show while rolling (same ranges as the math)
	const SPIN_FACES = [5, 8, 10, 12, 15, 20, 25];
	const BAG_FACES = [0, 2, 3, 5, 8, 10, 15, 20];
	const ROLL_SPINS = 1.3; // seconds the spins reel rolls
	const ROLL_BAG = 2.1; // the Trick-or-Treat Bag reel lands a beat later

	let show = $state(false);
	let spins = $state(0);
	let lootBag = $state(0);
	let clock = $state<Clock>();
	let intro = $state(createTween01(1));
	let oncomplete = $state(() => {});

	const face = (faces: number[], until: number, value: number) => {
		const t = clock?.seconds ?? 0;
		if (t >= until) return value;
		return faces[Math.floor(t * 14) % faces.length];
	};
	const landed = (until: number) => (clock?.seconds ?? 0) >= until;
	const pop = (until: number) => {
		const since = (clock?.seconds ?? 0) - until;
		return since < 0 ? 1 : easeOutBack(Math.min(1, since / 0.35), 3);
	};

	context.eventEmitter.subscribeOnMount({
		mysteryReveal: async (emitterEvent) => {
			spins = emitterEvent.spins;
			lootBag = emitterEvent.lootBag;
			show = true;
			intro = createTween01(450);
			clock?.stop();
			clock = createClock();
			context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
			setTimeout(() => context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_up' }), ROLL_SPINS * 1000);
			setTimeout(() => context.eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_explosion_b' }), ROLL_BAG * 1000);
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
			scale={easeOutBack(Math.min(1, intro.t), 1.8)}
		>
			<Rays radius={PANEL.width * 0.95} />
			<Plaque width={PANEL.width} height={PANEL.height} glow={1} />
			<BitmapText anchor={0.5} y={-PANEL.height * 0.33} text="MYSTERY BONUS" style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.14 }} />

			<!-- free spins reel -->
			<Container x={-PANEL.width * 0.22} y={PANEL.height * 0.06}>
				<Plaque width={PANEL.width * 0.36} height={PANEL.height * 0.42} alpha={0.9} />
				<Container scale={pop(ROLL_SPINS)}>
					<BitmapText anchor={0.5} y={-PANEL.height * 0.03} text={`${face(SPIN_FACES, ROLL_SPINS, spins)}`}
						alpha={landed(ROLL_SPINS) ? 1 : 0.75} style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.2 }} />
				</Container>
				<BitmapText anchor={0.5} y={PANEL.height * 0.14} text="FREE SPINS" style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.07 }} />
			</Container>

			<!-- starting Trick-or-Treat Bag reel -->
			<Container x={PANEL.width * 0.22} y={PANEL.height * 0.06}>
				<Plaque width={PANEL.width * 0.36} height={PANEL.height * 0.42} alpha={0.9} />
				<Container scale={pop(ROLL_BAG)}>
					<BitmapText anchor={0.5} y={-PANEL.height * 0.03} text={`x${face(BAG_FACES, ROLL_BAG, lootBag)}`}
						alpha={landed(ROLL_BAG) ? 1 : 0.75} style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.2 }} />
				</Container>
				<BitmapText anchor={0.5} y={PANEL.height * 0.14} text="TREAT BAG" style={{ fontFamily: 'gold', fontSize: PANEL.height * 0.07 }} />
			</Container>
		</Container>
	</MainContainer>

	{#if landed(ROLL_BAG)}
		<PressToContinue onpress={() => oncomplete()} />
	{/if}
</FadeContainer>
