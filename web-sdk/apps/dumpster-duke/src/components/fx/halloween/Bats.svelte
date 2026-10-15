<!-- Bats flapping across the screen now and then, each on its own path and timing. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { Container, Graphics } from 'pixi-svelte';

	import { createClock } from '../timeline.svelte';

	type Props = { width: number; height: number; count?: number };
	const props: Props = $props();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const rand = (i: number, k: number) => {
		const v = Math.sin(i * 127.1 + k * 311.7) * 43758.5453;
		return v - Math.floor(v);
	};
	const bats = Array.from({ length: props.count ?? 6 }, (_, i) => ({
		period: 9 + rand(i, 1) * 10, // seconds between passes
		flight: 4 + rand(i, 2) * 3, // seconds on screen
		offset: rand(i, 3) * 12,
		y: 0.08 + rand(i, 4) * 0.42,
		dir: rand(i, 5) > 0.5 ? 1 : -1,
		size: 0.6 + rand(i, 6) * 0.7,
		flap: 9 + rand(i, 7) * 5,
	}));

	const drawBat = (flap: number) => (g: PIXI.Graphics) => {
		const lift = flap * 18;
		const wing = (s: number) => [
			0, -2,
			s * 14, -8 - lift * 0.4,
			s * 30, -10 - lift,
			s * 46, -2 - lift * 0.6,
			s * 38, 4 - lift * 0.2,
			s * 30, 1,
			s * 22, 7,
			s * 14, 3,
			0, 5,
		];
		g.poly(wing(1)).fill(0x120a1c);
		g.poly(wing(-1)).fill(0x120a1c);
		g.ellipse(0, 2, 7, 11).fill(0x120a1c);
		g.poly([-6, -7, -4, -15, -1, -8, 1, -8, 4, -15, 6, -7]).fill(0x120a1c);
		g.circle(-2.5, -3, 1.6).fill(0xff7a1a);
		g.circle(2.5, -3, 1.6).fill(0xff7a1a);
	};
</script>

{#each bats as bat}
	{@const t = (clock.seconds + bat.offset) % bat.period}
	{#if t < bat.flight}
		{@const u = t / bat.flight}
		{@const x = bat.dir > 0 ? -80 + u * (props.width + 160) : props.width + 80 - u * (props.width + 160)}
		{@const y = props.height * bat.y + Math.sin(u * Math.PI * 3) * props.height * 0.04}
		<Container {x} {y} scale={{ x: bat.size * 1.2 * bat.dir, y: bat.size * 1.2 }}>
			<Graphics draw={drawBat(Math.sin(clock.seconds * bat.flap))} />
		</Container>
	{/if}
{/each}
