import _ from 'lodash';

import { recordBookEvent, checkIsMultipleRevealEvents, type BookEventHandlerMap } from 'utils-book';
import { stateBet } from 'state-shared';

import { eventEmitter } from './eventEmitter';
import { playBookEvent } from './utils';
import { winLevelMap, type WinLevel, type WinLevelData } from './winLevelMap';
import { stateGame, stateGameDerived } from './stateGame.svelte';
import type { BookEvent, BookEventOfType, BookEventContext } from './typesBookEvent';
import type { FreeSpinKind, Position } from './types';
import * as board from './tiltBoard.svelte';

const MAX_OR_NOTHING = 'MAX_OR_NOTHING';
const isMaxOrNothing = () => stateBet.activeBetModeKey === MAX_OR_NOTHING;

const winLevelSoundsPlay = ({ winLevelData }: { winLevelData: WinLevelData }) => {
	if (winLevelData?.alias === 'max') eventEmitter.broadcastAsync({ type: 'uiHide' });
	if (winLevelData?.sound?.sfx) eventEmitter.broadcast({ type: 'soundOnce', name: winLevelData.sound.sfx });
	if (winLevelData?.sound?.bgm) eventEmitter.broadcast({ type: 'soundMusic', name: winLevelData.sound.bgm });
	if (winLevelData?.type === 'big') eventEmitter.broadcast({ type: 'soundLoop', name: 'sfx_bigwin_coinloop' });
};

const winLevelSoundsStop = () => {
	eventEmitter.broadcast({ type: 'soundStop', name: 'sfx_bigwin_coinloop' });
	eventEmitter.broadcast({
		type: 'soundMusic',
		name: stateGame.gameType === 'basegame' ? 'bgm_main' : 'bgm_freespin',
	});
	eventEmitter.broadcastAsync({ type: 'uiShow' });
};

/** Which free spins a trigger starts, read ahead in the book (Mitten's Gift or lit keepers). */
const upcomingFreeSpins = (bookEvents: BookEvent[], fromIndex: number) => {
	const after = bookEvents.filter((e) => e.index > fromIndex);
	const firstSpin = after.findIndex((e) => e.type === 'updateFreeSpin');
	const before = firstSpin === -1 ? after : after.slice(0, firstSpin);
	const gift = before.find((e) => e.type === 'mysteryReveal') as BookEventOfType<'mysteryReveal'> | undefined;
	const init = before.find((e) => e.type === 'keepersInit') as BookEventOfType<'keepersInit'> | undefined;
	const kind: FreeSpinKind = gift?.kind ?? (init && init.keepers.some((k) => k > 0) ? 'super' : 'free');
	return { kind, gift };
};

const celebrate = async (positions: Position[]) => {
	eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_scatter_win_v2' });
	await board.highlight(positions);
};

