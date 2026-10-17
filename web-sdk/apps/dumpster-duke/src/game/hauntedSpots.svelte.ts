// Haunted Spots (cluster pays): per reel, per visible row; 0 = clear, 1 = haunted,
// 2+ = multiplier for clusters that win on that spot. Set from the math's
// `hauntedSpots` book events; cleared every base spin and when a raid starts or ends.
import { BOARD_DIMENSIONS } from './constants';

const empty = () => Array.from({ length: BOARD_DIMENSIONS.x }, () => Array(BOARD_DIMENSIONS.y).fill(0) as number[]);

export const stateHauntedSpots = $state({
	spots: empty(),
	// performance.now() of the last change per spot, for the pop animation
	changedAt: empty(),
});

export const setHauntedSpots = (spots: number[][]) => {
	const now = performance.now();
	spots.forEach((reel, r) =>
		reel.forEach((value, c) => {
			if (stateHauntedSpots.spots[r]?.[c] !== value) stateHauntedSpots.changedAt[r][c] = now;
		}),
	);
	stateHauntedSpots.spots = spots.map((reel) => [...reel]);
};

export const clearHauntedSpots = () => {
	if (stateHauntedSpots.spots.some((reel) => reel.some((v) => v > 0))) {
		stateHauntedSpots.spots = empty();
		stateHauntedSpots.changedAt = empty();
	}
};
