# Whisker Tilt — concept

> Status: concept / pre-math. Working title. Second title for the nyxhilx Stake Engine
> lineup, after Dumpster Duke. Prototype of the core mechanic: [`prototype/tilt.py`](prototype/tilt.py).

## 1. Pitch

It's midnight in an old toyshop. On the top shelf sits a square glass **snow box** with a
tiny winter village inside, and **Mitten**, the shop cat, can't stop pawing at it. Every
time a win clears out, Mitten bats the box a quarter turn: **gravity rotates**, the
whole village slides into a new wall, fresh snow-globe pieces fall in from the opposite
side, and the **Edge Keeper** standing on the new floor scoops up any snowflake coins
that slid onto their side.

One line: *a cluster tumble where the board doesn't refill from above — it falls in
whichever direction the cat just turned it, and the four walls of the box each hold
their own multiplier.*

Tone: cosy-mischievous. Warm toyshop amber outside the glass, cold blue-white village
inside; Mitten's huge paw and eye fill the background between spins.

## 2. Why it's different

| Usual cluster tumble | Whisker Tilt |
|---|---|
| Symbols always fall down, refill from the top | Gravity turns 90° clockwise after every winning cascade: down → left → up → right |
| Multiplier lives on a cell spot or a global meter | Multipliers live on the **four walls** of the board; a cluster is multiplied by every wall it touches |
| Board position doesn't matter | Position matters: corner clusters touch two walls, centre clusters touch none |
| Long cascades only add more wins | Every 4th tilt is a **full turn** → *Snowstorm*: all four walls double |

The rotation is easy to read (the whole box visibly turns), so the novelty costs the
player no learning curve: "things fall toward the floor, the floor keeps changing".

## 3. Board and pays

- **6×6** square grid (square so every rotation keeps the same shape).
- **Cluster pays**: 5+ identical symbols connected horizontally/vertically.
- Pay brackets: 5, 6, 7, 8, 9–10, 11–12, 13–15, 16+.

| Code | Symbol | Notes |
|---|---|---|
| H1 | Golden Sleigh | top pay |
| H2 | Gingerbread House | |
| H3 | Nutcracker Guard | |
| H4 | Snowman with a cat-scratched scarf | |
| L1–L4 | Glass baubles: red, blue, green, gold | four distinct shapes for colour-blind reading (round, teardrop, star, bell) |
| S | Wind-up Key (scatter) | winds the box's music drum; triggers the bonus |
| C | Snowflake Coin (x2 – x50) | not part of clusters; banked by an Edge Keeper |

Placeholder paytable lives in the prototype; final values come from the math model.

## 4. Core mechanic: Tilt Tumble

1. Symbols drop in with gravity pointing **down** (base game always starts here).
2. **Coin banking:** any Snowflake Coin resting against the current floor wall is taken by
   that wall's Edge Keeper (its value is added to the keeper), the coin leaves, and the gap
   refills. Repeat until no coin is on the floor.
3. **Evaluate clusters.** Each winning cluster pays
   `pay(symbol, size) × max(1, sum of the keepers on every wall the cluster touches)`.
4. Winning symbols pop. **Mitten bats the box**: gravity rotates 90° clockwise.
   Everything slides toward the new floor; new symbols fall in from the opposite wall.
5. Back to step 2. The spin ends when a settle produces no cluster.
6. **Snowstorm:** every 4th quarter-turn (a full rotation of the box) doubles all four
   keepers (each keeper capped at x1000).

Coins stuck against a wall that isn't the floor wait there. They're banked only when a
later tilt makes that wall the floor, which is what builds the "one more tilt" tension
in the base game.

### Edge Keepers

Four tiny villagers stand on the box's walls, each holding a lantern with their value:

| Wall | Keeper | Floor when gravity points |
|---|---|---|
| South | Skater | down |
| West | Fisher | left |
| North | Lamplighter | up |
| East | Baker | right |

A keeper at x0 is unlit and adds nothing. Base game: keepers reset every spin. Free
spins: keepers never reset.

## 5. Features

Six features. Free Spins, Super Free Spins and Feature Spins can happen in normal play;
Mystery Free Spins and Max or Nothing are buy-only; Ante is a bet switch.

