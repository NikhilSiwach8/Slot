/**
 * Runs the six reels as one spin and hands the result over to the template's
 * board (which handles tumbles and wins). Rendering lives in
 * components/ReelSpinner.svelte; this module never touches Pixi.
 *
 *   start()  – on bet press: reels launch before the result is known
 *   land(e)  – on the reveal event: reels stop left to right on exactly e.board
 */
import { stateBet } from 'state-shared';

import config from '../config';
import { BOARD_DIMENSIONS, MULTIPLIER_VALUES } from '../constants';
import { eventEmitter } from '../eventEmitter';
import { stateGame, stateGameDerived } from '../stateGame.svelte';
import type { RawSymbol } from '../types';
import { REEL_SPIN_CONFIG, REEL_SPIN_TURBO, type ReelSpinConfig } from './config';
import { ReelMotion, type TapeSymbol } from './reelMotion';

type RevealLike = { board: RawSymbol[][]; anticipation?: number[]; gameType?: string };

const strips = config.paddingReels as unknown as Record<string, { name: string }[][]>;

export const stateReelSpin = $state({
	/** the spinner is drawing the reels (the template board is hidden) */
	active: false,
	/** board shake offset in px */
	shake: { x: 0, y: 0 },
	/** darken symbols that are not part of the current win */
	dimNonWinning: false,
});

let hurried = false;
const currentConfig = (): ReelSpinConfig =>
	stateBet.isTurbo || hurried ? { ...REEL_SPIN_CONFIG, ...REEL_SPIN_TURBO } : REEL_SPIN_CONFIG;

// filler symbols come from the game's own reel strips, from a random point each spin
let stripOffsets: number[] = new Array(BOARD_DIMENSIONS.x).fill(0);
const filler = (reelIndex: number) => (index: number): TapeSymbol => {
	const strip = strips[stateGame.gameType === 'basegame' ? 'basegame' : 'freegame']?.[reelIndex] ??
		strips.basegame[reelIndex];
	const raw = strip[(((stripOffsets[reelIndex] - index) % strip.length) + strip.length) % strip.length];
	if (raw.name === 'M') {
		return { name: 'M', multiplier: MULTIPLIER_VALUES[Math.abs(index * 7 + reelIndex) % 4] };
	}
	return raw.name === 'S' ? { name: 'S', scatter: true } : { name: raw.name };
};

export const reels = Array.from(
	{ length: BOARD_DIMENSIONS.x },
	(_, reelIndex) => new ReelMotion(reelIndex, currentConfig, filler(reelIndex)),
);

let startedAt = 0;
// which reels the current reveal anticipates (scatter tease)
let pendingAnticipation: boolean[] = [];
let landResolve: (() => void) | null = null;
let shakeUntil = 0;
let shakeStrength = 0;

let shakeDuration = 120;
const shake = (now: number, strength: number, duration: number) => {
	shakeStrength = strength;
	shakeDuration = duration;
	shakeUntil = now + duration;
};

/** Shake the board (e.g. big wins). */
export const shakeBoard = (strength: number, duration: number) => shake(performance.now(), strength, duration);

export const reelSpin = {
	/** Launch the reels from whatever the board shows now. */
	start(now = performance.now()) {
		if (stateReelSpin.active) return;
		hurried = false;
		stripOffsets = stripOffsets.map(() => Math.floor(Math.random() * 10_000));
		const showing = stateGameDerived.boardRaw();
		reels.forEach((reel, reelIndex) => reel.setResting(showing[reelIndex] as TapeSymbol[]));
		stateReelSpin.active = true;
		eventEmitter.broadcast({ type: 'boardHide' });
		reels.forEach((reel) => reel.start(now));
		startedAt = now;
		shake(now, currentConfig().launchShake, 120);
	},

	/** Stop on the revealed board. Resolves once every reel has settled. */
	land(reveal: RevealLike, now = performance.now()): Promise<void> {
		if (!stateReelSpin.active) this.start(now);
		const c = currentConfig();
		pendingAnticipation = reels.map((_, reelIndex) => (reveal.anticipation?.[reelIndex] ?? 0) > 0);
		const earliest = Math.max(now, startedAt + c.spinAcceleration + c.spinDuration);
		let extra = 0;
		reels.forEach((reel, reelIndex) => {
			if ((reveal.anticipation?.[reelIndex] ?? 0) > 0) extra += c.anticipationDelay;
			reel.requestStop(reveal.board[reelIndex] as TapeSymbol[], earliest + reelIndex * c.reelStopDelay + extra, now);
		});
		return new Promise((resolve) => {
			landResolve = () => {
				// hand over to the template board, already showing the result
				stateGameDerived.enhancedBoard.settle(reveal.board);
				stateGame.board.forEach((reel) => (reel.reelState.anticipating = false));
				eventEmitter.broadcast({ type: 'boardShow' });
				stateReelSpin.active = false;
				resolve();
			};
		});
	},

	/** Stop button: bring all pending stops forward and use the turbo timings. */
	hurry(now = performance.now()) {
		if (!stateReelSpin.active) return;
		hurried = true;
		reels.forEach((reel, reelIndex) => reel.hurry(now + reelIndex * currentConfig().reelStopDelay, now));
	},

	/** Advance one frame. Called by the renderer's ticker; returns reels that just landed. */
	update(now: number): number[] {
		const landed: number[] = [];
		reels.forEach((reel, reelIndex) => {
			const wasSpinning = reel.spinning;
			reel.update(now);
			if (wasSpinning && reel.justStopped) landed.push(reelIndex);
		});

		for (const reelIndex of landed) {
			eventEmitter.broadcast({ type: 'soundOnce', name: 'sfx_reel_stop_1', forcePlay: !stateBet.isTurbo });
			// scatter / cap landing sounds, as the template board did
			for (let row = 0; row < 5; row++) {
				const symbol = reels[reelIndex].symbolAt(row);
				stateGameDerived.onSymbolLand({ rawSymbol: symbol as RawSymbol });
			}
			// tease the next reel if it is anticipated
			const next = stateGame.board[reelIndex + 1];
			stateGame.board[reelIndex].reelState.anticipating = false;
			if (next && reels[reelIndex + 1].spinning && pendingAnticipation[reelIndex + 1]) {
				next.reelState.anticipating = true;
			}
			shake(now, 1.5, 70);
		}

		if (landResolve && reels.every((reel) => !reel.spinning)) {
			const resolve = landResolve;
			landResolve = null;
			resolve();
		}

		return landed;
	},

	/** Advance the board shake; runs every frame, spinning or not. */
	updateShake(now: number) {
		if (now < shakeUntil) {
			const fade = Math.min(1, (shakeUntil - now) / shakeDuration);
			stateReelSpin.shake = {
				x: Math.sin(now * 0.071) * shakeStrength * 0.4 * fade,
				y: Math.sin(now * 0.09) * shakeStrength * fade,
			};
		} else if (stateReelSpin.shake.y !== 0 || stateReelSpin.shake.x !== 0) {
			stateReelSpin.shake = { x: 0, y: 0 };
		}
	},

	config: currentConfig,
};
