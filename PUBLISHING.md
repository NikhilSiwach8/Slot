# Publishing Dumpster Duke on Stake Engine

## 1. Build the upload folders

```bash
scripts/setup.sh                      # once per machine: pinned math-sdk + web-sdk
cd math-sdk && env/bin/python games/dumpster_duke/run.py && cd ..   # only if the math changed
scripts/package_release.sh            # -> dist/math, dist/frontend
```

| Folder | Contents | Upload to |
|---|---|---|
| `dist/math` | `index.json`, `books_base.jsonl.zst`, `books_bonus.jsonl.zst`, `lookUpTable_base_0.csv`, `lookUpTable_bonus_0.csv` | Stake Engine dashboard → Math |
| `dist/frontend` | Static SvelteKit build (`index.html`, `_app/`, `assets/`) | Stake Engine dashboard → Front End |

The math folder was checked with `validate-books-index.mjs` and passed.

## 2. Math summary

| Mode | Cost | RTP | Max win | Max win frequency |
|---|---|---|---|---|
| base | 1x | 96.50% | 10,000x | 1 in 5.0M |
| bonus (buy Midnight Raid) | 100x | 96.50% | 10,000x | 1 in 100k |

Base game: hits 1 in 3.44, triggers the bonus 1 in 210, std dev 8.7.

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
| bonus | bonus (every buy triggers) | 0 | 51.6x |
| bonus | big bonus | 1 | 633.6x |
| bonus | win cap | 1875 | 10,000x |

Every bonus buy triggers free spins and always pays, so the bonus mode has no loss or normal-win case. To regenerate the table after a math rerun, run `scripts/find_replay_examples.py`.

## 5. Manual steps (need your account)

1. **Provider name.** Replace `sample_provider` in `web-sdk/apps/dumpster-duke/src/game/config.ts` with your provider slug. Then rerun `scripts/package_release.sh`.
2. **Dashboard art.** Upload the following in the Tile Editor:
   - the game tile: bright background plus foreground character, no text;
   - your provider logo.
3. **Test on the real RGS.**
   - Play both modes from the dashboard preview.
   - Open a replay link with `?replay=true` for each event id above.
   - Try `?social=true`.
4. **Review the audio.** Sounds are synthesized by `sound/make_sounds.py`. Listen to them and replace any you don't like by dropping in new files and rebuilding the sprite.
5. **Submit for review**, pasting the replay table above into the notes.
