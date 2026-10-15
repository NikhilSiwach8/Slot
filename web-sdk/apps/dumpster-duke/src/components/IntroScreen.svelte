<!--
	Intro screen shown after loading ("press anywhere to continue"): the DUMPSTER DUKE logo
	over the mine background and three feature panels drawn as little dumpsters with
	slime-dripping lids:
	  1. Bottle Caps up to 100x multiply every win
	  2. 4+ Golden Trash Cans trigger the Midnight Raid (Loot Bag never resets)
	  3. Max win 10,000x
	Landscape: panels in a row. Portrait: wide panels stacked, icons left of the text.
-->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { BitmapText, Container, Graphics, Sprite, Text } from 'pixi-svelte';
	import { MainContainer } from 'components-layout';

	import { getContext } from '../game/context';
	import { SYMBOL_INFO_MAP } from '../game/constants';
	import { socialText } from '../game/social';
	import CoverImage from './CoverImage.svelte';
	import Rays from './fx/Rays.svelte';
	import { createClock, easeOutBack } from './fx/timeline.svelte';

	const context = getContext();
	const clock = createClock();
	onDestroy(() => clock.stop());

	const layout = $derived(context.stateLayoutDerived.mainLayout());
	const landscape = $derived(layout.width >= layout.height);

	// panel sizes in layout px
	const TALL = { width: 470, height: 540 };
	const WIDE = { width: 900, height: 330 };

	const key = (name: string) => SYMBOL_INFO_MAP[name]?.static.assetKey ?? SYMBOL_INFO_MAP.H1.static.assetKey;
	const textStyle = (size: number) => ({
		fontFamily: 'Arial Black, Arial, sans-serif',
		fontWeight: '900',
		fontSize: size,
		fill: 0xfff6e6,
		align: 'center',
		stroke: { color: 0x1a0b06, width: size * 0.22, join: 'round' },
		dropShadow: { color: 0x000000, alpha: 0.55, distance: 3, blur: 2, angle: Math.PI / 2 },
	}) as const;

	type Feature = { lines: string[]; icons?: string[]; title?: string[] };
	const FEATURES: Feature[] = [
		{ icons: ['M_100', 'H1'], lines: ['BOTTLE CAPS UP TO 100X', 'MULTIPLY EVERY WIN'] },
		{ icons: ['S', 'S', 'S'], lines: ['4+ GOLDEN TRASH CANS', 'TRIGGER THE MIDNIGHT RAID', 'THE LOOT BAG NEVER RESETS'] },
		{ title: ['MAX', 'WIN'], lines: ['UNLOCK A MASSIVE', '10,000X MAX WIN'] },
	];

	/** A dumpster: slate body with ribs and a gold frame, slimy green lid, wheels. */
	const drawDumpster = (w: number, h: number) => (g: PIXI.Graphics) => {
		const lidH = h * 0.14;
		const top = -h / 2 + lidH * 0.7;
		const r = Math.min(w, h) * 0.08;
		// shadow + wheels
		g.ellipse(0, h / 2 + 10, w * 0.46, 22).fill({ color: 0x000000, alpha: 0.4 });
		for (const x of [-w * 0.34, w * 0.34]) g.circle(x, h / 2 - 4, h * 0.05).fill(0x1a1a22).stroke({ color: 0x5a5f6e, width: 5 });
		// body
		g.roundRect(-w / 2, top, w, h / 2 - top, r).fill(0x3b4150).stroke({ color: 0x14161c, width: 6 });
		for (let i = 1; i < 6; i++) {
			const x = -w / 2 + (w * i) / 6;
			g.rect(x - 3, top + 14, 6, h / 2 - top - 28).fill({ color: 0x000000, alpha: 0.18 });
		}
		// gold frame + dark label plate
		g.roundRect(-w / 2 + 14, top + 14, w - 28, h / 2 - top - 28, r * 0.7).stroke({ color: 0xf2b33d, width: 6 });
		g.roundRect(-w / 2 + 26, top + 26, w - 52, h / 2 - top - 52, r * 0.6).fill({ color: 0x1d1033, alpha: 0.82 });
		// lid with slime drips
		g.roundRect(-w / 2 - 18, -h / 2, w + 36, lidH, lidH * 0.35).fill(0x4f9a24).stroke({ color: 0x1d3a0e, width: 6 });
		g.roundRect(-w / 2 - 6, -h / 2 + 6, w + 12, lidH * 0.32, lidH * 0.16).fill({ color: 0xbff28a, alpha: 0.35 });
		const drips = [-0.38, -0.12, 0.2, 0.41];
		drips.forEach((p, i) => {
			const x = p * w;
			const len = lidH * (0.7 + (i % 2) * 0.6);
			g.roundRect(x - 9, -h / 2 + lidH - 6, 18, len, 9).fill(0x6cc23a);
			g.circle(x, -h / 2 + lidH - 6 + len, 12).fill(0x6cc23a);
		});
	};

	const bob = (i: number) => Math.sin(clock.seconds * 1.6 + i * 1.3) * 8;
	const pop = (i: number) => easeOutBack(Math.min(1, Math.max(0, (clock.seconds - 0.15 - i * 0.12) / 0.5)), 2);
