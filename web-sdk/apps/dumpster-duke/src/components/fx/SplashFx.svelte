<!--
	Scary animation layer over a bonus splash (drawn in canvas px over the art):
	  raid     orange storm: bats bursting out of the dumpster, embers, a lightning strike now and then
	  super    purple storm: frequent lightning with screen flashes, ghosts circling, bats
	  mystery  toxic green: pulsing slime glow, floating "?" marks, ghosts rising, green fog
	  outro    gold haul: ghosts drifting away, embers, bats leaving
	Every splash also gets a heartbeat vignette and a glow pulsing around the plaque.
-->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { BitmapText, Container, Graphics } from 'pixi-svelte';

	import type { Rect, SplashName } from '../../game/splashes';
	import Embers from './halloween/Embers.svelte';
	import Fog from './halloween/Fog.svelte';
	import { clamp01, type Clock } from './timeline.svelte';

	type Props = { name: SplashName; width: number; height: number; plaque: Rect; clock: Clock; strike: number; strikeIndex: number };
	const props: Props = $props();

	const t = $derived(props.clock.seconds);
	const W = $derived(props.width);
	const H = $derived(props.height);
	const u = $derived(Math.min(W, H) / 1080); // 1 at 1080 px
	const LOOK = {
		raid: { glow: 0xff7a1a, bats: 10, ghosts: 0, marks: 0 },
		super: { glow: 0xb04bff, bats: 8, ghosts: 5, marks: 0 },
		mystery: { glow: 0x7dff3a, bats: 0, ghosts: 4, marks: 9 },
		outro: { glow: 0xffc84a, bats: 6, ghosts: 3, marks: 0 },
	} as const;
	const look = $derived(LOOK[props.name]);

	const rand = (i: number, k: number) => {
		const v = Math.sin(i * 127.1 + k * 311.7) * 43758.5453;
		return v - Math.floor(v);
	};

	// heartbeat: two quick thumps every 1.3 s
	const beat = $derived.by(() => {
		const p = (t % 1.3) / 1.3;
		return Math.max(0, 1 - Math.abs(p - 0.05) / 0.06) + Math.max(0, 1 - Math.abs(p - 0.2) / 0.06) * 0.7;
	});

	const drawVignette = (g: PIXI.Graphics) => {
		const a = 0.32 + beat * 0.18;
		const band = Math.min(W, H) * 0.06;
		for (let k = 0; k < 5; k++) {
			const inset = band * k;
			g.rect(inset, inset, W - inset * 2, H - inset * 2).stroke({ color: 0x07020c, width: band, alpha: a * (1 - k * 0.2) });
		}
	};

	const drawPlaqueGlow = (g: PIXI.Graphics) => {
		const pulse = 0.6 + Math.sin(t * 3.2) * 0.25 + beat * 0.25;
		const { x, y, width, height } = props.plaque;
		for (let k = 4; k >= 1; k--) {
			g.ellipse(x, y, width * (0.5 + k * 0.09), height * (0.6 + k * 0.32)).fill({ color: look.glow, alpha: 0.05 * pulse });
		}
	};

	// bats burst from the centre of the art and fly out past the edges, over and over
	const bats = $derived(
		Array.from({ length: look.bats }, (_, i) => {
			const period = 2.4 + rand(i, 1) * 1.6;
			const local = t - 0.2 - rand(i, 2) * 1.2;
			if (local < 0) return null;
			const p = (local % period) / period;
			const angle = -Math.PI / 2 + (rand(i, 3) - 0.5) * Math.PI * 1.6;
			const dist = p * Math.max(W, H) * 0.75;
			return {
				x: W / 2 + Math.cos(angle) * dist + Math.sin(p * 10 + i) * 20 * u,
				y: H * 0.55 + Math.sin(angle) * dist * 0.85,
				scale: u * (0.8 + rand(i, 4)) * (0.4 + p * 1.6),
				flip: Math.cos(angle) < 0 ? -1 : 1,
				flap: Math.sin(t * (15 + rand(i, 5) * 6) + i),
				alpha: Math.min(1, p * 6),
			};
		}).filter((b) => b !== null),
	);
	const drawBat = (flap: number) => (g: PIXI.Graphics) => {
		const lift = flap * 16;
		const wing = (s: number) => [0, -2, s * 14, -8 - lift * 0.4, s * 30, -10 - lift, s * 44, -2 - lift * 0.6, s * 36, 4, s * 28, 1, s * 20, 7, s * 12, 3, 0, 5];
		g.poly(wing(1)).fill(0x0b0612);
		g.poly(wing(-1)).fill(0x0b0612);
		g.ellipse(0, 2, 7, 11).fill(0x0b0612);
		g.circle(-2.6, -3, 2).fill(0xff3b1a);
		g.circle(2.6, -3, 2).fill(0xff3b1a);
	};

	// ghosts: rise from the bottom and sway (super: they circle the plaque instead)
	const ghosts = $derived(
		Array.from({ length: look.ghosts }, (_, i) => {
			const fade = clamp01((t - 0.4 - i * 0.25) / 0.6);
			if (props.name === 'super') {
				const a = t * 0.8 * (i % 2 ? 1 : -1) + (i / look.ghosts) * Math.PI * 2;
				// fade out while crossing the middle so they never cover the plaque or the art's centre
				const side = clamp01((Math.abs(Math.cos(a)) - 0.45) / 0.3);
				return {
					x: props.plaque.x + Math.cos(a) * props.plaque.width * 0.95,
					y: props.plaque.y + Math.sin(a) * props.plaque.height * 2.2,
					scale: u * (0.8 + rand(i, 6) * 0.4),
					alpha: fade * 0.75 * side,
					wave: t * 6 + i,
				};
			}
			const period = 5 + rand(i, 7) * 3;
			const p = ((t + rand(i, 8) * period) % period) / period;
			return {
				// rise along the sides of the screen, clear of the plaque
				x: (i % 2 ? W * (0.72 + rand(i, 9) * 0.2) : W * (0.08 + rand(i, 9) * 0.2)) + Math.sin(t * 1.3 + i) * 30 * u,
				y: H * (1.08 - p * 1.25),
				scale: u * (0.7 + rand(i, 10) * 0.6),
				alpha: fade * Math.sin(p * Math.PI) * 0.7,
				wave: t * 6 + i,
			};
		}),
	);
	const drawGhost = (wave: number) => (g: PIXI.Graphics) => {
		g.ellipse(0, 0, 72, 84).fill({ color: 0xc9ffe0, alpha: 0.07 });
		const outline: number[] = [];
		for (let k = 0; k <= 10; k++) {
			const a = Math.PI + (k / 10) * Math.PI;
			outline.push(Math.cos(a) * 38, Math.sin(a) * 42 - 4);
		}
		for (let k = 1; k < 7; k++) outline.push(38 - k * 12.6, 46 + Math.sin(k * 1.5 + wave) * 6 + (k % 2 ? 8 : 0));
		g.poly(outline).fill({ color: 0xeefff4, alpha: 0.85 });
		g.ellipse(-13, -8, 7, 10).fill(0x10081a);
		g.ellipse(13, -8, 7, 10).fill(0x10081a);
		g.ellipse(0, 14, 8, 11 + Math.sin(wave) * 3).fill(0x10081a);
	};

	// mystery: glowing "?" marks drifting up and spinning
	const marks = $derived(
		Array.from({ length: look.marks }, (_, i) => {
			const period = 3.5 + rand(i, 11) * 2.5;
			const p = ((t + rand(i, 12) * period) % period) / period;
			return {
				// drift up the sides, clear of the plaque
				x: i % 2 ? W * (0.72 + rand(i, 13) * 0.22) : W * (0.06 + rand(i, 13) * 0.22),
				y: H * (0.95 - p * 0.9),
				rotation: Math.sin(t * 2 + i) * 0.5,
				scale: u * (0.6 + rand(i, 14) * 0.8),
				alpha: Math.sin(p * Math.PI) * 0.9,
			};
		}),
	);

	// lightning bolt from the top of the screen (strike timing comes from Splash)
	const drawBolt = (g: PIXI.Graphics) => {
		if (props.strike <= 0.05) return;
		const i = props.strikeIndex;
		let x = W * (0.15 + rand(i, 15) * 0.7);
		let y = 0;
		const pts = [x, y];
		for (let k = 0; k < 11; k++) {
			x += (rand(i * 17 + k, 16) - 0.5) * W * 0.07;
			y += H * 0.065;
			pts.push(x, y);
		}
		const colour = props.name === 'mystery' ? 0xb6ff8a : props.name === 'super' ? 0xe0c8ff : 0xfff1d6;
		g.poly(pts, false).stroke({ color: colour, width: 26 * u, alpha: props.strike * 0.3 });
		g.poly(pts, false).stroke({ color: 0xffffff, width: 7 * u, alpha: props.strike });
		g.rect(0, 0, W, H).fill({ color: colour, alpha: props.strike * 0.18 });
	};
