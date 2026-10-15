import type { BetType } from 'rgs-requests';

import type { SymbolName, RawSymbol, GameType, Position, Gravity, Wall, FreeSpinKind } from './types';

// Events from math/whisker_tilt (see math/whisker_tilt/README.md for the full contract).

type BookEventReveal = {
	index: number;
	type: 'reveal';
	board: RawSymbol[][];
	paddingPositions: number[];
	anticipation: number[];
	gameType: GameType;
};

type BookEventWinInfo = {
	index: number;
	type: 'winInfo';
	totalWin: number;
	wins: {
		symbol: SymbolName;
		clusterSize: number;
		win: number;
		positions: Position[];
		meta: {
			globalMult: number;
			/** the Edge Keeper multiplier applied to this cluster */
			clusterMult: number;
			/** walls the cluster touches, 0 South .. 3 East */
			walls: number[];
			winWithoutMult: number;
			overlay: Position;
		};
	}[];
};

type BookEventUpdateTumbleWin = { index: number; type: 'updateTumbleWin'; amount: number };
type BookEventSetTotalWin = { index: number; type: 'setTotalWin'; amount: number };
type BookEventSetWin = { index: number; type: 'setWin'; amount: number; winLevel: number };
type BookEventFinalWin = { index: number; type: 'finalWin'; amount: number };
type BookEventWincap = { index: number; type: 'wincap'; amount: number };

type BookEventFreeSpinTrigger = { index: number; type: 'freeSpinTrigger'; totalFs: number; positions: Position[] };
type BookEventFreeSpinRetrigger = { index: number; type: 'freeSpinRetrigger'; totalFs: number; positions: Position[] };
type BookEventUpdateFreeSpin = { index: number; type: 'updateFreeSpin'; amount: number; total: number };
type BookEventFreeSpinEnd = { index: number; type: 'freeSpinEnd'; amount: number; winLevel: number };

// --- the Tilt Tumble ---

type BookEventTilt = {
	index: number;
	type: 'tilt';
	gravity: Gravity;
	turn: number;
	/** cascade: after a win; paw: Mitten turns the box before a free spin */
	cause: 'cascade' | 'paw';
};

type BookEventSnowstorm = { index: number; type: 'snowstorm'; turn: number; keepers: number[] };

type BookEventSettleBoard = {
	index: number;
	type: 'settleBoard';
	cause: 'cascade' | 'bank';
	gravity: Gravity;
	removed: Position[];
	newSymbols: (Position & RawSymbol)[];
};

type BookEventKeeperBank = {
	index: number;
	type: 'keeperBank';
	wall: Wall;
	coins: (Position & { value: number })[];
	keepers: number[];
};

type BookEventKeepersInit = { index: number; type: 'keepersInit'; keepers: number[] };

// --- features ---

type BookEventMysteryReveal = { index: number; type: 'mysteryReveal'; kind: FreeSpinKind; spins: number };
type BookEventCrackMeter = { index: number; type: 'crackMeter'; progress: number };
type BookEventShelfResult = { index: number; type: 'shelfResult'; shattered: boolean };

// customised: rebuilds the screen when a bonus round is resumed
type BookEventCreateBonusSnapshot = { index: number; type: 'createBonusSnapshot'; bookEvents: BookEvent[] };

export type BookEvent =
	| BookEventReveal
	| BookEventWinInfo
	| BookEventUpdateTumbleWin
	| BookEventSetTotalWin
	| BookEventSetWin
	| BookEventFinalWin
	| BookEventWincap
	| BookEventFreeSpinTrigger
	| BookEventFreeSpinRetrigger
	| BookEventUpdateFreeSpin
	| BookEventFreeSpinEnd
	| BookEventTilt
	| BookEventSnowstorm
	| BookEventSettleBoard
	| BookEventKeeperBank
	| BookEventKeepersInit
	| BookEventMysteryReveal
	| BookEventCrackMeter
	| BookEventShelfResult
	| BookEventCreateBonusSnapshot;

export type Bet = BetType<BookEvent>;
export type BookEventOfType<T> = Extract<BookEvent, { type: T }>;
export type BookEventContext = { bookEvents: BookEvent[] };
