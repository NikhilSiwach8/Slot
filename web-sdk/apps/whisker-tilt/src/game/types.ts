import type config from './config';

export type SymbolName = keyof typeof config.symbols;
/** A symbol as the math books send it: `multiplier` is a Snowflake Coin's value. */
export type RawSymbol = { name: SymbolName; multiplier?: number; scatter?: boolean };
export type BetMode = keyof typeof config.betModes;
export type GameType = 'basegame' | 'freegame';

/** Screen coordinates: reel = column from the West wall, row = 0 at the North wall. */
export type Position = {
	reel: number;
	row: number;
};

/** Gravity and wall share an index: 0 down/South, 1 left/West, 2 up/North, 3 right/East. */
export type Gravity = 'down' | 'left' | 'up' | 'right';
export type Wall = 'south' | 'west' | 'north' | 'east';
export type FreeSpinKind = 'free' | 'super';
