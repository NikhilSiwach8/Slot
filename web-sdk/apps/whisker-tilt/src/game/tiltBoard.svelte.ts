/**
 * The Whisker Tilt board: a 6x6 grid of symbols that slide toward whichever wall is the
 * floor. This module owns the board state and its animations; components/TiltBoard.svelte
 * only draws it. Positions are screen coordinates (reel = column from the West wall,
 * row = 0 at the North wall), the same as the math books.
 *
 *   dropOut()          bet pressed: the old symbols fall out through the floor
 *   reveal(board)      a reveal event: new symbols fall in from the far wall and land
 *   settle(...)        a settleBoard event: removed symbols pop, survivors slide, new ones fall in
 *   bankCoins(...)     a keeperBank event: coins fly to the floor wall's keeper
 *   highlight(...)     winning clusters pulse, the rest dim
 *   tilt(gravity)      Mitten bats the box: it wobbles and gravity turns
 */
import { stateBet } from 'state-shared';

import {
	BOARD_DIMENSIONS,
	GRAVITIES,
	GRAVITY_STEP,
	INITIAL_BOARD,
	SYMBOL_SIZE,
	WALLS,
} from './constants';
import type { Gravity, Position, RawSymbol, Wall } from './types';

export type BoardCell = {
	id: number;
	raw: RawSymbol;
	/** centre in board pixels */
	x: number;
	y: number;
	scale: number;
	alpha: number;
	rotation: number;
	/** 0..1 win glow */
	glow: number;
};

const N = BOARD_DIMENSIONS.x;
let nextId = 1;

export const cellX = (reel: number) => (reel + 0.5) * SYMBOL_SIZE;
export const cellY = (row: number) => (row + 0.5) * SYMBOL_SIZE;

const makeCell = (raw: RawSymbol, reel: number, row: number): BoardCell => ({
	id: nextId++,
	raw,
	x: cellX(reel),
	y: cellY(row),
	scale: 1,
	alpha: 1,
	rotation: 0,
	glow: 0,
});

export const stateBoard = $state({
	/** [reel][row]; null while a cell is empty mid-animation */
	grid: INITIAL_BOARD.map((reel, r) => reel.map((raw, row) => makeCell(raw, r, row))) as (BoardCell | null)[][],
	/** cells animating off the board (no longer in the grid) */
	leaving: [] as BoardCell[],
	gravity: 'down' as Gravity,
	keepers: [0, 0, 0, 0],
	/** 0..1 flash per keeper when its value changes */
	keeperPulse: [0, 0, 0, 0],
	/** box wobble when Mitten bats it, radians */
	wobble: 0,
	/** Snowstorm whiteout, 0..1 */
	flash: 0,
	/** darken symbols that are not part of the current win */
	dimOthers: false,
	winning: new Set<number>(),
});

// --- timing --------------------------------------------------------------------

const speed = () => (stateBet.isTurbo ? 0.45 : 1);
export const easeOutCubic = (u: number) => 1 - (1 - u) ** 3;
export const easeInCubic = (u: number) => u ** 3;
export const easeOutBack = (u: number, s = 1.4) => 1 + (s + 1) * (u - 1) ** 3 + s * (u - 1) ** 2;

/** Run `step(t)` for t in 0..1 over `ms` (scaled down in turbo). */
export const animate = (ms: number, step: (t: number) => void, delay = 0) =>
	new Promise<void>((resolve) => {
		const duration = Math.max(1, ms * speed());
		const wait = delay * speed();
		const start = performance.now() + wait;
		const tick = (now: number) => {
			const t = Math.max(0, Math.min(1, (now - start) / duration));
			if (now >= start) step(t);
			if (t < 1) requestAnimationFrame(tick);
			else resolve();
		};
		requestAnimationFrame(tick);
	});

// --- lanes ---------------------------------------------------------------------

/** Cells of one lane ordered from the wall symbols enter at to the floor (as in the math). */
export const laneCells = (gravity: Gravity, lane: number): [number, number][] => {
	const idx = [...Array(N).keys()];
	if (gravity === 'down') return idx.map((row) => [lane, row]);
	if (gravity === 'up') return idx.reverse().map((row) => [lane, row]);
	if (gravity === 'left') return idx.reverse().map((reel) => [reel, lane]);
	return idx.map((reel) => [reel, lane]);
};

const forEachCell = (fn: (cell: BoardCell, reel: number, row: number) => void) =>
	stateBoard.grid.forEach((reel, r) => reel.forEach((cell, row) => cell && fn(cell, r, row)));

export const boardRaw = (): RawSymbol[][] =>
	stateBoard.grid.map((reel) => reel.map((cell) => cell?.raw ?? { name: 'L1' }));

// --- operations ------------------------------------------------------------------

/** Put a board on screen without animation (resume, errors, stories). */
export const show = (board: RawSymbol[][] = INITIAL_BOARD, gravity: Gravity = stateBoard.gravity) => {
	stateBoard.gravity = gravity;
	stateBoard.leaving = [];
	stateBoard.grid = board.map((reel, r) => reel.map((raw, row) => makeCell(raw, r, row)));
};

