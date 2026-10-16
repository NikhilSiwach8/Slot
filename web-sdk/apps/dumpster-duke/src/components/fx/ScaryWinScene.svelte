<!--
	Scary win scene behind the win title: the vampire dumpster (H1) bursts up out of a
	slimy aura, then keeps chomping (squash and stretch) with slime dripping off it.
	Each tier adds more:
	  0 good   aura, slime
	  1 big    + bats bursting out of the dumpster
	  2 super  + ghosts circling it
	  3 mega   + lightning flashes and a shaking screen
	  4 epic   + the werewolf possum and witch pigeon rising on either side
	  5 max    everything, bigger
	All positions are relative to the scene centre (the dumpster's resting point).
-->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { Container, Graphics, Sprite } from 'pixi-svelte';

	import { SYMBOL_INFO_MAP, SYMBOL_SIZE } from '../../game/constants';
	import { clamp01, easeOutBack, type Clock } from './timeline.svelte';

	type Props = { clock: Clock; tier: number; size?: number };
	const props: Props = $props();

	const S = $derived(props.size ?? SYMBOL_SIZE * 2.3); // dumpster size
	const t = $derived(props.clock.seconds);
	const tier = $derived(props.tier);
	const key = (name: string) => SYMBOL_INFO_MAP[name].static.assetKey;

	const rand = (i: number, k: number) => {
		const v = Math.sin(i * 127.1 + k * 311.7) * 43758.5453;
		return v - Math.floor(v);
	};

	// --- the dumpster: rise, then chomp every ~0.8 s ---
	const rise = $derived(easeOutBack(clamp01((t - 0.05) / 0.55), 1.8));
	const chomp = $derived.by(() => {
		const p = (t * (1.1 + tier * 0.12)) % 1;
		return t < 0.6 || p > 0.22 ? 0 : Math.sin((p / 0.22) * Math.PI);
	});
	const wobble = $derived(Math.sin(t * 6.5) * (0.035 + tier * 0.01));

	// --- lightning (mega+): a strike roughly every 1.6 s ---
	const strike = $derived.by(() => {
		if (tier < 3 || t < 0.4) return 0;
		const p = ((t - 0.4) % 1.6) / 1.6;
		const a = Math.max(0, 1 - Math.abs(p - 0.02) / 0.03);
		const b = Math.max(0, 1 - Math.abs(p - 0.1) / 0.06) * 0.7;
		return Math.max(a, b);
	});
	const strikeIndex = $derived(Math.floor(Math.max(0, t - 0.4) / 1.6));
	const shake = $derived(
		tier >= 3 ? (strike * 14 + (t < 0.7 ? (0.7 - t) * 30 : 0)) * (1 + (tier - 3) * 0.4) : t < 0.5 ? (0.5 - t) * 12 : 0,
	);
	const shakeX = $derived(Math.sin(t * 91) * shake);
	const shakeY = $derived(Math.cos(t * 77) * shake);

	// --- aura: layered purple/green glow pulsing behind the dumpster ---
	const drawAura = (g: PIXI.Graphics) => {
		const pulse = 1 + Math.sin(t * 4) * 0.06 + chomp * 0.08;
		const r = S * (0.75 + tier * 0.06) * pulse * rise;
		for (let k = 6; k >= 1; k--) {
			g.circle(0, 0, r * (0.45 + k * 0.12)).fill({ color: k % 2 ? 0x5b1f8f : 0x3fae2a, alpha: 0.07 });
		}
		g.circle(0, 0, r * 0.5).fill({ color: 0x9bff5a, alpha: 0.08 + chomp * 0.08 });
	};

	// --- slime: drops falling from the dumpster's bottom edge ---
	const drawSlime = (g: PIXI.Graphics) => {
		if (rise < 0.6) return;
		const n = 7 + tier * 2;
		for (let i = 0; i < n; i++) {
			const period = 0.9 + rand(i, 1) * 0.8;
			const u = ((t + rand(i, 2) * period) % period) / period;
			const x = (rand(i, 3) - 0.5) * S * 0.75;
			const y = S * 0.38 + u * u * S * 0.9;
			const r = (5 + rand(i, 4) * 6) * (1 - u * 0.5);
			g.circle(x, y, r).fill({ color: 0x7ee03a, alpha: 0.9 * (1 - u) });
			g.poly([x - r * 0.7, y - r * 0.3, x, y - r * 2.4, x + r * 0.7, y - r * 0.3]).fill({
				color: 0x7ee03a,
				alpha: 0.9 * (1 - u),
			});
		}
	};

	// --- bats (big+): burst out of the dumpster, then keep streaming ---
	const bats = $derived(
		Array.from({ length: 6 + tier * 3 }, (_, i) => {
			const period = 1.8 + rand(i, 5) * 1.2;
			const start = 0.35 + rand(i, 6) * 0.4;
			const local = t - start;
			if (local < 0) return null;
			const u = (local % period) / period;
			const angle = -Math.PI / 2 + (rand(i, 7) - 0.5) * Math.PI * 1.5;
			const dist = u * S * (2.2 + rand(i, 8));
			return {
				x: Math.cos(angle) * dist + Math.sin(u * 9 + i) * 18,
				y: Math.sin(angle) * dist * 0.8 - S * 0.1,
				scale: (0.7 + rand(i, 9) * 0.9) * (0.4 + u * 0.8),
				alpha: u < 0.85 ? 1 : (1 - u) / 0.15,
				flip: Math.cos(angle) < 0 ? -1 : 1,
				flap: Math.sin(t * (16 + rand(i, 10) * 6) + i),
			};
		}).filter((b) => b !== null),
	);
	const drawBat = (flap: number) => (g: PIXI.Graphics) => {
		const lift = flap * 16;
		const wing = (s: number) => [0, -2, s * 14, -8 - lift * 0.4, s * 30, -10 - lift, s * 44, -2 - lift * 0.6, s * 36, 4, s * 28, 1, s * 20, 7, s * 12, 3, 0, 5];
		g.poly(wing(1)).fill(0x0d0716);
		g.poly(wing(-1)).fill(0x0d0716);
		g.ellipse(0, 2, 7, 11).fill(0x0d0716);
		g.circle(-2.6, -3, 1.9).fill(0xff3b1a);
		g.circle(2.6, -3, 1.9).fill(0xff3b1a);
	};

	// --- ghosts (super+): wisps circling the dumpster ---
	const ghosts = $derived(
		Array.from({ length: tier >= 2 ? 3 + (tier - 2) * 2 : 0 }, (_, i) => {
			const a = t * (0.9 + rand(i, 11) * 0.5) * (i % 2 ? 1 : -1) + (i / 3) * Math.PI * 2;
			const fade = clamp01((t - 0.5 - i * 0.12) / 0.5);
			return {
				x: Math.cos(a) * S * (0.95 + rand(i, 12) * 0.3),
				y: Math.sin(a) * S * 0.42 - S * 0.05,
				alpha: fade * (0.55 + Math.sin(t * 3 + i) * 0.2),
				scale: (0.55 + rand(i, 13) * 0.3) * (Math.sin(a) > 0 ? 1.1 : 0.85),
				front: Math.sin(a) > 0,
				wave: t * 6 + i,
			};
		}),
	);
	const drawGhost = (wave: number) => (g: PIXI.Graphics) => {
		g.ellipse(0, 0, 70, 80).fill({ color: 0xb8ffd0, alpha: 0.08 });
		const outline: number[] = [];
		for (let k = 0; k <= 10; k++) {
			const a = Math.PI + (k / 10) * Math.PI;
			outline.push(Math.cos(a) * 38, Math.sin(a) * 42 - 4);
		}
		for (let k = 1; k < 7; k++) outline.push(38 - k * 12.6, 46 + Math.sin(k * 1.5 + wave) * 6 + (k % 2 ? 8 : 0));
		g.poly(outline).fill({ color: 0xe6fff0, alpha: 0.85 });
		g.ellipse(-13, -8, 7, 10).fill(0x10081a);
		g.ellipse(13, -8, 7, 10).fill(0x10081a);
		g.ellipse(0, 14, 8, 11 + Math.sin(wave) * 3).fill(0x10081a);
	};

	// --- lightning bolts (mega+) ---
	const drawBolt = (g: PIXI.Graphics) => {
		if (strike <= 0.05) return;
		for (let b = 0; b < 2; b++) {
			const side = (strikeIndex + b) % 2 ? 1 : -1;
			let x = side * S * (0.9 + rand(strikeIndex, b) * 0.6);
			let y = -S * 2.2;
			const pts = [x, y];
			for (let k = 0; k < 9; k++) {
				x += (rand(strikeIndex * 13 + k, b + 3) - 0.5) * S * 0.35;
				y += S * 0.26;
				pts.push(x, y);
			}
			g.poly(pts, false).stroke({ color: 0xd9f6ff, width: 7, alpha: strike });
			g.poly(pts, false).stroke({ color: 0x9a6bff, width: 22, alpha: strike * 0.35 });
		}
	};
	const drawFlash = (g: PIXI.Graphics) => {
		if (strike <= 0.05) return;
		g.rect(-S * 8, -S * 6, S * 16, S * 12).fill({ color: 0xcfd8ff, alpha: strike * 0.22 });
	};

	// --- side monsters (epic+): werewolf possum and witch pigeon rise and lurch ---
	const sideRise = $derived(tier >= 4 ? easeOutBack(clamp01((t - 0.55) / 0.6), 1.6) : 0);
</script>

<Container x={shakeX} y={shakeY}>
	<Graphics draw={drawFlash} />
	<Graphics draw={drawAura} />

	{#each ghosts.filter((g) => !g.front) as ghost}
		<Container x={ghost.x} y={ghost.y} scale={ghost.scale} alpha={ghost.alpha}>
			<Graphics draw={drawGhost(ghost.wave)} />
		</Container>
	{/each}

	{#if sideRise > 0}
		{#each [{ name: 'H2', side: -1, phase: 0 }, { name: 'H3', side: 1, phase: 1.7 }] as monster}
			{@const lurch = Math.sin(t * 5 + monster.phase)}
			<Container
				x={monster.side * S * 1.05}
				y={S * 0.25 + (1 - sideRise) * S * 1.2 + Math.abs(lurch) * -8}
				rotation={monster.side * (0.12 + lurch * 0.06)}
				alpha={clamp01(sideRise * 1.5)}
			>
				<Sprite key={key(monster.name)} anchor={0.5} width={S * 0.78} height={S * 0.78} tint={0xffd2d2} />
			</Container>
		{/each}
	{/if}

	<!-- the vampire dumpster -->
	<Container y={(1 - rise) * S * 1.4 - chomp * 22} rotation={wobble} alpha={clamp01(rise * 2)}>
		<Container scale={{ x: (1 - chomp * 0.1) * Math.max(0.01, rise), y: (1 + chomp * 0.14) * Math.max(0.01, rise) }}>
			<Sprite
				key={key('H1')}
				anchor={0.5}
				width={S}
				height={S}
				tint={strike > 0.3 ? 0xd8e4ff : chomp > 0.5 ? 0xffe0c0 : 0xffffff}
			/>
		</Container>
	</Container>

	<Graphics draw={drawSlime} />

	{#each ghosts.filter((g) => g.front) as ghost}
		<Container x={ghost.x} y={ghost.y} scale={ghost.scale} alpha={ghost.alpha}>
			<Graphics draw={drawGhost(ghost.wave)} />
		</Container>
	{/each}

	{#if tier >= 1}
		{#each bats as bat}
			<Container x={bat.x} y={bat.y} scale={{ x: bat.scale * bat.flip, y: bat.scale }} alpha={bat.alpha}>
				<Graphics draw={drawBat(bat.flap)} />
			</Container>
		{/each}
	{/if}

	<Graphics draw={drawBolt} />
</Container>
