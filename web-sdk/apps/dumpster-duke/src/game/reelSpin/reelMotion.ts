/**
 * Reel motion model — pure logic, no rendering.
 *
 * Each reel is an endless tape of symbols indexed by integer position. A tape
 * index `i` is drawn at row `i + scroll` (row 0 = top visible row), so increasing
 * `scroll` moves the content down. When the result arrives, the revealed board is
 * written onto the tape far enough above the window that it is never visible
 * early, and the reel is steered so that it comes to rest with `scroll` exactly an
 * integer N — which puts the result precisely in the window. Filler symbols come
 * from the game's own reel strips.
 */
import type { ReelSpinConfig } from './config';

export type TapeSymbol = { name: string; multiplier?: number; scatter?: boolean };

type Phase = 'idle' | 'launch' | 'cruise' | 'decel' | 'bounce';

const easeOutCubic = (u: number) => 1 - (1 - u) ** 3;
const easeOutQuad = (u: number) => 1 - (1 - u) ** 2;
const clamp01 = (u: number) => Math.max(0, Math.min(1, u));
const smoothstep = (u: number) => u * u * (3 - 2 * u);

/** Rows of the padded board: one hidden row above and one below the 5 visible rows. */
export const PADDED_ROWS = { top: -1, bottom: 5 };

export class ReelMotion {
	scroll = 0;
	velocity = 0; // symbols per ms (for blur / stretch)
	phase: Phase = 'idle';
	/** set when the reel has come to rest on its target this frame */
	justStopped = false;

	private tape = new Map<number, TapeSymbol>();
	private phaseStart = 0;
	private scrollAtPhaseStart = 0;
	private stopAt = Infinity; // time the reel may begin its stop sequence
	private target: number | null = null; // integer scroll to come to rest on
	private decelFrom = 0; // scroll at which deceleration begins
	private result: TapeSymbol[] | null = null;
	private lastTime = 0;
	private lastScroll = 0;

	private readonly reelIndex: number;
	private readonly config: () => ReelSpinConfig;
	private readonly filler: (index: number) => TapeSymbol;

	constructor(reelIndex: number, config: () => ReelSpinConfig, filler: (index: number) => TapeSymbol) {
		this.reelIndex = reelIndex;
		this.config = config;
		this.filler = filler;
	}

	/** Show these padded symbols (7 rows: hidden top, 5 visible, hidden bottom) at rest. */
	setResting(padded: TapeSymbol[]) {
		this.tape.clear();
		this.scroll = 0;
		this.velocity = 0;
		this.phase = 'idle';
		padded.forEach((symbol, k) => this.tape.set(k + PADDED_ROWS.top, symbol));
	}

	symbolAt(index: number): TapeSymbol {
		let symbol = this.tape.get(index);
		if (!symbol) {
			symbol = this.filler(index);
			this.tape.set(index, symbol);
		}
		return symbol;
	}

	/** Tape indices currently intersecting the window (plus one row each side). */
	visibleIndices(): number[] {
		const first = Math.floor(-this.scroll) + PADDED_ROWS.top;
		const out: number[] = [];
		for (let i = first; i <= first + 7; i++) out.push(i);
		return out;
	}

	get spinning() {
		return this.phase !== 'idle';
	}

	start(now: number) {
		if (this.spinning) return;
		this.phase = 'launch';
		this.phaseStart = now;
		this.scrollAtPhaseStart = this.scroll;
		this.stopAt = Infinity;
		this.target = null;
		this.result = null;
		this.lastTime = now;
		this.lastScroll = this.scroll;
	}

	/**
	 * Land on `padded` (7 symbols), starting to slow down at `stopAt`. The landing
	 * is planned straight away from where the reel will be at that moment, so the
	 * reel slows exactly on schedule with no extra run-in.
	 */
	requestStop(padded: TapeSymbol[], stopAt: number, now: number) {
		this.result = padded;
		this.stopAt = stopAt;
		this.planStop(now);
	}

	/** Bring a planned stop forward (stop button / turbo) if the result isn't in view yet. */
	hurry(stopAt: number, now: number) {
		if (!this.result || this.phase === 'decel' || this.phase === 'bounce' || this.phase === 'idle') return;
		if (stopAt >= this.stopAt) return;
		// the old landing spot is still out of sight: hand it back to filler and re-plan
		for (let r = PADDED_ROWS.top; r <= PADDED_ROWS.bottom; r++) this.tape.delete(r - this.target!);
		this.stopAt = stopAt;
		this.planStop(now);
	}

