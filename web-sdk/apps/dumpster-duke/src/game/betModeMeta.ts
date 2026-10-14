// Bet modes shown in the UI. The template ships demo modes (ANTE, SUPERANTE, ...)
// that this game doesn't have; these mirror the real math modes from the synced
// config so the buy menu can only ever request a mode the RGS knows.
import { stateMeta, type BetModeMeta } from 'state-shared';

import config from './config';
import { SCATTER_AWARDS, formatRtp } from './rules';

const base = config.betModes.base;
const ante = config.betModes.ante;
const bonus = config.betModes.bonus;
const spins = SCATTER_AWARDS.map((award) => award.spins);

const noAssets = { icon: '', volatility: '', button: '', dialogImage: '', dialogVolatility: '' };

export const BET_MODE_META: BetModeMeta = {
	BASE: {
		mode: 'BASE',
		costMultiplier: base.cost,
		type: 'default',
		parent: '',
		children: '',
		maxWin: base.max_win,
		assets: noAssets,
		text: { title: '', dialog: '', button: '', betAmountLabel: '', tickerIdle: '', tickerSpin: '' },
	},
	// Ante bet: an 'activate' mode, so it stays on between spins and the SDK charges
	// costMultiplier x bet (stateBetDerived.betCost) until the player switches it off.
	ANTE: {
		mode: 'ANTE',
		costMultiplier: ante.cost,
		type: 'activate',
		parent: '',
		children: '',
		maxWin: ante.max_win,
		assets: noAssets,
		text: {
			title: 'DOUBLE CHANCE',
			description: 'The Midnight Raid triggers twice as often on every spin.',
			dialog: `RTP ${formatRtp(ante.rtp)} · Max win ${ante.max_win.toLocaleString('en-US')}x`,
			button: 'ACTIVATE',
			betAmountLabel: 'DOUBLE CHANCE',
			tickerIdle: 'DOUBLE CHANCE IS ON',
			tickerSpin: 'GOOD LUCK',
		},
	},
	BONUS: {
		mode: 'BONUS',
		costMultiplier: bonus.cost,
		type: 'buy',
		parent: '',
		children: '',
		maxWin: bonus.max_win,
		assets: noAssets,
		text: {
			title: 'MIDNIGHT RAID',
			description:
				`Starts with ${SCATTER_AWARDS[0].scatters}–${SCATTER_AWARDS[SCATTER_AWARDS.length - 1].scatters} ` +
				`Golden Trash Cans for ${Math.min(...spins)}–${Math.max(...spins)} free spins. ` +
				`The Loot Bag multiplier never resets during the raid.`,
			dialog: `RTP ${formatRtp(bonus.rtp)} · Max win ${bonus.max_win.toLocaleString('en-US')}x`,
			button: 'BUY',
			betAmountLabel: 'BONUS BUY', // shown as "BONUS" in social mode (see UiLabel)
			tickerIdle: '',
			tickerSpin: '',
		},
	},
};

export const applyBetModeMeta = () => {
	stateMeta.betModeMeta = BET_MODE_META;
};
