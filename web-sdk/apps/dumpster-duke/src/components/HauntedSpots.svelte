<!--
	Haunted Spots on the board (cluster pays).
	  layer="tile"   behind the symbols: a ghostly green-purple glow on every haunted spot,
	                 burning hotter (purple -> orange -> red) as its multiplier grows
	  layer="badge"  above the symbols: the "x4" etc. badge on multiplier spots, which pops
	                 when the spot doubles
	Spots blink in with a flash when they change. State: game/hauntedSpots.svelte.ts.
-->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { BitmapText, Container, Graphics } from 'pixi-svelte';

	import { SYMBOL_SIZE } from '../game/constants';
	import { stateHauntedSpots } from '../game/hauntedSpots.svelte';
	import { getSymbolX, getSymbolY } from '../game/utils';
	import BoardContainer from './BoardContainer.svelte';
	import { createClock, easeOutBack } from './fx/timeline.svelte';

	type Props = { layer: 'tile' | 'badge' };
	const props: Props = $props();

	const clock = createClock();
	onDestroy(() => clock.stop());
	const t = $derived(clock.seconds);
	const now = $derived(performance.now() + t * 0); // re-evaluate every frame with the clock

	// colour by strength: haunted (1) ghost green, x2-x8 purple, x16-x32 orange, x64+ red
	const colour = (v: number) => (v <= 1 ? 0x6cff9a : v <= 8 ? 0xb44bff : v <= 32 ? 0xff8a1a : 0xff2a3a);
	const pop = (r: number, c: number) => {
		const age = (now - stateHauntedSpots.changedAt[r][c]) / 1000;
		return age < 0 || age > 0.6 ? 1 : easeOutBack(Math.min(1, age / 0.45), 3);
	};
	const flash = (r: number, c: number) => {
		const age = (now - stateHauntedSpots.changedAt[r][c]) / 1000;
		return age < 0 || age > 0.5 ? 0 : 1 - age / 0.5;
	};

	const drawTile = (v: number, r: number, c: number) => (g: PIXI.Graphics) => {
		const s = SYMBOL_SIZE * 0.96;
		const pulse = 0.75 + Math.sin(t * 2.4 + r * 0.9 + c * 1.3) * 0.25;
		const col = colour(v);
		const strength = v <= 1 ? 0.22 : Math.min(0.6, 0.3 + Math.log2(v) * 0.05);
		g.roundRect(-s / 2, -s / 2, s, s, s * 0.18).fill({ color: 0x14081f, alpha: 0.55 });
		for (let k = 3; k >= 1; k--) {
			const pad = k * 3;
			g.roundRect(-s / 2 + pad, -s / 2 + pad, s - pad * 2, s - pad * 2, s * 0.16).fill({
				color: col,
				alpha: strength * pulse * 0.35,
			});
		}
		g.roundRect(-s / 2 + 2, -s / 2 + 2, s - 4, s - 4, s * 0.16).stroke({ color: col, width: 3, alpha: 0.5 + pulse * 0.4 });
		const f = flash(r, c);
		if (f > 0) g.roundRect(-s / 2, -s / 2, s, s, s * 0.18).fill({ color: 0xffffff, alpha: f * 0.5 });
	};

	const drawBadge = (v: number) => (g: PIXI.Graphics) => {
		const w = SYMBOL_SIZE * (v >= 100 ? 0.56 : 0.46);
		const h = SYMBOL_SIZE * 0.3;
		g.roundRect(-w / 2, -h / 2, w, h, h * 0.45).fill({ color: 0x14081f, alpha: 0.9 }).stroke({ color: colour(v), width: 3 });
	};
</script>

<BoardContainer>
	{#each stateHauntedSpots.spots as reel, r}
		{#each reel as v, c}
			{#if v > 0}
				<Container x={getSymbolX(r)} y={getSymbolY(c)}>
					{#if props.layer === 'tile'}
						<Container scale={pop(r, c)}>
							<Graphics draw={drawTile(v, r, c)} />
						</Container>
					{:else if v >= 2}
						<Container x={SYMBOL_SIZE * 0.24} y={SYMBOL_SIZE * 0.33} scale={pop(r, c) * (1 + Math.sin(t * 3 + r + c) * 0.04)}>
							<Graphics draw={drawBadge(v)} />
							<BitmapText anchor={0.5} text={`X${v}`} style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * 0.24 }} />
						</Container>
					{/if}
				</Container>
			{/if}
		{/each}
	{/each}
</BoardContainer>
