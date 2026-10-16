<!-- A full-screen bonus splash covering the canvas, fully animated. The art is split into
     layers (art/make_splash_layers.py): signs swing on their chains, dumpsters chomp, the
     chest rattles, pumpkins and lanterns flicker, ghosts float, the bag beats like a heart.
     The whole picture lunges in out of the dark and keeps breathing; lightning strikes jolt
     it; SplashFx adds bats, ghosts, fog and a heartbeat vignette on top. The art has a blank
     plaque; the children snippet gets its rectangle in canvas px to draw the count / win on. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import type { Snippet } from 'svelte';
	import { onDestroy } from 'svelte';
	import { Container, Graphics, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { plaqueOnCanvas, SPLASH_IMAGE, type Rect, type SplashName } from '../game/splashes';
	import { SPLASH_LAYERS } from '../game/splashLayers';
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
	// the 2:3 art sits full height in the middle of the image
	const artH = $derived(image.h);
	const artW = $derived(image.h * (2 / 3));
	const px = $derived(artH / 1536); // one art pixel in image px

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
	const beat = $derived.by(() => {
		const p = (t % 1.3) / 1.3;
		return Math.max(0, 1 - Math.abs(p - 0.05) / 0.06) + Math.max(0, 1 - Math.abs(p - 0.2) / 0.06) * 0.7;
	});

	// entrance: lunge in from 125% out of black, a jolt as it lands, then a slow breathing zoom
	// (never below 1.02 so the breathing never shows the image edge)
	const enter = $derived(easeOutCubic(clamp01(t / 0.7)));
	const zoom = $derived(1.27 - 0.25 * enter + Math.sin(t * 0.9) * 0.012 + strike * 0.01);
	const jolt = $derived((t < 0.95 && t > 0.6 ? (0.95 - t) * 40 : 0) + strike * 9);
	const shakeX = $derived(Math.sin(t * 87) * jolt);
	const shakeY = $derived(Math.cos(t * 71) * jolt);
	const fadeIn = $derived(clamp01(t / 0.45));

	type Motion = { x: number; y: number; rotation: number; sx: number; sy: number; alpha: number; glow: number };
	const still: Motion = { x: 0, y: 0, rotation: 0, sx: 1, sy: 1, alpha: 1, glow: 0 };
	// each layer's motion at time t (offsets in art px), phase-shifted per layer
	const motion = (anim: string, ph: number): Motion => {
		const live = clamp01((t - 0.5) / 0.4); // parts come alive once the art has landed
		const m = { ...still };
		switch (anim) {
			case 'swing':
				m.rotation = (Math.sin(t * 1.5 + ph) * 0.03 + strike * Math.sin(t * 40) * 0.02) * live;
				break;
			case 'glow':
				m.sx = m.sy = 1 + Math.sin(t * 2 + ph) * 0.015 * live;
				m.glow = (0.12 + 0.12 * Math.sin(t * 2.3 + ph)) * live;
				break;
			case 'flicker':
				m.sx = m.sy = 1 + Math.sin(t * 3 + ph) * 0.02 * live;
				m.glow = (0.15 + 0.4 * Math.abs(Math.sin(t * 13 + ph) * Math.sin(t * 7.3 + ph * 2))) * live;
				break;
			case 'chomp': {
				const p = (t * 0.95 + ph * 0.3) % 1;
				const c = p < 0.2 ? Math.sin((p / 0.2) * Math.PI) * live : 0;
				m.sx = 1 - c * 0.045;
				m.sy = 1 + c * 0.07;
				m.y = -c * 16;
				m.rotation = Math.sin(t * 3 + ph) * 0.012 * live;
				break;
			}
			case 'breathe':
				m.sx = m.sy = 1 + Math.sin(t * 2.2 + ph) * 0.035 * live;
				m.glow = (0.1 + 0.18 * (Math.sin(t * 2.2 + ph) + 1) * 0.5 + beat * 0.15) * live;
				break;
			case 'float':
				m.y = Math.sin(t * 1.8 + ph) * 16 * live;
				m.x = Math.sin(t * 1.1 + ph) * 9 * live;
				m.rotation = Math.sin(t * 1.4 + ph) * 0.05 * live;
				m.alpha = 0.85 + 0.15 * Math.sin(t * 3 + ph);
				break;
			case 'pulse':
				m.sx = m.sy = 1 + beat * 0.045 * live;
				m.glow = beat * 0.25 * live;
				break;
			case 'spin':
				m.rotation = Math.sin(t * 2.6) * 0.22 * live;
				m.y = Math.sin(t * 2) * 12 * live;
				m.sx = m.sy = 1 + Math.sin(t * 4) * 0.05 * live;
				m.glow = (0.2 + 0.2 * Math.sin(t * 5)) * live;
				break;
			case 'rattle': {
				const q = t % 1.6;
				const r = q < 0.5 ? (1 - q / 0.5) * live : 0;
				m.rotation = Math.sin(t * 60) * 0.022 * r;
				m.x = Math.sin(t * 47) * 6 * r;
				m.y = -Math.abs(Math.sin(t * 30)) * 8 * r;
				m.glow = (0.1 + r * 0.3) * live;
				break;
			}
		}
		return m;
	};
</script>

<Container x={shakeX} y={shakeY}>
	<Container x={canvas.width / 2} y={canvas.height / 2} scale={scale * zoom} alpha={fadeIn}>
		<Sprite
			key={`fs_${props.name}_${portrait ? 'portrait' : 'landscape'}`}
			anchor={0.5}
			width={image.w}
			height={image.h}
			tint={strike > 0.4 ? 0xe6ecff : 0xffffff}
		/>
		{#each SPLASH_LAYERS[props.name] as layer, i}
			{@const m = motion(layer.anim, i * 1.7)}
			<Container
				x={(layer.px - 0.5) * artW + m.x * px}
				y={(layer.py - 0.5) * artH + m.y * px}
				rotation={m.rotation}
				scale={{ x: m.sx, y: m.sy }}
				alpha={m.alpha}
			>
				<Sprite
					key={layer.key}
					anchor={0.5}
					x={(layer.x - layer.px) * artW}
					y={(layer.y - layer.py) * artH}
					width={layer.w * artW}
					height={layer.h * artH}
				/>
				{#if m.glow > 0.01}
					<Sprite
						key={layer.key}
						anchor={0.5}
						x={(layer.x - layer.px) * artW}
						y={(layer.y - layer.py) * artH}
						width={layer.w * artW}
						height={layer.h * artH}
						alpha={m.glow}
						blendMode="add"
					/>
				{/if}
			</Container>
		{/each}
	</Container>
	<SplashFx name={props.name} width={canvas.width} height={canvas.height} {plaque} {clock} {strike} {strikeIndex} />
	{@render props.children?.({ plaque })}
</Container>
<!-- the screen starts black and the art "wakes up" out of the dark -->
<Graphics draw={(g: PIXI.Graphics) => { if (fadeIn < 1) g.rect(0, 0, canvas.width, canvas.height).fill({ color: 0x000000, alpha: 1 - fadeIn }); }} />