| # | Feature | In-game name | How you get it | Cost (target, set by math) |
|---|---|---|---|---|
| 1 | Ante — Double Chance | **Catnip** | toggle in the bet panel | 1.25× per spin |
| 2 | Free Spins | **Snow Day** | 4 / 5 Wind-up Keys, or buy | buy 100× |
| 3 | Super Free Spins | **Super Snow Day** | 6+ Wind-up Keys, or buy | buy 250× |
| 4 | Mystery Free Spins | **Mitten's Gift** | buy | buy 140× |
| 5 | Feature Spins | **Paw Spins** | bet mode, per spin | 5× per spin |
| 6 | Max or Nothing Spins | **Off the Shelf** | buy | buy 200× |

All modes: RTP 96.50% (within Stake's ±0.5% between modes), max win **10,000×**, the round
ends as soon as it is reached.

### 5.1 Ante — Double Chance (Catnip)

- Costs **1.25×** the bet. Mitten is on catnip: Wind-up Keys appear more often, so
  Snow Day triggers **twice as often**. Everything else about the spin is unchanged.
- While Catnip is on, every buy (Snow Day, Super, Gift, Off the Shelf) and Paw Spins are
  disabled, as Stake requires; switching it off re-enables them.
- Math: a separate reel set with more keys. Since a trigger needs 4 keys, about 2^¼ ≈ 1.2×
  more keys gives 2× the triggers (prototype: 1 in 242 → 1 in 133 spins).

### 5.2 Free Spins (Snow Day)

- **4 keys → 10 spins, 5 keys → 12 spins.** (6+ keys → Super Snow Day, below.)
- Keepers, gravity direction and the quarter-turn count **persist for the whole bonus**.
- **The Paw:** before each free spin drops, Mitten turns the box a quarter turn. So the
  floor wall changes every spin, all four keepers get coins, and a Snowstorm comes at
  least every 4 spins.
- **3+ keys** during the bonus → **+3 spins** (lifetime cap: 50 spins).
- Buy: **100×**, guarantees 4 or 5 keys.

### 5.3 Super Free Spins (Super Snow Day)

- **6+ keys → 12 spins**, or buy for **250×**.
- Same as Snow Day, plus **all four keepers start lit at x5**, so every edge cluster is
  multiplied from the first spin and every Snowstorm doubles something.
- Snowflake Coins land more often (heavier coin strip).
- Look: night falls in the toyshop, the box glows gold, Mitten's eyes shine.

### 5.4 Mystery Free Spins (Mitten's Gift)

- Buy for **140×**. Mitten knocks a wrapped present off the shelf; it unwraps to reveal the
  round before it starts. Starting weights (to tune):

  | Gift | Weight |
  |---|---|
  | Snow Day, 8 spins | 20 |
  | Snow Day, 10 spins | 25 |
  | Snow Day, 12 spins | 20 |
  | Snow Day, 15 spins | 15 |
  | Super Snow Day, 10 spins | 12 |
  | Super Snow Day, 12 spins | 8 |

- The price sits between Snow Day and Super: you pay less than Super, and 20% of gifts are
  Super rounds. The reveal is part of the book (`mysteryReveal` event), so it is replayable.

### 5.5 Feature Spins (Paw Spins)

- A bet mode at **5× per spin**, played as single spins (works with autoplay).
- Every Paw Spin starts with **all four keepers lit at x2** and is **guaranteed to win**
  (the mode's book set holds no zero-win spins), so every spin tilts at least once.
- Keys still trigger Snow Day / Super Snow Day as usual.
- Keepers reset each spin, as in the base game.
- Prototype: full turns happen 1 in ~520 Paw Spins vs 1 in ~3,000 base spins.

### 5.6 Max or Nothing Spins (Off the Shelf)

- Buy for **200×**. Mitten pushes the box to the edge of the shelf and plays a Super Snow Day.
- Spin wins are **not paid** in this mode: they put cracks in the glass instead, shown on a
  **crack meter** that fills toward 10,000×. No coin amounts or win counters are shown.
- If the round reaches **10,000×**, the box falls, shatters and pays the **max win**.
  Otherwise the box holds and the round pays **0**.
- So every round is either 10,000× or nothing. At 96.50% RTP and 200× cost, the max hits in
  **1 in ~52** rounds (p = 0.965 × 200 / 10,000).
- Math: the mode's books are two sets, max-win rounds (weight p) and zero rounds (real Super
  rounds that fall short of 10,000×). The optimizer only has to hit p.

## 6. Bet modes (math-sdk)

| Mode id | Cost | Feature | Notes |
|---|---|---|---|
| `base` | 1× | normal play | keys trigger Snow Day / Super |
| `ante` | 1.25× | Catnip | own reel set, 2× trigger rate |
| `bonus` | 100× | Snow Day buy | 4–5 keys guaranteed |
| `super` | 250× | Super Snow Day buy | |
| `mystery` | 140× | Mitten's Gift | gift drawn from weights in the book |
| `feature` | 5× | Paw Spins | no zero-win books |
| `max_or_nothing` | 200× | Off the Shelf | win is 0 or 10,000× |

Base hit rate target ~1 in 3.5, high volatility.

## 7. Prototype findings (placeholder weights — feel, not RTP)

`python prototype/tilt.py --mode <base|ante|feature|bonus|super|mystery> --sims N`:

| | Base | Catnip (ante) | Paw Spins |
|---|---|---|---|
| Hit rate | 1 in 5.3 | 1 in 5.4 | every spin |
| Tilts per spin | 0: 80%, 1: 18%, 2: 2%, 3+: 0.2% | same | 1: 88%, 2: 10%, 3+: 1.3% |
| Full turn (Snowstorm) | 1 in 3,000 | 1 in 3,000 | 1 in ~520 |
| Bonus trigger | 1 in 242 | 1 in 133 | — |

| | Snow Day (10) | Super Snow Day (12) | Mitten's Gift |
|---|---|---|---|
| Snowstorms per round | 2.75 | 3.38 | 2.94 |
| Biggest keeper: median / p90 / p99 | x16 / x60 / x216 | x44 / x120 / x432 | x18 / x84 / x400 |
| Walls lit at the end | 1.75 of 4 | 4 of 4 | 2.07 of 4 |

What this says:

- Without the Paw, free spins only averaged 0.2 Snowstorms per round — the bonus didn't
  feel like turning the box. Adding the Paw fixed it, so it's now part of the design.
- Super Snow Day's keepers end up about 3× bigger than Snow Day's, which fits a ~3× price.
- Base-game full turns are a true rare event. That's fine as a "hype moment", and Paw Spins
  are where players can chase them.
- Ante: 1.2× more keys gives 1.8× the triggers here; the final reel set will hit 2×.
- Hit rate (1 in 5 with flat weights) needs reel strips to reach ~1 in 3.5.
- Off the Shelf has no prototype: it's a choice of book weights, not new gameplay.

`python prototype/tilt.py --demo 158` shows a two-tilt spin: the first tilt slides an x10
coin onto the West wall, and the cluster after it touches that wall and pays ×10.

## 7b. Math results (math-sdk model, `math/whisker_tilt/`)

1.1M simulated rounds; all 7 modes pass the SDK's RGS format checks.

| Mode | Cost | RTP | Hit rate | Bonus | Max win 10,000× | Std dev / cost |
|---|---|---|---|---|---|---|
| Base | 1× | 96.50% | 1 in 2.9 | 1 in 240 | 1 in 2.4M | 14.7 |
| Catnip (ante) | 1.25× | 96.50% | 1 in 4.4 | 1 in 120 | 1 in 1.2M | 17.5 |
| Paw Spins | 5× | 96.50% | every spin | 1 in 189 | 1 in 790k | 3.8 |
| Snow Day buy | 100× | 96.50% | every buy | — | 1 in 100k | 1.5 |
| Super Snow Day buy | 250× | 96.50% | every buy | — | 1 in 10k | 1.3 |
| Mitten's Gift | 140× | 96.50% | every buy | — | 1 in 36k | 1.3 |
| Off the Shelf | 200× | 96.50% | 1 in 52 | — | 1 in 52 | 6.9 |

- Snow Day averages ~92× bet in the base game, Super ~250×, Mitten's Gift ~136× raw.
- Base, Catnip and Paw Spins keep the simulated win spread (`natural_weights.py`); the
  optimizer's curve fit had squeezed 1–5× base wins to 1 in 218 spins (now 1 in 6).
- The SDK flags Super and Off the Shelf against its *3-star volatility* limits. That's a
  rating warning, not an approval failure: both are high-volatility buys by design.
- Book files: ~1 GB compressed in total (buy modes ~200 MB each), so the release zips need
  splitting like Dumpster Duke's.

## 8. Implementation notes

### Math (StakeEngine math-sdk)

- Reuse the cluster + tumble flow. Gravity rotation is done by **rotating the board into
  the gravity frame, running the normal down-tumble, and rotating back**: a fixed 90° turn
  per tilt, so the reels, their stops and their strip positions stay the usual
  column-falls-down logic. The prototype's `to_frame` / `settle` / `from_frame` is
  the reference.
- Refill pulls from per-direction reel strips (or one set used in every frame; to decide
  while tuning).
- Track `gravity`, `turn`, `keepers[4]` in the game state; reset in base, carry in free spins.
- Distribution/optimizer: criteria for 0-win, base wins, Snowstorm wins, free-spin wins, max win.

### New book events

| Event | Payload |
|---|---|
| `tilt` | `{ gravity, turn, cause }`: gravity is down / left / up / right, cause is cascade / paw |
| `settle` | the new board after the slide + refill (positions are in screen coordinates) |
| `keeperBank` | `{ wall, coinValue, keeperTotal, position }` |
| `snowstorm` | `{ keepers: [s, w, n, e] }` after doubling |
| `clusterWin` | as in the cluster app, plus `walls` touched and `multiplier` |
| `mysteryReveal` | `{ kind, spins }`: kind is free / super |
| `crackMeter` | `{ progress }`: Off the Shelf only, replaces win counters |

### Client (web-sdk, from the cluster app)

- The box rotates visually, but the grid is drawn in screen coordinates: rotate the
  container 90° with ease-in-out (~350 ms, ~180 ms turbo), then counter-rotate the symbols
  so they stay upright, then slide along the new gravity.
- Each keeper is a small Pixi container on its wall; lantern flare + number count-up on bank.
- Snowstorm: whiteout flash, snow particles, all four lanterns pulse ×2.
- Turbo/skip must cut the rotation, not just the slide.

## 9. Risks and open questions

- **Readability on mobile:** a rotating board can disorient. Mitigation: rotate the frame
  and the snow only, symbols stay upright; a big arrow on the floor wall.
- **Multiplier stacking:** corner clusters add two keepers and a wall-to-wall cluster can touch
  three or four, up to x4000 per cluster after storms. The 10,000× cap makes this safe, but optimizer criteria must keep the max-win
  frequency within Stake's limits (more often than 1 in 10M).
- **Animation length:** each tilt adds ~0.5 s. Long base cascades are rare (2% reach 2 tilts),
  so it's OK, but the bonus with the Paw adds a turn per spin: keep the Paw quick.
- **Off the Shelf presentation:** showing progress that isn't paid can read as a lost win.
  Rules and UI must say clearly that only 10,000× pays; check with Stake before building.
- **Paw Spins price:** settled at 5× by simulation (an average Paw Spin pays ~4.4×).
- Should a cluster touching the floor wall get a small bonus (x2) even with unlit keepers,
  to make edges matter in the base game? Test after first math run.

## 10. Next steps

1. Sign off this concept (theme + mechanic).
2. Math: set up `math/whisker_tilt/` on the math-sdk with the rotate-tumble and the seven
   bet modes in section 6, simulate, tune reel strips and prices toward the targets.
3. Art prompt sheet in the Dumpster Duke style workflow (`docs/ART_PROMPTS.md`) for
   symbols, keepers, Mitten and the toyshop background.
4. Client: fork the cluster app, add the `tilt` / `keeperBank` / `snowstorm` /
   `mysteryReveal` / `crackMeter` events and the buy menu for the five buyable modes.
