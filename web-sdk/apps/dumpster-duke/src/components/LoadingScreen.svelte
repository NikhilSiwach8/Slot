<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { BitmapText, Container, Graphics } from 'pixi-svelte';
	import { FadeContainer } from 'components-pixi';
	import { MainContainer } from 'components-layout';

	import { getContext } from '../game/context';
	import TransitionAnimation from './TransitionAnimation.svelte';
	import PressToContinue from './PressToContinue.svelte';
	import UiArt from '../ui/components/UiArt.svelte';
	import { createClock } from './fx/timeline.svelte';

	type Props = {
		onloaded: () => void;
	};

	const props: Props = $props();
	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());

	let loadingType = $state<'start' | 'transition'>('start');

	const BAR = { width: 420, height: 34 };
	const drawBar = (progress: number) => (g: PIXI.Graphics) => {
		g.roundRect(-BAR.width / 2, 0, BAR.width, BAR.height, BAR.height / 2).fill(0x1d1033).stroke({ color: 0xc8782a, width: 4 });
		const inner = Math.max(0, (BAR.width - 10) * progress);
		if (inner > 0) {
			g.roundRect(-BAR.width / 2 + 5, 5, inner, BAR.height - 10, (BAR.height - 10) / 2).fill(0xffc23a);
		}
	};
</script>

<!-- title, bouncing crown coin and loading bar -->
<FadeContainer show={loadingType === 'start'}>
	<MainContainer>
		<Container
			x={context.stateLayoutDerived.mainLayout().width * 0.5}
			y={context.stateLayoutDerived.mainLayout().height * 0.42}
		>
			<Container y={-170 - Math.abs(Math.sin(clock.seconds * 3)) * 40} scale={{ x: Math.cos(clock.seconds * 4), y: 1 }}>
				<UiArt name="icon_bonus" width={150} height={150} />
			</Container>
			<BitmapText anchor={0.5} text="DUMPSTER" style={{ fontFamily: 'gold', fontSize: 130 }} />
			<BitmapText anchor={0.5} y={120} text="DUKE" style={{ fontFamily: 'gold', fontSize: 150 }} />
			{#if !context.stateApp.loaded}
				<Graphics y={240} draw={drawBar(context.stateApp.loadingProgress / 100)} />
			{/if}
		</Container>
	</MainContainer>
</FadeContainer>

<!-- press to continue -->
<FadeContainer show={loadingType === 'start' && context.stateApp.loaded}>
	<PressToContinue onpress={() => (loadingType = 'transition')} />
</FadeContainer>

<!-- transition between the loading screen and the game -->
<FadeContainer show={loadingType === 'transition'}>
	<TransitionAnimation oncomplete={props.onloaded} />
</FadeContainer>