let dropping: Promise<void> | null = null;

/** Bet pressed: everything on the board falls out through the floor wall. */
export const dropOut = () => {
	if (dropping) return dropping;
	const step = GRAVITY_STEP[stateBoard.gravity];
	const cells: { cell: BoardCell; x: number; y: number; delay: number }[] = [];
	forEachCell((cell, reel, row) => {
		const depth = step.x !== 0 ? (step.x > 0 ? N - 1 - reel : reel) : step.y > 0 ? N - 1 - row : row;
		const lane = step.x !== 0 ? row : reel;
		cells.push({ cell, x: cell.x, y: cell.y, delay: lane * 25 + depth * 18 });
	});
	stateBoard.leaving = cells.map((c) => c.cell);
	stateBoard.grid = stateBoard.grid.map((reel) => reel.map(() => null));
	const distance = SYMBOL_SIZE * (N + 1);
	dropping = Promise.all(
		cells.map(({ cell, x, y, delay }) =>
			animate(
				260,
				(t) => {
					const e = easeInCubic(t);
					cell.x = x + step.x * distance * e;
					cell.y = y + step.y * distance * e;
				},
				delay,
			),
		),
	).then(() => {
		stateBoard.leaving = [];
		dropping = null;
	});
	return dropping;
};

/** A reveal event: the board falls in from the far wall along the current gravity. */
export const reveal = async (
	board: RawSymbol[][],
	{ onLand }: { onLand?: (raw: RawSymbol) => void } = {},
) => {
	if (stateBoard.grid.some((reel) => reel.some(Boolean))) await dropOut();
	else if (dropping) await dropping;

	const step = GRAVITY_STEP[stateBoard.gravity];
	const distance = SYMBOL_SIZE * (N + 1);
	const grid: (BoardCell | null)[][] = board.map((reel) => reel.map(() => null));
	const moves: Promise<void>[] = [];
	for (let lane = 0; lane < N; lane++) {
		laneCells(stateBoard.gravity, lane).forEach(([reel, row], i) => {
			const raw = board[reel][row];
			const cell = makeCell(raw, reel, row);
			const tx = cell.x;
			const ty = cell.y;
			cell.x = tx - step.x * distance;
			cell.y = ty - step.y * distance;
			grid[reel][row] = cell;
			// the floor end of each lane lands first, lanes ripple across the board
			const delay = lane * 45 + (N - 1 - i) * 30;
			moves.push(
				animate(
					380,
					(t) => {
						const e = easeOutBack(t, 1.1);
						cell.x = tx - step.x * distance * (1 - e);
						cell.y = ty - step.y * distance * (1 - e);
					},
					delay,
				).then(() => onLand?.(raw)),
			);
		});
	}
	stateBoard.grid = grid;
	await Promise.all(moves);
};

/**
 * A settleBoard event: `removed` cells pop, survivors slide toward the floor keeping their
 * order, and `newSymbols` fall in from beyond the far wall into the cells left free.
 */
export const settle = async ({
	gravity,
	removed,
	newSymbols,
}: {
	gravity: Gravity;
	removed: Position[];
	newSymbols: (Position & RawSymbol)[];
}) => {
	stateBoard.gravity = gravity;
	const gone = new Set(removed.map((p) => `${p.reel},${p.row}`));
	const fresh = new Map(newSymbols.map((s) => [`${s.reel},${s.row}`, s]));

	// pop the removed cells
	const popping: BoardCell[] = [];
	removed.forEach(({ reel, row }) => {
		const cell = stateBoard.grid[reel][row];
		if (cell) popping.push(cell);
	});
	await animate(200, (t) =>
		popping.forEach((cell) => {
			cell.scale = 1 + 0.3 * t;
			cell.alpha = Math.min(cell.alpha, 1 - t);
		}),
	);

	const step = GRAVITY_STEP[gravity];
	const grid: (BoardCell | null)[][] = stateBoard.grid.map((reel) => reel.map(() => null));
	const moves: Promise<void>[] = [];
	for (let lane = 0; lane < N; lane++) {
		const cells = laneCells(gravity, lane);
		const survivors = cells
			.filter(([r, c]) => !gone.has(`${r},${c}`))
			.map(([r, c]) => stateBoard.grid[r][c])
			.filter((cell): cell is BoardCell => cell !== null);
		const k = cells.length - survivors.length;
		// survivors fill the floor end of the lane, in order
		survivors.forEach((cell, i) => {
			const [reel, row] = cells[k + i];
			grid[reel][row] = cell;
			const fromX = cell.x;
			const fromY = cell.y;
			const toX = cellX(reel);
			const toY = cellY(row);
			if (fromX !== toX || fromY !== toY) {
				const cellsMoved = Math.abs(toX - fromX + (toY - fromY)) / SYMBOL_SIZE;
				moves.push(
					animate(220 + cellsMoved * 45, (t) => {
						const e = easeOutBack(t, 0.9);
						cell.x = fromX + (toX - fromX) * e;
						cell.y = fromY + (toY - fromY) * e;
					}),
				);
			}
		});
		// new symbols enter from beyond the far wall, as if the lane continued outside the box
		cells.slice(0, k).forEach(([reel, row], i) => {
			const incoming = fresh.get(`${reel},${row}`);
			const { reel: _r, row: _c, ...raw } = incoming ?? { reel, row, name: 'L1' as const };
			const cell = makeCell(raw as RawSymbol, reel, row);
			const toX = cell.x;
			const toY = cell.y;
			cell.x = toX - step.x * SYMBOL_SIZE * (k + 0.5);
			cell.y = toY - step.y * SYMBOL_SIZE * (k + 0.5);
			grid[reel][row] = cell;
			const fromX = cell.x;
			const fromY = cell.y;
			moves.push(
				animate(
					300 + k * 45,
					(t) => {
						const e = easeOutBack(t, 0.9);
						cell.x = fromX + (toX - fromX) * e;
						cell.y = fromY + (toY - fromY) * e;
					},
					(k - 1 - i) * 30 + lane * 20,
				),
			);
		});
	}
	stateBoard.grid = grid;
	await Promise.all(moves);
};

