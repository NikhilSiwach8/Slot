# Publishing Dumpster Duke on Stake Engine

## 1. Build the upload folders

```bash
scripts/setup.sh                      # once per machine: pinned math-sdk + web-sdk
cd math-sdk && env/bin/python games/dumpster_duke/run.py && cd ..   # only if the math changed
scripts/package_release.sh            # -> dist/math, dist/frontend
```

| Folder | Contents | Upload to |
|---|---|---|
| `dist/math` | `index.json`, `books_<mode>.jsonl.zst` and `lookUpTable_<mode>_0.csv` for all 7 modes (base, ante, feature, bonus, super, mystery, max) | Stake Engine dashboard → Math |
| `dist/frontend` | Static SvelteKit build (`index.html`, `_app/`, `assets/`) | Stake Engine dashboard → Front End |

The math folder was checked with `validate-books-index.mjs` and passed.

Ready-made copies live in `release/`: `dumpster_duke_frontend.zip`, and the math split into
`dumpster_duke_math_<n>of<N>.zip` parts because GitHub refuses files over 100 MB. Unzip every math
part into one folder to get all 15 math files (index + 7 books + 7 lookup tables).

## 2. Math summary

| Mode | Cost | RTP | Max win | Max win frequency |
|---|---|---|---|---|
| base | 1x | 96.50% | 10,000x | 1 in 5.0M |
| ante (Double Chance) | 1.25x | 96.50% | 10,000x | 1 in 4.0M |
| feature (Feature Spin) | 5x | 96.50% | 10,000x | 1 in 1.0M |
| bonus (buy Midnight Raid) | 100x | 96.50% | 10,000x | 1 in 100k |
| super (Super Bonus) | 250x | 96.50% | 10,000x | 1 in 20k |
| mystery (Mystery Bonus) | 100x | 96.50% | 10,000x | 1 in 100k |
| max (Max or Nothing) | 200x | 96.50% | 10,000x | 1 in 250 (4,000x MAX BOOST 1 in 26.1) |

Win style: cluster pays (5+ touching, orthogonal) with Haunted Spots (a spot a win explodes from is
haunted; each further win there makes it x2, x4, ... x128; cleared each base spin, kept through the raid;
`hauntedSpots` book event). Reels: math/dumpster_duke/make_reels.py (runs of 1-3).
Base game: hits 1 in 3.44, triggers the bonus 1 in 210, std dev 10.8.
Double Chance (ante): hits 1 in 4.32, triggers the bonus 1 in 105 (2x base), std dev 12.1.
Feature Spin: every spin shows 3 Golden Trash Cans and a Bottle Cap; hits 1 in 5.37.
Super Bonus: Loot Bag starts at x10, a Bottle Cap on every free spin. Mystery Bonus: 5-25 spins and a x0-x20
starting Loot Bag drawn at random (a `mysteryReveal` book event carries both before `freeSpinTrigger`).
Max or Nothing: a single base-game spin (no free spins; boards with 4+ Cursed Trash Cans are
redrawn). Every board carries a MAX Candy Cap (multiplier value 25,000, shown as MAX). A winning
spin tumbles, then the MAX cap applies through the normal `boardMultiplierInfo` event and the win
is set to that round's prize (a `maxBoost` event drives the celebration; `maxWin: true` for the
full max win); a losing spin pays 0. Three outcomes: 10,000x (MAX WIN, 20% of the RTP, 1 in 250),
4,000x (MAX BOOST, 76.5% of the RTP, 1 in 26.1) or 0. Weights are set exactly by
`math/dumpster_duke/fixed_weights.py` (P(prize) = RTP share x cost / prize). A single 0-or-10,000x
outcome would put the whole RTP in 10,000x wins (tail liability 0.965 > 0.6), so the split keeps the
mode inside the risk checks: P(win >= 5,000x) = P(win >= 10,000x) = 0.004 (limits 0.01 / 0.005),
expected tail liability (10,000x) 0.2 (limit 0.6) and (40x, per cost) 0.2 (limit 0.8). Every other mode
has P(win >= 5,000x) <= 0.0002, expected tail liability (10,000x) <= 0.002 and (40x) <= 0.557
(Double Chance). The SDK's own 3-star warning prints these tail liabilities without dividing by the
cost, so it overstates them for the buy modes; `validate-books-index` passes for all 7 modes. Mention this mode explicitly to reviewers.

