<!-- Faint ghosts drifting through the background now and then: they fade in, wobble along a
     slow path with a waving tail, and fade out again. -->
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
		const v = Math.sin(i * 91.7 + k * 47.3) * 43758.5453;
		return v - Math.floor(v);
	};
	const ghosts = Array.from({ length: props.count ?? 3 }, (_, i) => ({
		period: 16 + rand(i, 1) * 10,
		life: 9 + rand(i, 2) * 4,
		offset: rand(i, 3) * 20,
		// keep to the sides of the screen so a ghost never drifts behind the reels
		x: i % 2 ? 0.78 + rand(i, 4) * 0.14 : 0.06 + rand(i, 4) * 0.14,
		y: 0.2 + rand(i, 5) * 0.5,
		dir: rand(i, 6) > 0.5 ? 1 : -1,
		size: 0.8 + rand(i, 7) * 0.6,
	}));

	const drawGhost = (wave: number) => (g: PIXI.Graphics) => {
		// soft halo
		for (let k = 4; k >= 1; k--) g.ellipse(0, 0, 46 + k * 10, 58 + k * 10).fill({ color: 0xc9d8ff, alpha: 0.04 });
		// body: round head, straight sides, wavy hem — one closed outline
		const outline: number[] = [];
		for (let k = 0; k <= 12; k++) {
			const a = Math.PI + (k / 12) * Math.PI;
			outline.push(Math.cos(a) * 40, -10 + Math.sin(a) * 40);
		}
		outline.push(40, 50);
		for (let k = 1; k < 8; k++) outline.push(40 - k * 10, 50 + Math.sin(k * 1.4 + wave) * 6 + (k % 2 ? 9 : 0));
		outline.push(-40, 50);
		g.poly(outline);
		g.fill({ color: 0xeef2ff, alpha: 0.8 });
		// face
		g.ellipse(-14, -14, 7, 10).fill({ color: 0x1a1030, alpha: 0.85 });
		g.ellipse(14, -14, 7, 10).fill({ color: 0x1a1030, alpha: 0.85 });
		g.ellipse(0, 12, 8, 11 + Math.sin(wave) * 2).fill({ color: 0x1a1030, alpha: 0.8 });
	};
</script>

{#each ghosts as ghost, i}
	{@const t = (clock.seconds + ghost.offset) % ghost.period}
	{#if t < ghost.life}
		{@const u = t / ghost.life}
		<Container
			x={props.width * ghost.x + ghost.dir * (u - 0.5) * props.width * 0.08}
			y={props.height * ghost.y + Math.sin(clock.seconds * 1.3 + i) * props.height * 0.025}
			scale={{ x: ghost.size * ghost.dir * (props.height / 1080), y: ghost.size * (props.height / 1080) }}
			rotation={Math.sin(clock.seconds * 0.9 + i) * 0.08}
			alpha={Math.sin(u * Math.PI) * 0.32}
		>
			<Graphics draw={drawGhost(clock.seconds * 3 + i)} />
		</Container>
	{/if}
{/each}
