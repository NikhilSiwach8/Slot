// Bet modes shown in the UI, mirroring the math modes in the synced config so the buy menu
// can only ever request a mode the RGS knows.
import { stateMeta, type BetModeMeta } from 'state-shared';

import config from './config';
import { KEY_AWARDS, RULES, formatRtp } from './rules';

const m = config.betModes;
const noAssets = { icon: '', volatility: '', button: '', dialogImage: '', dialogVolatility: '' };
const odds = (mode: { rtp: number; max_win: number }) =>
	`RTP ${formatRtp(mode.rtp)} · Max win ${mode.max_win.toLocaleString('en-US')}x`;
const spins = KEY_AWARDS.map((award) => award.spins);

type Text = BetModeMeta[string]['text'];
const meta = (
	mode: string,
	source: { cost: number; max_win: number },
	type: 'default' | 'activate' | 'buy',
	text: Text,
) => ({
	mode,
	costMultiplier: source.cost,
	type,
	parent: '',
	children: '',
	maxWin: source.max_win,
	assets: noAssets,
	text,
});

export const BET_MODE_META: BetModeMeta = {
	BASE: meta('BASE', m.base, 'default', {
		title: '',
		dialog: '',
		button: '',
		betAmountLabel: '',
		tickerIdle: '',
		tickerSpin: '',
	}),
	// 'activate' modes stay on between spins and charge costMultiplier x bet per spin
	ANTE: meta('ANTE', m.ante, 'activate', {
		title: 'CATNIP',
		description: 'Double chance: Snow Day triggers twice as often on every spin.',
		dialog: odds(m.ante),
		button: 'ACTIVATE',
		betAmountLabel: 'CATNIP',
		tickerIdle: 'CATNIP IS ON',
		tickerSpin: 'GOOD LUCK',
	}),
	FEATURE: meta('FEATURE', m.feature, 'activate', {
		title: 'PAW SPINS',
		description: `Every spin starts with all four keepers lit at x${RULES.featureStartKeeper} and is guaranteed to win.`,
		dialog: odds(m.feature),
		button: 'ACTIVATE',
		betAmountLabel: 'PAW SPINS',
		tickerIdle: 'PAW SPINS ARE ON',
		tickerSpin: 'GOOD LUCK',
	}),
	BONUS: meta('BONUS', m.bonus, 'buy', {
		title: 'SNOW DAY',
		description:
			`${Math.min(...spins)}–${Math.max(...spins)} free spins. Keepers, gravity and every ` +
			`turn of the box carry over, and Mitten turns the box before each spin.`,
		dialog: odds(m.bonus),
		button: 'BUY',
		betAmountLabel: 'BONUS BUY',
		tickerIdle: '',
		tickerSpin: '',
	}),
	SUPER: meta('SUPER', m.super, 'buy', {
		title: 'SUPER SNOW DAY',
		description: `${RULES.superSpins} free spins with all four keepers starting lit at x${RULES.superStartKeeper}.`,
		dialog: odds(m.super),
		button: 'BUY',
		betAmountLabel: 'BONUS BUY',
		tickerIdle: '',
		tickerSpin: '',
	}),
	MYSTERY: meta('MYSTERY', m.mystery, 'buy', {
		title: "MITTEN'S GIFT",
		description: 'A wrapped present: Snow Day or Super Snow Day, 8 to 15 free spins.',
		dialog: odds(m.mystery),
		button: 'BUY',
		betAmountLabel: 'BONUS BUY',
		tickerIdle: '',
		tickerSpin: '',
	}),
	MAX_OR_NOTHING: meta('MAX_OR_NOTHING', m.max_or_nothing, 'buy', {
		title: 'OFF THE SHELF',
		description:
			`A Super Snow Day that pays ${RULES.wincap.toLocaleString('en-US')}x the bet if it reaches ` +
			`the max win, and nothing otherwise.`,
		dialog: odds(m.max_or_nothing),
		button: 'BUY',
		betAmountLabel: 'BONUS BUY',
		tickerIdle: '',
		tickerSpin: '',
	}),
};

export const applyBetModeMeta = () => {
	stateMeta.betModeMeta = BET_MODE_META;
};
