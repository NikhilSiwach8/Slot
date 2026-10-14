# Dumpster Duke — Game Design Document

> Working title. Stake Engine slot, 6×5 pay-anywhere tumbling ("scatter pays").

## 1. Concept

Under the neon glow of a back-alley junkyard, **the Dumpster Duke** — a pompous raccoon
in a bottle-cap crown and a tin-foil cape — rules a kingdom of trash. His court of
alley critters guards the night's haul. Every tumble digs deeper into the pile; land
enough **Golden Trash Cans** and the Duke leads a **Midnight Raid**, stuffing bottle-cap
multipliers into his ever-growing **Loot Bag**.

Tone: comedic, mischievous, loud. Night-time palette (deep teal/purple sky, neon
pink and acid-green signage) contrasted with warm, gold-yellow treasure.

## 2. Art direction

Reference *feel*: chunky, cel-shaded cartoon slots (e.g. the Meta Gaming style of
*Swamp King*) — **original characters and assets only, nothing copied**.

- Thick dark outlines (≈6–8% of symbol width), rounded chunky silhouettes.
- 2–3 tone cel shading + one hard specular highlight per form.
- Saturated, high-contrast colours; each symbol owns a distinct hue so it reads
  at a glance on mobile.
- Characters are expressive and slightly over-the-top (big eyes, toothy grins).
- Symbols sit on no tile; they float over a dark reel window with a soft drop shadow.

## 3. Grid & pays

- 6 reels × 5 rows, pay anywhere: **8+ matching symbols anywhere** pay.
- Winning symbols explode, remaining symbols fall, new symbols drop in (tumble).
  Tumbling repeats until no new wins.
- Pay groups (count on board): 8–9, 10–11, 12–14, 15+.

| Symbol | Code | 8–9 | 10–11 | 12–14 | 15+ |
|---|---|---|---|---|---|
| The Dumpster Duke (raccoon king) | H1 | 10 | 25 | 50 | 100 |
| Possum Bruiser | H2 | 2.5 | 10 | 25 | 50 |
| Bling Pigeon | H3 | 2 | 5 | 15 | 40 |
| Golden Pizza Slice | H4 | 1.5 | 2 | 12 | 30 |
| Soda Can | L1 | 1 | 1.5 | 10 | 20 |
| Fish Bone | L2 | 0.8 | 1.2 | 8 | 16 |
| Banana Peel | L3 | 0.5 | 1 | 5 | 12 |
| Apple Core | L4 | 0.4 | 0.9 | 4 | 10 |

Payouts are multiples of the bet. (Values are the starting paytable; final
values are fixed once the math is signed off.)

## 4. Special symbols

- **Golden Trash Can (S, scatter)** — pays nothing itself, triggers the bonus.
- **Bottle Cap (M, multiplier)** — carries a value from 2× to 100×. Appears in
  base game and free spins. Stays on screen through tumbles.

## 5. Base game

- After all tumbles, if the spin won, the values of all Bottle Caps on screen are
  **added together** and the spin win is multiplied by that total.
- **4+ Golden Trash Cans** anywhere trigger the Midnight Raid:
  4 → 10 spins, 5 → 12 spins, 6+ → 15 spins.

## 6. Midnight Raid (free spins)

- Starts with an empty **Loot Bag** (×0).
- Whenever a free spin ends with a win, every Bottle Cap on screen is added to the
  Loot Bag, and that spin's win is multiplied by the **whole Loot Bag total**.
  The Loot Bag never resets during the raid.
- Spins that win with no caps showing are still multiplied by the Loot Bag (if > 0).
- **3+ Golden Trash Cans** during the raid award **+5 spins**.

## 7. Bet modes

| Mode | Cost | Description |
|---|---|---|
| `base` | 1× | Normal play |
| `bonus` | 100× | Buy the Midnight Raid (4–6 scatters guaranteed) |

## 8. Math targets

- RTP **96.50%** for every mode (Stake: 90–98%, modes within 0.5%).
- Max win **10,000×** bet (round ends immediately when reached).
- Base hit rate better than 1 in 4 (Stake minimum: 1 in 20).
- Bonus frequency ≈ 1 in 250–400 spins.
- 100k+ simulated outcomes per mode; max win must be reachable.

## 9. Animation & feedback plan

- Spin: symbols fall in column by column with a squash-and-stretch bounce.
- Win: winning symbols pulse (scale 1 → 1.15), glow, then pop in a burst of
  confetti-trash particles before the tumble.
- Bottle Cap: spins on land, value counts up into the Loot Bag with a fly-to trail.
- Scatter: wobble + lid-pop on land; anticipation shake on remaining reels at 3.
- Big win tiers (Big / Mega / Epic / Max) with coin shower and count-up.
- Midnight Raid intro: neon "RAID!" sign flickers on, alley lights switch to purple.

## 10. Compliance notes (Stake Engine)

- Stateless; no jackpots, gamble or cash-out.
- Spacebar = bet, sound mute, autoplay confirmation, mobile layout, static CDN-only
  frontend — handled by the web-sdk.
- Rules screen must state RTP, max win, bonus-buy cost, and all of the above.