/** Board-space point where a wall's keeper stands (just outside the board window). */
export const wallAnchor = (wall: Wall) => {
	const size = SYMBOL_SIZE * N;
	const out = SYMBOL_SIZE * 0.95;
	return {
		south: { x: size / 2, y: size + out },
		west: { x: -out, y: size / 2 },
		north: { x: size / 2, y: -out },
		east: { x: size + out, y: size / 2 },
	}[wall];
};

/** A keeperBank event: the coins fly into the floor wall's keeper, whose value then updates. */
export const bankCoins = async ({
	wall,
	coins,
	keepers,
}: {
	wall: Wall;
	coins: (Position & { value: number })[];
	keepers: number[];
}) => {
	const target = wallAnchor(wall);
	const flying = coins
		.map(({ reel, row }) => stateBoard.grid[reel][row])
		.filter((cell): cell is BoardCell => cell !== null);
	await Promise.all(
		flying.map((cell, i) => {
			const fromX = cell.x;
			const fromY = cell.y;
			return animate(
				420,
				(t) => {
					const e = easeInCubic(t);
					cell.x = fromX + (target.x - fromX) * e;
					cell.y = fromY + (target.y - fromY) * e - Math.sin(t * Math.PI) * SYMBOL_SIZE * 0.6;
					cell.scale = 1 - 0.55 * e;
					cell.alpha = t < 0.85 ? 1 : (1 - t) / 0.15;
				},
				i * 80,
			);
		}),
	);
	setKeepers(keepers);
};

export const setKeepers = (keepers: number[]) => {
	const changed = keepers.map((value, i) => value !== stateBoard.keepers[i]);
	stateBoard.keepers = [...keepers];
	changed.forEach((did, i) => {
		if (!did) return;
		animate(600, (t) => (stateBoard.keeperPulse[i] = 1 - t));
	});
};

/** A Snowstorm: whiteout, then every keeper shows its doubled value. */
export const snowstorm = async (keepers: number[]) => {
	await animate(260, (t) => (stateBoard.flash = t));
	setKeepers(keepers);
	await animate(520, (t) => (stateBoard.flash = 1 - t));
};

/** Winning clusters pulse and glow while everything else dims. */
export const highlight = async (positions: Position[]) => {
	const cells = positions
		.map(({ reel, row }) => stateBoard.grid[reel][row])
		.filter((cell): cell is BoardCell => cell !== null);
	stateBoard.winning = new Set(cells.map((cell) => cell.id));
	stateBoard.dimOthers = true;
	await animate(900, (t) =>
		cells.forEach((cell) => {
			const pulse = t < 0.35 ? Math.sin((t / 0.35) * Math.PI) * 0.18 : 0;
			cell.scale = 1 + pulse;
			cell.rotation = Math.sin(t * Math.PI * 5) * 0.06 * (1 - t);
			cell.glow = t < 0.2 ? t / 0.2 : 1 - (t - 0.2) / 0.8;
		}),
	);
	stateBoard.dimOthers = false;
	stateBoard.winning = new Set();
};

/** Mitten bats the box: a quick wobble in the turning direction, then gravity points anew. */
export const tilt = async (gravity: Gravity) => {
	const turn = GRAVITIES.indexOf(gravity) === (GRAVITIES.indexOf(stateBoard.gravity) + 1) % 4 ? 1 : -1;
	stateBoard.gravity = gravity;
	await animate(480, (t) => {
		stateBoard.wobble = turn * 0.09 * Math.sin(t * Math.PI * 2.5) * (1 - t);
	});
	stateBoard.wobble = 0;
};

export const wallIndex = (wall: Wall) => WALLS.indexOf(wall);