</script>

<Graphics draw={drawPlaqueGlow} />

{#if props.name === 'mystery'}
	<Fog width={W} height={H} variant="ground" alpha={0.9} />
{:else}
	<Fog width={W} height={H} variant="ground" alpha={0.6} />
{/if}
{#if props.name === 'raid' || props.name === 'outro'}
	<Embers width={W} height={H} count={props.name === 'outro' ? 40 : 28} />
{/if}

{#each ghosts as ghost}
	<Container x={ghost.x} y={ghost.y} scale={ghost.scale} alpha={ghost.alpha}>
		<Graphics draw={drawGhost(ghost.wave)} />
	</Container>
{/each}

{#each marks as mark}
	<Container x={mark.x} y={mark.y} rotation={mark.rotation} scale={mark.scale} alpha={mark.alpha}>
		<BitmapText anchor={0.5} text="?" style={{ fontFamily: 'gold', fontSize: 110 }} tint={0x9dff6a} />
	</Container>
{/each}

{#each bats as bat}
	<Container x={bat.x} y={bat.y} scale={{ x: bat.scale * bat.flip, y: bat.scale }} alpha={bat.alpha}>
		<Graphics draw={drawBat(bat.flap)} />
	</Container>
{/each}

<Graphics draw={drawBolt} />
<Graphics draw={drawVignette} />
