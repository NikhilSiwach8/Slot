// Bet modes shown in the UI. The template ships demo modes (ANTE, SUPERANTE, ...)
// that this game doesn't have; these mirror the real math modes from the synced
// config so the buy menu can only ever request a mode the RGS knows.
import { stateMeta, type BetModeMeta } from 'state-shared';

import config from './config';
import { SCATTER_AWARDS, formatRtp } from './rules';

const base = config.betModes.base;
const ante = config.betModes.ante;
const bonus = config.betModes.bonus;
const feature = config.betModes.feature;
const superRaid = config.betModes.super;
const mystery = config.betModes.mystery;
const maxOrNothing = config.betModes.max;

const rtpLine = (mode: { rtp: number; max_win: number }) =>
	`RTP ${formatRtp(mode.rtp)} · Max win ${mode.max_win.toLocaleString('en-US')}x`;
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
			description: 'The Haunted Raid triggers twice as often on every spin.',
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
			title: 'HAUNTED RAID',
			description:
				`Starts with ${SCATTER_AWARDS[0].scatters}–${SCATTER_AWARDS[SCATTER_AWARDS.length - 1].scatters} ` +
				`Cursed Trash Cans for ${Math.min(...spins)}–${Math.max(...spins)} free spins. ` +
				`The Trick-or-Treat Bag multiplier never resets during the raid.`,
			dialog: `RTP ${formatRtp(bonus.rtp)} · Max win ${bonus.max_win.toLocaleString('en-US')}x`,
			button: 'BUY',
			betAmountLabel: 'BONUS BUY', // shown as "BONUS" in social mode (see UiLabel)
			tickerIdle: '',
			tickerSpin: '',
		},
	},
};

// Extra modes: Feature Spin (stays on), Super Raid, Mystery Bonus and Max or Nothing (buys).
Object.assign(BET_MODE_META, {
	FEATURE: {
		mode: 'FEATURE',
		costMultiplier: feature.cost,
		type: 'activate',
		parent: '',
		children: '',
		maxWin: feature.max_win,
		assets: noAssets,
		text: {
			title: 'FEATURE SPIN',
			description:
				'Every spin lands 3 Cursed Trash Cans and at least one Candy Cap. One more can starts the Haunted Raid.',
			dialog: rtpLine(feature),
			button: 'ACTIVATE',
			betAmountLabel: 'FEATURE SPIN',
			tickerIdle: 'FEATURE SPIN IS ON',
			tickerSpin: 'GOOD LUCK',
		},
	},
	SUPER: {
		mode: 'SUPER',
		costMultiplier: superRaid.cost,
		type: 'buy',
		parent: '',
		children: '',
		maxWin: superRaid.max_win,
		assets: noAssets,
		text: {
			title: 'SUPER BONUS',
			description:
				'A Haunted Raid where the Trick-or-Treat Bag starts at x10 and every free spin lands at least one Candy Cap.',
			dialog: rtpLine(superRaid),
			button: 'BUY',
			betAmountLabel: 'SUPER BONUS',
			tickerIdle: '',
			tickerSpin: '',
		},
	},
	MYSTERY: {
		mode: 'MYSTERY',
		costMultiplier: mystery.cost,
		type: 'buy',
		parent: '',
		children: '',
		maxWin: mystery.max_win,
		assets: noAssets,
		text: {
			title: 'MYSTERY BONUS',
			description:
				'The Duke\'s chest reveals a surprise Haunted Raid: 5 to 25 free spins and a Trick-or-Treat Bag starting anywhere from x0 to x20.',
			dialog: rtpLine(mystery),
			button: 'BUY',
			betAmountLabel: 'MYSTERY BONUS',
			tickerIdle: '',
			tickerSpin: '',
		},
	},
	MAX: {
		mode: 'MAX',
		costMultiplier: maxOrNothing.cost,
		type: 'buy',
		parent: '',
		children: '',
		maxWin: maxOrNothing.max_win,
		assets: noAssets,
		text: {
			title: 'MAX OR NOTHING',
			description: `A single spin: any win is boosted to the ${maxOrNothing.max_win.toLocaleString('en-US')}x max win, no win pays nothing.`,
			dialog: rtpLine(maxOrNothing),
			button: 'BUY',
			betAmountLabel: 'MAX OR NOTHING',
			tickerIdle: '',
			tickerSpin: '',
		},
	},
});

export const applyBetModeMeta = () => {
	stateMeta.betModeMeta = BET_MODE_META;
};
