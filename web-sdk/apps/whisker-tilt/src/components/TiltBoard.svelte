<!-- The snow box: frame, the masked 6x6 window with its sliding symbols, the four Edge
     Keepers on the walls, the floor-wall glow, Snowstorm whiteout and (Off the Shelf) cracks.
     All motion comes from game/tiltBoard.svelte.ts; this component only draws it. -->
<script lang="ts">
	import type * as PIXI from 'pixi.js';
	import { BitmapText, Container, Graphics, Rectangle, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES, FRAME, GRAVITIES, SYMBOL_ART, SYMBOL_SIZE, WALLS } from '../game/constants';
	import { stateBoard, wallAnchor, type BoardCell } from '../game/tiltBoard.svelte';

	const context = getContext();
	const layout = $derived(context.stateGameDerived.boardLayout());
	const W = BOARD_SIZES.width;
	const H = BOARD_SIZES.height;

	const KEEPER_KEYS = ['keeper_south', 'keeper_west', 'keeper_north', 'keeper_east'];
	// width / height of each keeper's art
	const KEEPER_ASPECT = [237 / 320, 247 / 320, 205 / 320, 235 / 320];
	const KEEPER_HEIGHT = SYMBOL_SIZE * 1.55;
	const floorWall = $derived(GRAVITIES.indexOf(stateBoard.gravity));

	const cells = $derived([
		...stateBoard.leaving,
		...(stateBoard.grid.flat().filter(Boolean) as BoardCell[]),
	]);

	const drawWindow = (g: PIXI.Graphics) => {
		g.roundRect(-6, -6, W + 12, H + 12, 14).fill({ color: 0x0d1f3d, alpha: 0.78 });
		for (let i = 1; i < 6; i++) {
			g.rect(i * SYMBOL_SIZE - 1, 8, 2, H - 16).fill({ color: 0xbfe3ff, alpha: 0.06 });
			g.rect(8, i * SYMBOL_SIZE - 1, W - 16, 2).fill({ color: 0xbfe3ff, alpha: 0.06 });
		}
	};

	// the floor wall glows so the player always sees which way things fall
	const drawFloor = (g: PIXI.Graphics) => {
		const t = 10;
		const rect = [
			[0, H - t, W, t],
			[0, 0, t, H],
			[0, 0, W, t],
			[W - t, 0, t, H],
		][floorWall];
		g.roundRect(rect[0], rect[1], rect[2], rect[3], 5).fill({ color: 0xffd36b, alpha: 0.9 });
	};

	const art = (cell: BoardCell) => SYMBOL_ART[cell.raw.name] ?? SYMBOL_ART.L1;
</script>

<Container
	x={layout.x}
	y={layout.y}
	scale={layout.scale}
	pivot={{ x: W / 2, y: H / 2 }}
	rotation={stateBoard.wobble}
>
	<Graphics draw={drawWindow} />

	<!-- symbols, clipped to the window -->
	<Container>
		<Rectangle isMask x={0} y={0} width={W} height={H} />
		{#each cells as cell (cell.id)}
			{@const a = art(cell)}
			{@const dim = stateBoard.dimOthers && !stateBoard.winning.has(cell.id)}
			<Container x={cell.x} y={cell.y} scale={cell.scale} rotation={cell.rotation} alpha={cell.alpha}>
				{#if cell.glow > 0}
					<Sprite
						anchor={0.5}
						key={a.frame}
						width={SYMBOL_SIZE * a.size * 1.18}
						height={SYMBOL_SIZE * a.size * 1.18}
						tint={0xffd36b}
						alpha={cell.glow * 0.8}
						blendMode="add"
					/>
				{/if}
				<Sprite
					anchor={0.5}
					key={a.frame}
					width={SYMBOL_SIZE * a.size}
					height={SYMBOL_SIZE * a.size}
					tint={dim ? 0x5d6a80 : 0xffffff}
				/>
				{#if cell.raw.name === 'C' && cell.raw.multiplier}
					<Graphics
						draw={(g) => g.roundRect(-26, -15, 52, 30, 12).fill({ color: 0x14305c, alpha: 0.85 })}
					/>
					<BitmapText
						anchor={0.5}
						text={`x${cell.raw.multiplier}`}
						style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * (cell.raw.multiplier >= 10 ? 0.27 : 0.32) }}
					/>
				{/if}
			</Container>
		{/each}
	</Container>

	<Graphics draw={drawFloor} alpha={0.55 + 0.45 * (1 - stateBoard.flash)} />

	<!-- the snow box frame, its window centred on the board -->
	<Sprite
		key="box_frame"
		anchor={0.5}
		x={W / 2 + (0.5 - FRAME.centerX) * FRAME.size}
		y={H / 2 + (0.5 - FRAME.centerY) * FRAME.size}
		width={FRAME.size}
		height={FRAME.size}
	/>

	<!-- Edge Keepers: one per wall, lantern value above their heads -->
	{#each WALLS as wall, i (wall)}
		{@const anchor = wallAnchor(wall)}
		{@const value = stateBoard.keepers[i]}
		{@const pulse = stateBoard.keeperPulse[i]}
		{@const lit = value > 0}
		{@const isFloor = floorWall === i}
		<Container x={anchor.x} y={anchor.y} scale={1 + pulse * 0.25}>
			{#if isFloor}
				<Sprite
					key={KEEPER_KEYS[i]}
					anchor={0.5}
					height={KEEPER_HEIGHT * 1.12}
					width={KEEPER_HEIGHT * 1.12 * KEEPER_ASPECT[i]}
					tint={0xffd36b}
					alpha={0.45}
					blendMode="add"
				/>
			{/if}
			<Sprite
				key={KEEPER_KEYS[i]}
				anchor={0.5}
				height={KEEPER_HEIGHT}
				width={KEEPER_HEIGHT * KEEPER_ASPECT[i]}
				tint={lit || isFloor ? 0xffffff : 0x8a96ab}
			/>
			<Container y={-KEEPER_HEIGHT * 0.5}>
				<Graphics
					draw={(g) =>
						g
							.roundRect(-44, -22, 88, 44, 18)
							.fill({ color: lit ? 0x7a3b0c : 0x23324d, alpha: 0.92 })
							.stroke({ color: lit ? 0xffd36b : 0x7f8fa8, width: 3 })}
				/>
				<BitmapText
					anchor={0.5}
					text={lit ? `x${value}` : 'x0'}
					alpha={lit ? 1 : 0.55}
					style={{ fontFamily: 'gold', fontSize: SYMBOL_SIZE * (value >= 100 ? 0.3 : 0.36) }}
				/>
			</Container>
		</Container>
	{/each}

	{#if context.stateGame.crack !== null}
		<Sprite
			key="crack_overlay"
			anchor={0.5}
			x={W / 2}
			y={H / 2}
			width={W * 1.05}
			height={W * 1.05 * 0.617}
			alpha={Math.min(1, context.stateGame.crack * 1.6)}
			scale={0.6 + 0.4 * context.stateGame.crack}
		/>
	{/if}

	{#if stateBoard.flash > 0}
		<Rectangle
			x={-SYMBOL_SIZE * 2}
			y={-SYMBOL_SIZE * 2}
			width={W + SYMBOL_SIZE * 4}
			height={H + SYMBOL_SIZE * 4}
			backgroundColor={0xf2fbff}
			alpha={stateBoard.flash * 0.85}
		/>
	{/if}
</Container>
