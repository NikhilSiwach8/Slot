// Player-facing rules data, all read from the config synced from the math
// (scripts/sync_fe_config_whisker_tilt.py), so the rules screen always matches the math.
import config from './config';

export const RULES = config.wtRules;
export const { keyAwards: KEY_AWARDS, minCluster: MIN_CLUSTER, coinValues: COIN_VALUES } = RULES;

export const SYMBOL_NAMES: Record<string, string> = {
	H1: 'Golden Sleigh',
	H2: 'Gingerbread House',
	H3: 'Nutcracker',
	H4: 'Snowman',
	L1: 'Red Bauble',
	L2: 'Blue Bauble',
	L3: 'Green Star',
	L4: 'Gold Bell',
	S: 'Wind-up Key',
	C: 'Snowflake Coin',
};

// Order of frames in the wtSymbols sprite sheet (see art/whisker_tilt/build_web_assets.py).
export const SHEET_ORDER = ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'S', 'C'];
export const SHEET_COLUMNS = 4;
export const SHEET_ROWS = 3;

type PayGroup = { from: number; to: number; pay: number };

/** Collapse the per-size paytable into ranges, e.g. 9-10 → 3x, 16-36 → 300x. */
export const getPayGroups = (symbol: string): PayGroup[] => {
	const entries = (config.symbols as unknown as Record<string, { paytable?: Record<string, number>[] | null }>)[symbol]
		?.paytable;
	if (!entries) return [];
	const flat = entries
		.map((entry) => Object.entries(entry)[0])
		.map(([count, pay]) => ({ count: Number(count), pay }))
		.sort((a, b) => a.count - b.count);
	const groups: PayGroup[] = [];
	for (const { count, pay } of flat) {
		const last = groups[groups.length - 1];
		if (last && last.pay === pay && last.to === count - 1) last.to = count;
		else groups.push({ from: count, to: count, pay });
	}
	return groups;
};

export const PAYING_SYMBOLS = ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4'];

export const BET_MODES = Object.entries(config.betModes).map(([name, mode]) => ({
	name,
	cost: mode.cost,
	rtp: mode.rtp,
	maxWin: mode.max_win,
	buyBonus: mode.buyBonus,
}));

export const formatRtp = (rtp: number) => `${(rtp * 100).toFixed(2)}%`;
export const formatX = (x: number) => `${Number(x).toLocaleString('en-US', { maximumFractionDigits: 2 })}x`;
