import type { Gravity, RawSymbol, SymbolName, Wall } from './types';

export const SYMBOL_SIZE = 100;
export const BOARD_DIMENSIONS = { x: 6, y: 6 };
export const BOARD_SIZES = {
	width: SYMBOL_SIZE * BOARD_DIMENSIONS.x,
	height: SYMBOL_SIZE * BOARD_DIMENSIONS.y,
};

/** The snow box frame art: its window spans ~60% of the image, centred at (0.49, 0.503). */
export const FRAME = { size: BOARD_SIZES.width / 0.6, centerX: 0.49, centerY: 0.503 };

/** Board + frame + keepers scale per layout, so the whole box fits the main area. */
export const BOARD_SCALE = { desktop: 0.76, tablet: 0.9, landscape: 0.84, portrait: 0.76 } as const;

export const GRAVITIES: Gravity[] = ['down', 'left', 'up', 'right'];
export const WALLS: Wall[] = ['south', 'west', 'north', 'east'];
/** Unit step "toward the floor" in board coordinates, per gravity. */
export const GRAVITY_STEP: Record<Gravity, { x: number; y: number }> = {
	down: { x: 0, y: 1 },
	left: { x: -1, y: 0 },
	up: { x: 0, y: -1 },
	right: { x: 1, y: 0 },
};

export const HIGH_SYMBOLS: SymbolName[] = ['H1', 'H2', 'H3', 'H4'];

/** Atlas frame and on-board size (fraction of a cell) for each symbol. */
export const SYMBOL_ART: Record<string, { frame: string; size: number }> = {
	H1: { frame: 'wt_h1.png', size: 1.0 },
	H2: { frame: 'wt_h2.png', size: 0.98 },
	H3: { frame: 'wt_h3.png', size: 1.0 },
	H4: { frame: 'wt_h4.png', size: 0.98 },
	L1: { frame: 'wt_l1.png', size: 0.9 },
	L2: { frame: 'wt_l2.png', size: 0.9 },
	L3: { frame: 'wt_l3.png', size: 0.9 },
	L4: { frame: 'wt_l4.png', size: 0.9 },
	S: { frame: 'wt_s.png', size: 1.05 },
	C: { frame: 'wt_c.png', size: 0.92 },
};

const L = (name: SymbolName): RawSymbol => ({ name });
export const INITIAL_BOARD: RawSymbol[][] = [
	[L('L1'), L('H1'), L('L3'), L('H2'), L('L4'), L('L2')],
	[L('L3'), L('H2'), L('L2'), { name: 'S', scatter: true }, L('H1'), L('L1')],
	[L('L2'), L('H3'), L('H1'), L('L3'), L('L1'), L('H4')],
	[L('L4'), { name: 'C', multiplier: 5 }, L('L4'), L('H1'), L('L2'), L('L3')],
	[L('H3'), L('L4'), L('L1'), L('H2'), L('L3'), L('H3')],
	[L('H2'), L('L2'), L('H3'), L('L3'), L('H4'), L('L4')],
];

export const zIndexes = {
	background: { backdrop: -3, normal: -2, feature: -1 },
};

export const SCATTER_LAND_SOUND_MAP = {
	1: 'sfx_scatter_stop_1',
	2: 'sfx_scatter_stop_2',
	3: 'sfx_scatter_stop_3',
	4: 'sfx_scatter_stop_4',
	5: 'sfx_scatter_stop_5',
} as const;
