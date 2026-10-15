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

## 5. Bonus: Snow Day (free spins)

- **4 / 5 / 6+ Wind-up Keys** → **10 / 12 / 15** free spins.
- Keepers, gravity direction and the quarter-turn count **persist for the whole bonus**.
- **The Paw:** before each free spin drops, Mitten turns the box a quarter turn. So the
  floor wall changes every spin, all four keepers get coins, and a Snowstorm comes at
  least every 4 spins.
- **3+ Keys** during the bonus → **+3 spins** (lifetime cap: 50 spins).

## 6. Bet modes (Stake)

| Mode | Cost | What |
|---|---|---|
| `base` | 1× | normal play |
| `ante` (Cat Nip) | 1.25× | bonus twice as often, same as Dumpster Duke's Double Chance |
| `bonus` | 100× | buy Snow Day (4–6 keys guaranteed) |
| `super` (optional) | 300× | buy Snow Day with every keeper already lit at x2 |

Targets: RTP 96.50% all modes, max win **10,000×** (round ends on reaching it),
high volatility, base hit rate ~1 in 3.5.

## 7. Prototype findings (placeholder weights — feel, not RTP)

`python prototype/tilt.py --sims 20000` and `--bonus --sims 5000`:

| | Base | Snow Day (10 spins) |
|---|---|---|
| Tilts per spin | 0: 80%, 1: 18%, 2: 2%, 3+: 0.2% | — |
| Snowstorm | ~1 in 2,500 spins | avg 2.75 per round, every round has one |
| Biggest keeper at the end | — | median x16, p90 x60, p99 x216 |

What this says:

- Without the Paw, free spins only averaged 0.2 Snowstorms per round — the bonus didn't
  feel like turning the box. Adding the Paw fixed it, so it's now part of the design.
- Base-game full turns are a true rare event. That's fine as a "hype moment", but if it
  should be part of base play, add Wilds or lower the cluster size to 4 so cascades run
  longer.
- Hit rate (1 in 5 with flat weights) needs reel strips to reach ~1 in 3.5.

`python prototype/tilt.py --demo 197` shows a two-tilt spin where a coin waiting on the
north wall gets banked once the box turns upside down.

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
- Should a cluster touching the floor wall get a small bonus (x2) even with unlit keepers,
  to make edges matter in the base game? Test after first math run.

## 10. Next steps

1. Sign off this concept (theme + mechanic).
2. Math: set up `math/whisker_tilt/` on the math-sdk with the rotate-tumble, simulate, tune
   reel strips toward the targets above.
3. Art prompt sheet in the Dumpster Duke style workflow (`docs/ART_PROMPTS.md`) for
   symbols, keepers, Mitten and the toyshop background.
4. Client: fork the cluster app, add the `tilt` / `keeperBank` / `snowstorm` events.
