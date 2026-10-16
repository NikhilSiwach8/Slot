// Player-facing rules data, all read from the config synced from the math
// (scripts/sync_fe_config.py), so the rules screen always matches the math.
import config from './config';

export const {
	scatterAwards: SCATTER_AWARDS,
	retrigger: RETRIGGER,
	minCluster: MIN_CLUSTER,
	capValues: CAP_VALUES,
	maxCap: MAX_CAP,
} = config.dukeRules;

/** Text on a Candy Cap: its value, or MAX for the Max or Nothing cap. */
export const capLabel = (value: number) => (value >= MAX_CAP ? 'MAX' : `${value}x`);

export const SYMBOL_NAMES: Record<string, string> = {
	H1: 'Count Dumpster Duke',
	H2: 'Werewolf Possum',
	H3: 'Witch Pigeon',
	H4: "Jack-o'-Pizza",
	L1: 'Mummy Can',
	L2: 'Ghost Fish',
	L3: 'Boo-nana',
	L4: 'Poison Apple',
	S: 'Cursed Trash Can',
	M: 'Candy Cap',
};

// Order of frames in the dukeSymbols sprite sheet (see art/build_atlas.py).
export const SHEET_ORDER = ['H1', 'H2', 'H3', 'H4', 'L1', 'L2', 'L3', 'L4', 'S', 'M'];
export const SHEET_COLUMNS = 4;
export const SHEET_ROWS = 3;

type PayGroup = { from: number; to: number; pay: number };

/** Collapse the per-count paytable into ranges, e.g. 8-9 → 10x, 10-11 → 25x. */
export const getPayGroups = (symbol: string): PayGroup[] => {
	const entries = (config.symbols as Record<string, { paytable?: Record<string, number>[] }>)[symbol]
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
