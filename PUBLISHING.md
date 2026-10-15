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
| max (Max or Nothing) | 500x | 96.50% | 10,000x | 1 in 20.7 |

Base game: hits 1 in 3.44, triggers the bonus 1 in 210, std dev 8.7.
Double Chance (ante): hits 1 in 4.32, triggers the bonus 1 in 105 (2x base), same average raid (~78x), std dev 9.0.
Feature Spin: every spin shows 3 Golden Trash Cans and a Bottle Cap; hits 1 in 5.37, raid 1 in 23 (avg ~99x bet).
Super Bonus: Loot Bag starts at x10, a Bottle Cap on every free spin. Mystery Bonus: 5-25 spins and a x0-x20
starting Loot Bag drawn at random (a `mysteryReveal` book event carries both before `freeSpinTrigger`).
Max or Nothing: only two outcomes, 0 or the 10,000x cap; weights are set exactly by
`math/dumpster_duke/fixed_weights.py` (P(cap) = RTP x cost / cap = 1 in 20.7). The SDK's own
format-check statistics step cannot handle a two-outcome table (it crashes computing the gap between
payouts); `validate-books-index` passes for all 7 modes. Mention this mode explicitly to reviewers.

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
| base | normal win | 15 | 1x |
| base | big win | 980 | 25x |
| base | loss | 1 | 0x |
| base | bonus trigger | 0 | 51.6x |
| base | big bonus | 5 | 130x |
| base | win cap | 629 | 10,000x |
| ante | normal win | 0 | 1.7x |
| ante | big win | 1028 | 28.5x |
| ante | loss | 1 | 0x |
| ante | bonus trigger | 4 | 13x |
| ante | big bonus | 58 | 144.2x |
| ante | win cap | 701 | 10,000x |
| feature | loss | 0 | 0x |
| feature | normal win | 21 | 1.6x |
| feature | big win | 53 | 18x |
| feature | bonus trigger | 4 | 14x |
| feature | big bonus | 58 | 217.8x |
| feature | win cap | 701 | 10,000x |
| bonus | bonus (every buy triggers) | 0 | 51.6x |
| bonus | big bonus | 1 | 633.6x |
| bonus | win cap | 1875 | 10,000x |
| super | bonus (every buy) | 0 | 98x |
| super | win cap | 1875 | 10,000x |
| mystery | bonus (every buy) | 0 | 10.9x |
| mystery | big bonus | 2 | 138.8x |
| mystery | win cap | 1875 | 10,000x |
| max | loss | 0 | 0x |
| max | win cap | 124 | 10,000x |

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
4. **Review the audio.** Sound effects and the bonus music are synthesized by `sound/make_sounds.py`. The base-game music is "Silly Intro" by Alexander Nakarada (`sound/source/bgm_main_silly_intro.mp3`, credited as CC BY 4.0 in the rules screen's Credits section); confirm that licence on the track's download page before release. It plays at 45% while idle and 100% while a round plays (`components/Sound.svelte`).
5. **Submit for review**, pasting the replay table above into the notes.