export const bookEventHandlerMap: BookEventHandlerMap<BookEvent, BookEventContext> = {
	reveal: async (bookEvent: BookEventOfType<'reveal'>, { bookEvents }: BookEventContext) => {
		eventEmitter.broadcast({ type: 'tumbleWinAmountHide' });
		eventEmitter.broadcast({ type: 'tumbleWinAmountReset' });
		if (checkIsMultipleRevealEvents({ bookEvents })) {
			eventEmitter.broadcast({ type: 'stopButtonEnable' });
			recordBookEvent({ bookEvent });
		}
		stateGame.gameType = bookEvent.gameType;
		stateGame.scatterCounter = 0;
		if (isMaxOrNothing() && stateGame.crack === null) stateGame.crack = 0;
		await board.reveal(bookEvent.board, { onLand: stateGameDerived.onSymbolLand });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_symbols_landing' });
	},

	// --- the Tilt Tumble ---

	tilt: async (bookEvent: BookEventOfType<'tilt'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_reel_stop_3' });
		await Promise.all([
			eventEmitter.broadcastAsync({ type: 'mittenBat', gravity: bookEvent.gravity }),
			board.tilt(bookEvent.gravity),
		]);
	},
	snowstorm: async (bookEvent: BookEventOfType<'snowstorm'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_explosion_c' });
		await board.snowstorm(bookEvent.keepers);
	},
	settleBoard: async (bookEvent: BookEventOfType<'settleBoard'>) => {
		if (bookEvent.cause === 'cascade') {
			eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_explosion_b' });
		}
		await board.settle(bookEvent);
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_symbols_landing' });
	},
	keeperBank: async (bookEvent: BookEventOfType<'keeperBank'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_landing' });
		await board.bankCoins(bookEvent);
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_multiplier_up' });
	},
	keepersInit: async (bookEvent: BookEventOfType<'keepersInit'>) => {
		board.setKeepers(bookEvent.keepers);
	},

	// --- wins ---

	winInfo: async (bookEvent: BookEventOfType<'winInfo'>) => {
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_winlevel_small' });
		const labels = isMaxOrNothing()
			? []
			: bookEvent.wins.map((win) => ({
					reel: win.meta.overlay.reel,
					row: win.meta.overlay.row,
					amount: win.win,
					mult: win.meta.clusterMult,
				}));
		await Promise.all([
			board.highlight(_.flatten(bookEvent.wins.map((win) => win.positions))),
			labels.length ? eventEmitter.broadcastAsync({ type: 'winLabelsShow', labels }) : undefined,
		]);
	},
	updateTumbleWin: async (bookEvent: BookEventOfType<'updateTumbleWin'>) => {
		if (bookEvent.amount > 0) {
			eventEmitter.broadcast({ type: 'tumbleWinAmountShow' });
			eventEmitter.broadcast({ type: 'tumbleWinAmountUpdate', amount: bookEvent.amount, animate: false });
		}
	},
	setTotalWin: async (bookEvent: BookEventOfType<'setTotalWin'>) => {
		stateBet.winBookEventAmount = bookEvent.amount;
	},
	setWin: async (bookEvent: BookEventOfType<'setWin'>) => {
		const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];
		eventEmitter.broadcast({ type: 'winShow' });
		winLevelSoundsPlay({ winLevelData });
		await eventEmitter.broadcastAsync({ type: 'winUpdate', amount: bookEvent.amount, winLevelData });
		winLevelSoundsStop();
		eventEmitter.broadcast({ type: 'winHide' });
	},
	wincap: async () => {},
	finalWin: async () => {
		eventEmitter.broadcast({ type: 'tumbleWinAmountHide' });
	},

	// --- free spins ---

	freeSpinTrigger: async (bookEvent: BookEventOfType<'freeSpinTrigger'>, { bookEvents }: BookEventContext) => {
		const { kind, gift } = upcomingFreeSpins(bookEvents, bookEvent.index);
		await celebrate(bookEvent.positions);
		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		if (gift) {
			await eventEmitter.broadcastAsync({ type: 'mysteryGiftReveal', kind: gift.kind, spins: gift.spins });
		}
		stateGame.freeSpinKind = kind;
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_superfreespin' });
		await eventEmitter.broadcastAsync({ type: 'transition' });
		eventEmitter.broadcast({ type: 'freeSpinIntroShow' });
		eventEmitter.broadcast({ type: 'soundOnce', name: 'jng_intro_fs' });
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_freespin' });
		await eventEmitter.broadcastAsync({ type: 'freeSpinIntroUpdate', totalFreeSpins: bookEvent.totalFs });
		stateGame.gameType = 'freeSpins';
		// free spins start with fresh keepers and gravity pointing down (Super lights them next)
		board.setKeepers([0, 0, 0, 0]);
		board.stateBoard.gravity = 'down';
		eventEmitter.broadcast({ type: 'freeSpinIntroHide' });
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({ type: 'freeSpinCounterUpdate', current: undefined, total: bookEvent.totalFs });
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerButtonShow' });
		eventEmitter.broadcast({ type: 'drawerFold' });
	},
	// played as part of freeSpinTrigger (the gift opens before the intro)
	mysteryReveal: async () => {},
	freeSpinRetrigger: async (bookEvent: BookEventOfType<'freeSpinRetrigger'>) => {
		await celebrate(bookEvent.positions);
		eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_fs_respins' });
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({ type: 'freeSpinCounterUpdate', current: undefined, total: bookEvent.totalFs });
	},
	updateFreeSpin: async (bookEvent: BookEventOfType<'updateFreeSpin'>) => {
		eventEmitter.broadcast({ type: 'freeSpinCounterShow' });
		eventEmitter.broadcast({ type: 'freeSpinCounterUpdate', current: bookEvent.amount, total: bookEvent.total });
	},
	freeSpinEnd: async (bookEvent: BookEventOfType<'freeSpinEnd'>) => {
		await eventEmitter.broadcastAsync({ type: 'uiHide' });
		// Off the Shelf shows its own result screen; a round that fell short has nothing to count up
		if (!(isMaxOrNothing() && bookEvent.amount === 0)) {
			const winLevelData = winLevelMap[bookEvent.winLevel as WinLevel];
			eventEmitter.broadcast({ type: 'freeSpinOutroShow' });
			eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_youwon_panel' });
			winLevelSoundsPlay({ winLevelData });
			await eventEmitter.broadcastAsync({ type: 'freeSpinOutroCountUp', amount: bookEvent.amount, winLevelData });
			winLevelSoundsStop();
			eventEmitter.broadcast({ type: 'freeSpinOutroHide' });
		}
		stateGame.gameType = 'basegame';
		eventEmitter.broadcast({ type: 'freeSpinCounterHide' });
		eventEmitter.broadcast({ type: 'tumbleWinAmountHide' });
		await eventEmitter.broadcastAsync({ type: 'transition' });
		board.setKeepers([0, 0, 0, 0]);
		board.stateBoard.gravity = 'down';
		eventEmitter.broadcast({ type: 'soundMusic', name: 'bgm_main' });
		await eventEmitter.broadcastAsync({ type: 'uiShow' });
		await eventEmitter.broadcastAsync({ type: 'drawerUnfold' });
		eventEmitter.broadcast({ type: 'drawerButtonHide' });
	},

	// --- Off the Shelf ---

	crackMeter: async (bookEvent: BookEventOfType<'crackMeter'>) => {
		const from = stateGame.crack ?? 0;
		const to = bookEvent.progress;
		if (to > from) eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_wild_explode' });
		await board.animate(400, (t) => (stateGame.crack = from + (to - from) * t));
	},
	shelfResult: async (bookEvent: BookEventOfType<'shelfResult'>) => {
		await eventEmitter.broadcastAsync({ type: 'shelfResult', shattered: bookEvent.shattered });
		stateGame.crack = null;
	},

	// customised: rebuild the screen when a bonus round is resumed
	createBonusSnapshot: async (bookEvent: BookEventOfType<'createBonusSnapshot'>) => {
		const { bookEvents } = bookEvent;
		const last = <T extends BookEvent['type']>(type: T) =>
			_.findLast(bookEvents, (e) => e.type === type) as BookEventOfType<T> | undefined;

		const trigger = last('freeSpinTrigger');
		if (trigger) await playBookEvent(trigger, { bookEvents });
		const spin = last('updateFreeSpin');
		if (spin) playBookEvent(spin, { bookEvents });
		const total = last('setTotalWin');
		if (total) playBookEvent(total, { bookEvents });
		const keepers = _.findLast(
			bookEvents,
			(e) => e.type === 'keepersInit' || e.type === 'keeperBank' || e.type === 'snowstorm',
		) as { keepers: number[] } | undefined;
		if (keepers) board.setKeepers(keepers.keepers);
		const tilt = last('tilt');
		if (tilt) board.stateBoard.gravity = tilt.gravity;
	},
};
