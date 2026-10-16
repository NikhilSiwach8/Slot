<!-- A full-screen bonus splash covering the canvas, animated: the art lunges in out of the
     dark with a jolt, then keeps slowly breathing while SplashFx adds the scary layer
     (bats, ghosts, lightning, fog, a heartbeat vignette). The art has a blank plaque; the
     children snippet gets its rectangle in canvas px to draw the spin count / win on. -->
<script lang="ts">
	import type { Snippet } from 'svelte';
	import { onDestroy } from 'svelte';
	import type * as PIXI from 'pixi.js';
	import { Container, Graphics, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { plaqueOnCanvas, SPLASH_IMAGE, type Rect, type SplashName } from '../game/splashes';
	import SplashFx from './fx/SplashFx.svelte';
	import { clamp01, createClock, easeOutCubic } from './fx/timeline.svelte';

	type Props = { name: SplashName; children?: Snippet<[{ plaque: Rect }]> };
	const props: Props = $props();

	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const portrait = $derived(canvas.width / canvas.height < 1);
	const image = $derived(portrait ? SPLASH_IMAGE.portrait : SPLASH_IMAGE.landscape);
	const scale = $derived(Math.max(canvas.width / image.w, canvas.height / image.h));
	const plaque = $derived(plaqueOnCanvas(props.name, canvas));
	const t = $derived(clock.seconds);

	// lightning: how often each splash gets a strike (0 = never)
	const STRIKE_PERIOD: Record<SplashName, number> = { raid: 3.2, super: 1.7, mystery: 2.6, outro: 0 };
	const period = $derived(STRIKE_PERIOD[props.name]);
	const strikeIndex = $derived(period ? Math.floor(Math.max(0, t - 0.9) / period) : 0);
	const strike = $derived.by(() => {
		if (!period || t < 0.9) return 0;
		const p = ((t - 0.9) % period) / period;
		const a = Math.max(0, 1 - Math.abs(p * period - 0.04) / 0.05);
		const b = Math.max(0, 1 - Math.abs(p * period - 0.2) / 0.1) * 0.6;
		return Math.max(a, b);
	});

	// entrance: lunge in from 125% out of black, a jolt as it lands, then a slow breathing zoom
	const enter = $derived(easeOutCubic(clamp01(t / 0.7)));
	// never below 1.02 so the breathing never shows the image edge
	const zoom = $derived(1.27 - 0.25 * enter + Math.sin(t * 0.9) * 0.012 + strike * 0.01);
	const jolt = $derived((t < 0.95 && t > 0.6 ? (0.95 - t) * 40 : 0) + strike * 9);
	const shakeX = $derived(Math.sin(t * 87) * jolt);
	const shakeY = $derived(Math.cos(t * 71) * jolt);
	const fadeIn = $derived(clamp01(t / 0.45));
</script>

<Container x={shakeX} y={shakeY}>
	<Sprite
		key={`fs_${props.name}_${portrait ? 'portrait' : 'landscape'}`}
		anchor={0.5}
		x={canvas.width / 2}
		y={canvas.height / 2}
		width={image.w * scale * zoom}
		height={image.h * scale * zoom}
		alpha={fadeIn}
		tint={strike > 0.4 ? 0xe6ecff : 0xffffff}
	/>
	<SplashFx name={props.name} width={canvas.width} height={canvas.height} {plaque} {clock} {strike} {strikeIndex} />
	{@render props.children?.({ plaque })}
</Container>
<!-- the screen starts black and the art "wakes up" out of the dark -->
<Graphics draw={(g: PIXI.Graphics) => { if (fadeIn < 1) g.rect(0, 0, canvas.width, canvas.height).fill({ color: 0x000000, alpha: 1 - fadeIn }); }} />
