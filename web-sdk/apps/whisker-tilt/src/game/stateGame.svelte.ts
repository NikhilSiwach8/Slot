import { createGetWinLevelDataByWinLevelAlias } from 'utils-shared/winLevel';

import type { FreeSpinKind } from './types';
import { stateLayoutDerived } from './stateLayout';
import { winLevelMap } from './winLevelMap';
import { eventEmitter } from './eventEmitter';
import { BOARD_SIZES, BOARD_SCALE, SCATTER_LAND_SOUND_MAP } from './constants';
import { boardRaw, type BoardCell } from './tiltBoard.svelte';

export const stateGame = $state({
	/** 'basegame', or the free spins ('freeSpins' while the intro plays, 'freegame' from reveals) */
	gameType: 'basegame' as string,
	/** which free spins are running: Snow Day or Super Snow Day */
	freeSpinKind: 'free' as FreeSpinKind,
	scatterCounter: 0,
	/** Off the Shelf: progress toward the cap (0..1), or null outside that mode */
	crack: null as number | null,
});

const scatterLandIndex = () => {
	if (stateGame.scatterCounter > 5) return 5;
	if (stateGame.scatterCounter < 1) return 1;
	return stateGame.scatterCounter as 1 | 2 | 3 | 4 | 5;
};

const onSymbolLand = (raw: BoardCell['raw']) => {
	if (raw.name === 'S') {
		stateGame.scatterCounter += 1;
		eventEmitter.broadcast({ type: 'soundOnce', name: SCATTER_LAND_SOUND_MAP[scatterLandIndex()] });
	}
};

const boardScale = () => BOARD_SCALE[stateLayoutDerived.layoutType()] ?? 0.76;

/** Centre of the board on the main layout, and its on-screen (scaled) size. */
const boardLayout = () => {
	const scale = boardScale();
	return {
		x: stateLayoutDerived.mainLayout().width * 0.5,
		y: stateLayoutDerived.mainLayout().height * 0.45,
		anchor: { x: 0.5, y: 0.5 },
		pivot: { x: BOARD_SIZES.width / 2, y: BOARD_SIZES.height / 2 },
		scale,
		width: BOARD_SIZES.width * scale,
		height: BOARD_SIZES.height * scale,
	};
};

export const { getWinLevelDataByWinLevelAlias } = createGetWinLevelDataByWinLevelAlias({
	winLevelMap,
});

export const stateGameDerived = {
	onSymbolLand,
	boardLayout,
	boardScale,
	boardRaw,
	scatterLandIndex,
	getWinLevelDataByWinLevelAlias,
};
