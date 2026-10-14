import _ from 'lodash';

import type { RawSymbol, SymbolState } from './types';

export const SYMBOL_SIZE = 100;

export const REEL_PADDING = 0.53;

// initial board (padded top and bottom)
export const INITIAL_BOARD: RawSymbol[][] = [
	[{ name: 'L1' }, { name: 'H1' }, { name: 'L3' }, { name: 'M', multiplier: 10 }, { name: 'H2' }, { name: 'L4' }, { name: 'H1' }],
	[{ name: 'L3' }, { name: 'H2' }, { name: 'L2' }, { name: 'S', scatter: true }, { name: 'H1' }, { name: 'L1' }, { name: 'L2' }],
	[{ name: 'L2' }, { name: 'H3' }, { name: 'H1' }, { name: 'L3' }, { name: 'L1' }, { name: 'H4' }, { name: 'L2' }],
	[{ name: 'L3' }, { name: 'H4' }, { name: 'L4' }, { name: 'H1' }, { name: 'S', scatter: true }, { name: 'L2' }, { name: 'H1' }],
	[{ name: 'H3' }, { name: 'L4' }, { name: 'M', multiplier: 2 }, { name: 'H2' }, { name: 'L1' }, { name: 'L2' }, { name: 'L3' }],
	[{ name: 'H2' }, { name: 'L2' }, { name: 'H3' }, { name: 'L3' }, { name: 'H4' }, { name: 'L4' }, { name: 'L2' }],
];

export const BOARD_DIMENSIONS = { x: INITIAL_BOARD.length, y: INITIAL_BOARD[0].length - 2 };

export const BOARD_SIZES = {
	width: SYMBOL_SIZE * BOARD_DIMENSIONS.x,
	height: SYMBOL_SIZE * BOARD_DIMENSIONS.y,
};

export const BACKGROUND_RATIO = 2039 / 1000;
export const PORTRAIT_BACKGROUND_RATIO = 1242 / 2208;
const PORTRAIT_RATIO = 800 / 1422;
const LANDSCAPE_RATIO = 1600 / 900;
const DESKTOP_RATIO = 1422 / 800;

const DESKTOP_HEIGHT = 800;
const LANDSCAPE_HEIGHT = 900;
const PORTRAIT_HEIGHT = 1422;
export const DESKTOP_MAIN_SIZES = { width: DESKTOP_HEIGHT * DESKTOP_RATIO, height: DESKTOP_HEIGHT };
export const LANDSCAPE_MAIN_SIZES = {
	width: LANDSCAPE_HEIGHT * LANDSCAPE_RATIO,
	height: LANDSCAPE_HEIGHT,
};
export const PORTRAIT_MAIN_SIZES = {
	width: PORTRAIT_HEIGHT * PORTRAIT_RATIO,
	height: PORTRAIT_HEIGHT,
};

export const HIGH_SYMBOLS = ['H1', 'H2', 'H3', 'H4'];

export const INITIAL_SYMBOL_STATE: SymbolState = 'static';

const HIGH_SYMBOL_SIZE = 0.9;
const LOW_SYMBOL_SIZE = 0.9;
const SPECIAL_SYMBOL_SIZE = 1;

const SPIN_OPTIONS_SHARED = {
	reelFallInDelay: 80,
	reelPaddingMultiplierNormal: 1.25,
	reelPaddingMultiplierAnticipated: 18,
	reelFallOutDelay: 145,
};

export const SPIN_OPTIONS_DEFAULT = {
	...SPIN_OPTIONS_SHARED,
	symbolFallInSpeed: 3.5,
	symbolFallInInterval: 30,
	symbolFallInBounceSpeed: 0.15,
	symbolFallInBounceSizeMulti: 0.5,
	symbolFallOutSpeed: 3.5,
	symbolFallOutInterval: 20,
};

export const SPIN_OPTIONS_FAST = {
	...SPIN_OPTIONS_SHARED,
	symbolFallInSpeed: 7,
	symbolFallInInterval: 0,
	symbolFallInBounceSpeed: 0.3,
	symbolFallInBounceSizeMulti: 0.25,
	symbolFallOutSpeed: 7,
	symbolFallOutInterval: 0,
};

export const MOTION_BLUR_VELOCITY = 31;

export const zIndexes = {
	background: {
		backdrop: -3,
		normal: -2,
		feature: -1,
	},
};

// Dumpster Duke symbols: sprites from the dukeSymbols sheet, animated in code
// (see components/DukeSymbol.svelte). Animation names: idle | land | win | explode | taken.
export const MULTIPLIER_VALUES = [2, 3, 4, 5, 8, 10, 15, 20, 25, 50, 100] as const;

type DukeSymbolInfo = {
	type: 'duke';
	assetKey: string;
	animation: 'idle' | 'land' | 'win' | 'explode' | 'taken';
	sizeRatios: { width: number; height: number };
	multiplier?: number;
};

const dukeStates = (
	assetKey: string,
	size: number,
	multiplier?: number,
): Record<SymbolState, DukeSymbolInfo> => {
	const info = (animation: DukeSymbolInfo['animation']): DukeSymbolInfo => ({
		type: 'duke',
		assetKey,
		animation,
		sizeRatios: { width: size, height: size },
		multiplier,
	});
	return {
		static: info('idle'),
		spin: info('idle'),
		land: info('land'),
		win: info('win'),
		postWinStatic: info('idle'),
		explosion: info('explode'),
	} as Record<SymbolState, DukeSymbolInfo>;
};

const multiplierEntries = (prefix: string, taken: boolean) =>
	Object.fromEntries(
		MULTIPLIER_VALUES.map((value) => {
			const states = dukeStates('duke_m.png', 0.9, value);
			if (taken) {
				for (const key of Object.keys(states) as SymbolState[]) {
					states[key] = { ...states[key], animation: 'taken' };
				}
			}
			return [`${prefix}_${value}`, states];
		}),
	);

export const SYMBOL_INFO_MAP: Record<string, Record<SymbolState, DukeSymbolInfo>> = {
	H1: dukeStates('duke_h1.png', HIGH_SYMBOL_SIZE * 1.05),
	H2: dukeStates('duke_h2.png', HIGH_SYMBOL_SIZE),
	H3: dukeStates('duke_h3.png', HIGH_SYMBOL_SIZE),
	H4: dukeStates('duke_h4.png', HIGH_SYMBOL_SIZE),
	L1: dukeStates('duke_l1.png', LOW_SYMBOL_SIZE * 0.9),
	L2: dukeStates('duke_l2.png', LOW_SYMBOL_SIZE * 0.9),
	L3: dukeStates('duke_l3.png', LOW_SYMBOL_SIZE * 0.9),
	L4: dukeStates('duke_l4.png', LOW_SYMBOL_SIZE * 0.9),
	S: dukeStates('duke_s.png', SPECIAL_SYMBOL_SIZE * 1.1),
	...multiplierEntries('M', false),
	...multiplierEntries('M_TAKEN', true),
};

export const SCATTER_LAND_SOUND_MAP = {
	1: 'sfx_scatter_stop_1',
	2: 'sfx_scatter_stop_2',
	3: 'sfx_scatter_stop_3',
	4: 'sfx_scatter_stop_4',
	5: 'sfx_scatter_stop_5',
} as const;