</script>

<CoverImage name="bg_base" />

<MainContainer>
	{#if landscape}
		{@const scale = Math.min(layout.width / 1750, (layout.height * 0.47) / TALL.height)}
		<!-- logo -->
		<Container x={layout.width / 2} y={layout.height * 0.19 + Math.sin(clock.seconds * 1.2) * 6} scale={pop(0)}>
			<Rays radius={330} alpha={0.55} />
			<Sprite key="duke_logo" anchor={0.5} width={layout.height * 0.36} height={layout.height * 0.36} />
		</Container>
		<!-- three panels in a row -->
		{#each FEATURES as feature, i}
			<Container
				x={layout.width / 2 + (i - 1) * 540 * scale}
				y={layout.height * 0.6 + bob(i)}
				scale={scale * pop(i + 1)}
			>
				<Graphics draw={drawDumpster(TALL.width, TALL.height)} />
				{#if feature.icons}
					{#each feature.icons as icon, k}
						{@const n = feature.icons.length}
						<Container x={(k - (n - 1) / 2) * (n === 3 ? 120 : 165)} y={-40 + (n === 3 && k === 1 ? -14 : 0)}>
							<Sprite key={key(icon)} anchor={0.5} width={n === 3 ? 150 : 175} height={n === 3 ? 150 : 175} />
							{#if icon.startsWith('M_')}
								<BitmapText anchor={0.5} y={-4} text={`${icon.slice(2)}x`} style={{ fontFamily: 'gold', fontSize: 52 }} />
							{/if}
						</Container>
					{/each}
				{:else if feature.title}
					<BitmapText anchor={0.5} y={-112} text={socialText(feature.title[0])} style={{ fontFamily: 'gold', fontSize: 108 }} />
					<BitmapText anchor={0.5} y={-12} text={socialText(feature.title[1])} style={{ fontFamily: 'gold', fontSize: 108 }} />
				{/if}
				{#each feature.lines as line, k}
					<Text anchor={0.5} y={92 + k * 46 - (feature.lines.length - 2) * 14} text={socialText(line)} style={textStyle(feature.lines.length > 2 ? 27 : 31)} />
				{/each}
			</Container>
		{/each}
	{:else}
		{@const scale = Math.min(layout.width / 960, (layout.height * 0.18) / WIDE.height)}
		<Container x={layout.width / 2} y={layout.height * 0.16} scale={pop(0)}>
			<Rays radius={layout.width * 0.42} alpha={0.55} />
			<Sprite key="duke_logo" anchor={0.5} width={layout.width * 0.66} height={layout.width * 0.66} />
		</Container>
		<!-- wide panels stacked: icons on the left, text on the right -->
		{#each FEATURES as feature, i}
			<Container x={layout.width / 2} y={layout.height * (0.42 + i * 0.19) + bob(i)} scale={scale * pop(i + 1)}>
				<Graphics draw={drawDumpster(WIDE.width, WIDE.height)} />
				<Container x={-WIDE.width * 0.26} y={20}>
					{#if feature.icons}
						{#each feature.icons as icon, k}
							{@const n = feature.icons.length}
							<Container x={(k - (n - 1) / 2) * (n === 3 ? 82 : 120)}>
								<Sprite key={key(icon)} anchor={0.5} width={n === 3 ? 115 : 135} height={n === 3 ? 115 : 135} />
								{#if icon.startsWith('M_')}
									<BitmapText anchor={0.5} y={-3} text={`${icon.slice(2)}x`} style={{ fontFamily: 'gold', fontSize: 40 }} />
								{/if}
							</Container>
						{/each}
					{:else if feature.title}
						<BitmapText anchor={0.5} y={-40} text={socialText(feature.title[0])} style={{ fontFamily: 'gold', fontSize: 82 }} />
						<BitmapText anchor={0.5} y={36} text={socialText(feature.title[1])} style={{ fontFamily: 'gold', fontSize: 82 }} />
					{/if}
				</Container>
				{#each feature.lines as line, k}
					<Text
						anchor={0.5}
						x={WIDE.width * 0.19}
						y={20 + (k - (feature.lines.length - 1) / 2) * 44}
						text={socialText(line)}
						style={textStyle(feature.lines.length > 2 ? 30 : 38)}
					/>
				{/each}
			</Container>
		{/each}
	{/if}
</MainContainer>
