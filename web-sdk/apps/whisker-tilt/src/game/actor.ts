import _ from 'lodash';

import { stateBet } from 'state-shared';
import { checkIsMultipleRevealEvents } from 'utils-book';
import { createPrimaryMachines, createIntermediateMachines, createGameActor } from 'utils-xstate';

import type { Bet } from './typesBookEvent';
import { stateXstateDerived } from './stateXstate';
import { playBet, convertTorResumableBet } from './utils';
import * as board from './tiltBoard.svelte';

const primaryMachines = createPrimaryMachines<Bet>({
	onResumeGameActive: (betToResume) => convertTorResumableBet(betToResume),
	onResumeGameInactive: (betToResume) => {
		const lastReveal = _.findLast(betToResume.state, (bookEvent) => bookEvent?.type === 'reveal');
		if (lastReveal && lastReveal.type === 'reveal') board.show(lastReveal.board);
	},
	onNewGameStart: async () => {
		// every base spin starts with unlit keepers and gravity pointing down
		board.setKeepers([0, 0, 0, 0]);
		board.stateBoard.gravity = 'down';
		if ((stateBet.isTurbo && stateXstateDerived.isAutoBetting()) || stateBet.isSpaceHold) return;
		stateBet.winBookEventAmount = 0;
		// the old board falls out straight away; the reveal fills it when the result arrives
		board.dropOut();
	},
	onNewGameError: () => board.show(),
	onPlayGame: async (bet) => await playBet(bet),
	checkIsBonusGame: (bet) => checkIsMultipleRevealEvents({ bookEvents: bet.state }),
});

const intermediateMachines = createIntermediateMachines(primaryMachines);

export const gameActor = createGameActor(intermediateMachines);
