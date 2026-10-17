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
| base | 1x | 96.50% | 50,000x | 1 in 8.0M |
| ante (Double Chance) | 1.25x | 96.50% | 50,000x | 1 in 6.4M |
| feature (Feature Spin) | 5x | 96.50% | 50,000x | 1 in 1.0M |
| bonus (buy Haunted Raid) | 100x | 96.50% | 50,000x | 1 in 100k |
| super (Super Bonus) | 250x | 96.50% | 50,000x | 1 in 20k |
| mystery (Mystery Bonus) | 100x | 96.50% | 50,000x | 1 in 100k |
| max (Max or Nothing) | 200x | 96.50% | 4,000x (mode prize) | 1 in 20.7 |

Win style: cluster pays (5+ touching, orthogonal) with Haunted Spots (a spot a win explodes from is
haunted; each further win there makes it x2, x4, ... x1024; cleared each base spin, kept through the raid;
`hauntedSpots` book event). Reels: math/dumpster_duke/make_reels.py (runs of 1-3).
Base game: hits 1 in 3.44, triggers the bonus 1 in 210, std dev 24.7.
Double Chance (ante): hits 1 in 4.32, triggers the bonus 1 in 105 (2x base), std dev 24.7.
Feature Spin: every spin shows 3 Golden Trash Cans and a Bottle Cap; hits 1 in 5.37.
Super Bonus: Loot Bag starts at x10, a Bottle Cap on every free spin. Mystery Bonus: 5-25 spins and a x0-x20
starting Loot Bag drawn at random (a `mysteryReveal` book event carries both before `freeSpinTrigger`).
Max or Nothing: a single base-game spin (no free spins; boards with 4+ Cursed Trash Cans are
redrawn). Every board carries a MAX Candy Cap (multiplier value 25,000, shown as MAX). A winning
spin tumbles, then the MAX cap applies through the normal `boardMultiplierInfo` event and the win
is set to the mode's prize of 4,000x (a `maxBoost` event drives the celebration); a losing spin pays
0. Only two outcomes, 0 or 4,000x; weights are set exactly by `math/dumpster_duke/fixed_weights.py`
(P(prize) = RTP x cost / prize = 1 in 20.7). The prize is kept under 5,000x so the mode passes the
risk checks. Worst values over all modes at the 50,000x max win: P(>= 5,000x) 0.00033,
P(>= 10,000x) 0.00015, P(>= 25,000x) 0.000066, P(>= 50,000x) 0.000052, ETL(10,000x) 0.036,
ETL(40x, per cost) 0.709 (Feature Spin), CVaR (top 0.1%) 238 per stake / 8,183 absolute (Super Bonus).
The SDK's own format-check statistics step cannot handle a two-outcome table (it crashes computing the
gap between payouts); `validate-books-index` passes for all 7 modes. Mention this mode explicitly to reviewers.

## 3. What was done to meet the approval checklist

- **Original assets only.** All web-sdk sample images, spines, sounds and the sample loader were removed. The only template file left is `stake-engine-loader.gif`, which is platform branding.
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
| base | win cap | 629 | 50,000x |
| ante | normal win | 38 | 1x |
| ante | big win | 495 | 18.5x |
| ante | loss | 0 | 0x |
| ante | bonus trigger / big bonus | 4 | 241.4x |
| ante | win cap | 701 | 50,000x |
| feature | loss | 1 | 0x |
| feature | normal win | 37 | 4x |
| feature | big win | 580 | 28x |
| feature | bonus trigger | 4 | 10.6x |
| feature | big bonus | 45 | 68.7x |
| feature | win cap | 701 | 50,000x |
| bonus | bonus (every buy triggers) | 0 | 48x |
| bonus | big bonus | 1 | 130.5x |
| bonus | win cap | 1875 | 50,000x |
| super | bonus (every buy) | 0 | 125.4x |
| super | win cap | 287 | 50,000x |
| mystery | bonus (every buy) | 0 | 1,358.7x |
| mystery | win cap | 1875 | 50,000x |
| max | loss | 0 | 0x |
| max | prize (4,000x) | 124 | 4,000x |

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
