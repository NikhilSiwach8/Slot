<!-- Scene change: a purple curtain closes from both sides around a spinning crown
     coin. `oncomplete` fires once the screen is fully covered (so the scene can
     switch underneath); the curtain is then opened by <Transition>. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy, onMount } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import UiArt from '../ui/components/UiArt.svelte';
	import { createTween01, type Tween01, easeInCubic, easeOutCubic } from './fx/timeline.svelte';

	type Props = {
		oncomplete: () => void;
		opening?: boolean;
	};

	const props: Props = $props();
	const context = getContext();
	const tween = createTween01(props.opening ? 380 : 420);
	onMount(() => {
		tween.done.then(() => props.oncomplete());
	});
	onDestroy(() => tween.stop());

	const covered = $derived(props.opening ? 1 - easeInCubic(tween.t) : easeOutCubic(tween.t));
	const draw = (amount: number) => (g: PIXI.Graphics) => {
		const { width, height } = context.stateLayoutDerived.canvasSizes();
		const half = (width / 2) * amount;
		g.rect(0, 0, half, height).fill(0x1a0b2e);
		g.rect(width - half, 0, half, height).fill(0x1a0b2e);
		// gold seams on the curtain edges
		g.rect(half - 6, 0, 6, height).fill(0xffc23a);
		g.rect(width - half, 0, 6, height).fill(0xffc23a);
	};
</script>

<Graphics draw={draw(covered)} />
<Container
	x={context.stateLayoutDerived.canvasSizes().width / 2}
	y={context.stateLayoutDerived.canvasSizes().height / 2}
	alpha={covered}
	rotation={(1 - covered) * Math.PI}
	scale={0.4 + covered * 0.6}
>
	<UiArt name="icon_bonus" width={180} height={180} />
</Container>
