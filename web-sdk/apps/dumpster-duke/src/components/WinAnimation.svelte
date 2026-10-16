<!-- Win banner: the scary dumpster scene (components/fx/ScaryWinScene.svelte) bursts up,
     the tier title (GOOD / BIG / SUPER / MEGA / EPIC / MAX WIN) slams in under it, and the
     counting amount sits below. Bigger tiers get more monsters, lightning and shake. -->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { onDestroy } from 'svelte';
	import { BitmapText, Container } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import Rays from './fx/Rays.svelte';
	import ScaryWinScene from './fx/ScaryWinScene.svelte';
	import { createClock, easeOutBack, clamp01 } from './fx/timeline.svelte';

	type Props = {
		animationMap: { intro: string; idle: string; outro: string };
		children: Snippet;
	};

	const props: Props = $props();
	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const TIERS: Record<string, { title: string; tier: number }> = {
		good: { title: 'GOOD WIN', tier: 0 },
		big: { title: 'BIG WIN', tier: 1 },
		super: { title: 'SUPER WIN', tier: 2 },
		mega: { title: 'MEGA WIN', tier: 3 },
		epic: { title: 'EPIC WIN', tier: 4 },
		max: { title: 'MAX WIN', tier: 5 },
	};
	const level = $derived(TIERS[props.animationMap.intro.split('_')[0]] ?? TIERS.big);
	const t = $derived(clock.seconds);
	// the title slams in once the dumpster has burst up
	const intro = $derived(easeOutBack(clamp01((t - 0.35) / 0.4), 2.6));
	const breathe = $derived(1 + Math.sin(t * 3) * 0.03);
	const jitter = $derived(level.tier >= 3 ? Math.sin(t * 53) * 2.5 : 0);
	const width = $derived(context.stateGameDerived.boardLayout().width);
	const scale = $derived(level.tier === 0 ? 0.78 : 1);
</script>

<Container {scale}>
	<Rays radius={width * 0.9} alpha={clamp01(t / 0.3) * (level.tier === 0 ? 0.5 : 1)} colour={level.tier >= 3 ? 0x9b5cff : undefined} />
	<Container y={-SYMBOL_SIZE * 1.35}>
		<ScaryWinScene {clock} tier={level.tier} />
	</Container>
	<Container scale={intro * breathe} x={jitter} y={SYMBOL_SIZE * 0.55}>
		<BitmapText anchor={0.5} text={level.title} style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 1.15 }} />
	</Container>
	<Container y={SYMBOL_SIZE * 1.6} scale={0.3 * clamp01((t - 0.45) / 0.3)}>
		{@render props.children()}
	</Container>
</Container>
