# Whisker Tilt — math model

StakeEngine math-sdk game for the [Whisker Tilt concept](../../concepts/whisker-tilt/CONCEPT.md):
6×6 cluster pays (5+), gravity turns 90° clockwise after every winning cascade, four Edge
Keepers (one per wall) multiply the clusters that touch their wall.

```bash
scripts/setup.sh                                   # restores math-sdk, links this folder in
cd math-sdk
env/bin/python games/whisker_tilt/run.py           # all 7 modes: sims + optimizer + checks
SIM_SCALE=0.05 env/bin/python games/whisker_tilt/run.py   # quick smoke run
python3 games/whisker_tilt/analyze.py              # RTP, hit rate, max win per mode
cd games/whisker_tilt && PYTHONPATH=../.. ../../env/bin/python profile_criteria.py bonus freegame 1000
python3 make_reels.py                              # regenerate reels/*.csv
```

## Files

| File | What |
|---|---|
| `game_config.py` | board, paytable, keys, coin values, Edge Keeper starts, Mitten's Gift table, the 7 bet modes |
| `game_calculations.py` | gravity lanes, `settle` (slide + refill from the far wall), clusters with wall multipliers |
| `game_executables.py` | the Tilt Tumble loop, coin banking, Snowstorm, feature entry, Off the Shelf zeroing |
| `game_events.py` | the new book events (below) |
| `gamestate.py` | base spin and free-spin flow |
| `game_optimization.py` | Rust-optimizer targets for the buy modes (bonus, super, mystery, max_or_nothing) |
| `natural_weights.py` | weights for base, ante and feature: every book in a criteria weighs the same, criteria shares set the trigger rate, max-win rate and RTP |
| `make_reels.py` | reel strips: `BR0` base, `BRA` Catnip, `FR0` Snow Day, `FRS` Super, `WCAP` max-win builder |

## Why base modes skip the optimizer

The Rust optimizer builds each criteria's distribution from random bell curves around the
target average. For this game that bunched base-mode bonuses around ~85× and squeezed base
wins of 1–5× from 1 in 4 spins to 1 in 218. `natural_weights.py` keeps the simulated spread
and only sets how often each criteria happens. The buy modes keep the optimizer, which left
their shape close to the simulations.

## How the tilt is simulated

Each refill lane is a column (gravity up/down) or a row (left/right), read from the wall
symbols enter at to the floor. Falling down continues the drawn reels upward exactly like
a normal tumble; the other three directions pull from the same strips, from their own
random stops. Lane `i` always refills from strip `i`.

## Book events

Positions are screen coordinates (`reel` = column from the West wall, `row` = 0 at the North
wall, no padding row). Gravity/wall index: 0 down/South, 1 left/West, 2 up/North, 3 right/East.

| Event | Fields |
|---|---|
| `reveal` | SDK event; the board lands along the current gravity |
| `tilt` | `gravity`, `turn`, `cause` (`cascade` after a win, `paw` before each free spin) |
| `snowstorm` | `turn`, `keepers` after doubling (every 4th turn) |
| `settleBoard` | `cause` (`cascade`/`bank`), `gravity`, `removed`, `newSymbols` (`reel`, `row`, symbol). Survivors slide toward the floor wall in their lane, keeping their order |
| `keeperBank` | `wall`, `coins` (`reel`, `row`, `value`), `keepers` |
| `keepersInit` | `keepers` when a round starts with lit walls (Paw Spins, Super Snow Day) |
| `winInfo` | SDK event; `meta.clusterMult` is the wall multiplier, `meta.walls` the walls touched |
| `mysteryReveal` | `kind` (`free`/`super`), `spins` |
| `crackMeter` | Off the Shelf only: `progress` 0–1 toward the cap, sent instead of win totals |
| `shelfResult` | Off the Shelf only: `shattered` (true = paid the max win) |

Off the Shelf books keep `winInfo` (needed to animate clusters) but leave out `setWin`,
`setTotalWin` and `updateTumbleWin`; their `freeSpinEnd` amount is the real payout (0 or the cap).