## 3. What was done to meet the approval checklist

- **Original assets only.** All web-sdk sample images, spines, sounds and the sample loader were removed. The only template file left is Stake Engine's intro loader (platform branding), shipped as `stake-engine-loader.webp`: the template GIF re-encoded at 800x800 (same frames and timing, 395 KB instead of 1.3 MB) by `scripts/make_loader_webp.py` so the intro shows at once.
- **No external requests.**
  - The Typekit font is replaced by the bundled Lilita One (`src/fonts.css` and the `webfontloader` shim).
  - The production build only calls the RGS.
- **Social mode** (`social=true`): restricted words are replaced by `src/game/social.ts`. This covers the UI labels, rules and buy menu.
- **Required screens:** rules, paytable, bet-mode info and disclaimer are in the info modal. They are built from the math config.
- **Replay** (`replay=true`) uses the SDK's replay flow and has been tested with the story books.
- **Viewports:** all seven Stake sizes render (1200×675, 1024×576, 800×450, 400×225, 425×812, 375×667, 320×568).
- **Console:** clean.

## 4. Replay event IDs for reviewers

| Mode | Case | Event id | Payout |
|---|---|---|---|
| base | normal win | 1 | 1.9x |
| base | big win | 436 | 15x |
| base | loss | 2 | 0x |
| base | bonus trigger | 0 | 48x |
| base | big bonus | 4 | 241.4x |
| base | win cap | 271 | 10,000x |
| ante | normal win | 38 | 1x |
| ante | big win | 495 | 18.5x |
| ante | loss | 0 | 0x |
| ante | bonus trigger / big bonus | 4 | 241.4x |
| ante | win cap | 701 | 10,000x |
| feature | loss | 1 | 0x |
| feature | normal win | 37 | 4x |
| feature | big win | 580 | 28x |
| feature | bonus trigger | 4 | 10.6x |
| feature | big bonus | 45 | 68.7x |
| feature | win cap | 701 | 10,000x |
| bonus | bonus (every buy triggers) | 0 | 48x |
| bonus | big bonus | 1 | 130.5x |
| bonus | win cap | 271 | 10,000x |
| super | bonus (every buy) | 0 | 125.4x |
| super | win cap | 158 | 10,000x |
| mystery | bonus (every buy) | 0 | 1,358.7x |
| mystery | win cap | 93 | 10,000x |
| max | loss | 0 | 0x |
| max | MAX BOOST | 11 | 4,000x |
| max | MAX WIN (win cap) | 124 | 10,000x |

Every bonus buy triggers free spins and always pays, so the bonus mode has no loss or normal-win case. To regenerate the table after a math rerun, run `scripts/find_replay_examples.py`.

## 5. Manual steps (need your account)

1. **Provider name** is `nyxhilx` (set in `math/dumpster_duke/game_config.py`; `sync_fe_config.py` copies it to the client).
2. **Dashboard art** (made by `python art/make_tile.py nyxhilx`, files in `art/tile/`):
   - Tile Editor → Background: `tile_background.png`; Foreground element: `tile_foreground.png`; title text "Dumpster Duke" is typed in the editor.
   - Team Settings → Branding: `provider_logo.png`.
   - `tile_preview.png` is only a mock of the finished tile; `tile_logo.png` is the full logo for marketing.
3. **Test on the real RGS.**
   - Play both modes from the dashboard preview.
   - Open a replay link with `?replay=true` for each event id above.
   - Try `?social=true`.
4. **Review the audio.** Most sound effects and the bonus music are synthesized by `sound/make_sounds.py`; the bonus-start, tumble-collect and spin-win sounds are your recordings in `sound/source/` (sfx_bonus_start, sfx_tumble_collect, sfx_win). The base-game music is "Silly Intro" by Alexander Nakarada (`sound/source/bgm_main_silly_intro.mp3`, credited as CC BY 4.0 in the rules screen's Credits section); confirm that licence on the track's download page before release. It plays at 45% while idle and 100% while a round plays (`components/Sound.svelte`).
5. **Submit for review**, pasting the replay table above into the notes.
