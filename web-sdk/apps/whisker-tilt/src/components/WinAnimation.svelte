<!-- Big-win banner: rotating gold rays, the tier title (BIG / SUPER / MEGA / EPIC /
     MAX WIN) slamming in, and the counting amount underneath. -->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { onDestroy } from 'svelte';
	import { BitmapText, Container } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import Rays from './fx/Rays.svelte';
	import { createClock, easeOutBack, clamp01 } from './fx/timeline.svelte';

	type Props = {
		animationMap: { intro: string; idle: string; outro: string };
		children: Snippet;
	};

	const props: Props = $props();
	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const TITLES: Record<string, string> = { big: 'BIG WIN', super: 'SUPER WIN', mega: 'MEGA WIN', epic: 'EPIC WIN', max: 'MAX WIN' };
	const title = $derived(TITLES[props.animationMap.intro.split('_')[0]] ?? 'BIG WIN');
	const intro = $derived(easeOutBack(clamp01(clock.seconds / 0.45), 2.2));
	const breathe = $derived(1 + Math.sin(clock.seconds * 3) * 0.03);
	const width = $derived(context.stateGameDerived.boardLayout().width);
</script>

<Rays radius={width * 0.9} alpha={clamp01(clock.seconds / 0.3)} />
<Container scale={intro * breathe} y={-SYMBOL_SIZE * 0.9}>
	<BitmapText anchor={0.5} text={title} style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 1.25 }} />
</Container>
<Container y={SYMBOL_SIZE * 0.55} scale={0.3 * clamp01(clock.seconds / 0.3)}>
	{@render props.children()}
</Container>
