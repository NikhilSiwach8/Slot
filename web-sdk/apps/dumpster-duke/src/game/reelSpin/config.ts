// Tunable reel-spin feel. Times are in ms, distances in symbols (1 = one symbol
// height) unless noted. `turbo` overrides apply when turbo is on or the player
// hits stop.

export type ReelSpinConfig = {
	/** launch: time from rest to full speed (ease-in) */
	spinAcceleration: number;
	/** launch: small upward pull before the reels drop, in symbols */
	launchKick: number;
	/** cruise speed in symbols per second */
	maxReelSpeed: number;
	/** per-reel speed multipliers so the reels don't scroll in lock-step */
	reelSpeedVariance: number[];
	/** minimum time at full speed before the first reel may stop */
	spinDuration: number;
	/** ease-out time from full speed to the overshoot point */
	decelerationDuration: number;
	/** delay between consecutive reel stops (left to right) */
	reelStopDelay: number;
	/** extra spin time for a reel that is being anticipated (scatter tease) */
	anticipationDelay: number;
	/** how far a reel runs past its stop before bouncing back, in symbols */
	overshootAmount: number;
	/** time to settle back from the overshoot */
	bounceDuration: number;
	/** vertical blur in px at full speed (scaled down with speed) */
	motionBlurAmount: number;
	/** vertical stretch of symbols at full speed (0.1 = +10%) */
	speedStretch: number;
	/** distance between symbol centres, in symbol heights */
	symbolSpacing: number;
	/** board shake on launch, in px */
	launchShake: number;
};

export const REEL_SPIN_CONFIG: ReelSpinConfig = {
	spinAcceleration: 110,
	launchKick: 0.12,
	maxReelSpeed: 32,
	reelSpeedVariance: [1, 1.03, 0.98, 1.04, 0.97, 1.02],
	spinDuration: 650,
	decelerationDuration: 230,
	reelStopDelay: 115,
	anticipationDelay: 550,
	overshootAmount: 0.16,
	bounceDuration: 150,
	motionBlurAmount: 14,
	speedStretch: 0.12,
	symbolSpacing: 1,
	launchShake: 5,
};

export const REEL_SPIN_TURBO: Partial<ReelSpinConfig> = {
	spinAcceleration: 70,
	spinDuration: 150,
	decelerationDuration: 150,
	reelStopDelay: 35,
	anticipationDelay: 300,
	bounceDuration: 100,
};