	/** Where the reel will be at `time` if it keeps cruising. */
	private predictScroll(time: number, now: number) {
		const c = this.config();
		const v = this.speed();
		if (this.phase === 'launch') {
			const launchEnd = this.phaseStart + c.spinAcceleration;
			const accelTime = c.spinAcceleration * 0.65;
			const atLaunchEnd = this.scrollAtPhaseStart + (v * accelTime) / 3;
			return atLaunchEnd + v * Math.max(0, time - launchEnd);
		}
		return this.scroll + v * Math.max(0, time - now);
	}

	private speed() {
		const c = this.config();
		return (c.maxReelSpeed / 1000) * (c.reelSpeedVariance[this.reelIndex] ?? 1);
	}

	/** Fix the landing position and write the result onto the tape above the window. */
	private planStop(now: number) {
		const c = this.config();
		const v = this.speed();
		const decelDistance = (v * c.decelerationDuration) / 3; // cubic ease-out from speed v
		const atStop = this.predictScroll(this.stopAt, now);
		// the result must be written where it can't be seen yet: > 7 rows above the window
		const target = Math.ceil(Math.max(this.scroll + 8, atStop + decelDistance - c.overshootAmount));
		this.target = target;
		this.decelFrom = target + c.overshootAmount - decelDistance;
		this.result!.forEach((symbol, k) => this.tape.set(k + PADDED_ROWS.top - target, symbol));
		// forget tape far below the window so it doesn't grow without bound
		for (const index of this.tape.keys()) if (index > -this.scroll + 12) this.tape.delete(index);
	}

	update(now: number) {
		this.justStopped = false;
		if (this.phase === 'idle') return;
		const c = this.config();
		const v = this.speed();
		const t = Math.max(0, now - this.phaseStart); // frame time can trail an event-time start by < 1 frame

		if (this.phase === 'launch') {
			// quick upward kick, then an ease-in drop to full speed
			const kickTime = c.spinAcceleration * 0.35;
			if (t < kickTime) {
				this.scroll = this.scrollAtPhaseStart - c.launchKick * Math.sin((t / kickTime) * Math.PI * 0.5);
			} else {
				const u = clamp01((t - kickTime) / (c.spinAcceleration - kickTime));
				const accelTime = c.spinAcceleration - kickTime;
				// the kick unwinds with zero speed at both ends, so the hand-over to cruise is seamless
				this.scroll = this.scrollAtPhaseStart - c.launchKick * (1 - smoothstep(u)) + (v * accelTime * u ** 3) / 3;
				if (u >= 1) {
					this.phase = 'cruise';
					this.phaseStart = now;
					this.scrollAtPhaseStart = this.scroll;
				}
			}
		} else if (this.phase === 'cruise') {
			this.scroll = this.scrollAtPhaseStart + v * t;
			if (this.target !== null && this.scroll >= this.decelFrom) {
				this.phase = 'decel';
				this.phaseStart = now - (this.scroll - this.decelFrom) / v;
				this.scrollAtPhaseStart = this.decelFrom;
			}
		} else if (this.phase === 'decel') {
			const u = clamp01(t / c.decelerationDuration);
			const end = this.target! + c.overshootAmount;
			this.scroll = this.decelFrom + (end - this.decelFrom) * easeOutCubic(u);
			if (u >= 1) {
				this.phase = 'bounce';
				this.phaseStart = now;
			}
		} else if (this.phase === 'bounce') {
			const u = clamp01(t / c.bounceDuration);
			this.scroll = this.target! + c.overshootAmount * (1 - easeOutQuad(u));
			if (u >= 1) {
				this.scroll = this.target!; // snap exactly onto the result
				this.phase = 'idle';
				this.result = null;
				this.justStopped = true;
				// renumber so the resting window is tape rows 0..4 again
				const settled = new Map<number, TapeSymbol>();
				for (let r = PADDED_ROWS.top; r <= PADDED_ROWS.bottom; r++) settled.set(r, this.symbolAt(r - this.target!));
				this.tape = settled;
				this.scroll = 0;
				this.target = null;
			}
		}

		const dt = Math.max(1, now - this.lastTime);
		this.velocity = this.phase === 'idle' ? 0 : (this.scroll - this.lastScroll) / dt;
		this.lastTime = now;
		this.lastScroll = this.scroll;
	}

	/** 0..1 how fast the reel is moving relative to full speed (for blur / stretch) */
	speedRatio() {
		return clamp01(Math.abs(this.velocity) / this.speed());
	}
}
