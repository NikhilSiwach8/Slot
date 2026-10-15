# Dumpster Duke

A Stake Engine slot: 6×5 pay-anywhere tumbling game with bottle-cap multipliers
and the "Midnight Raid" free spins. Design: [docs/GDD.md](docs/GDD.md).

| Folder | What |
|---|---|
| `math/dumpster_duke/` | Math model for StakeEngine/math-sdk (config, reels, game logic) |
| `web-sdk/apps/dumpster-duke/` | Game client (Svelte + PixiJS, forked from the web-sdk scatter app) |
| `art/` | Art prompts, ChatGPT/OpenAI generation + finishing pass, sprite-sheet builder |
| `docs/` | Game design doc, ChatGPT art prompt sheet |
| `concepts/` | New game concepts: [Whisker Tilt](concepts/whisker-tilt/CONCEPT.md) (rotating-gravity cluster tumble) |
| `math/whisker_tilt/` | Whisker Tilt math model (7 bet modes) — see its [README](math/whisker_tilt/README.md) |
| `scripts/` | SDK setup and math → client sync tools |

## Setup

```bash
scripts/setup.sh            # restores math-sdk + web-sdk around our folders
```

## Math

```bash
cd math-sdk && env/bin/python games/dumpster_duke/run.py   # sims + optimizer + checks (~45 min)
python math/dumpster_duke/analyze.py                         # RTP, hit rate, max win, distribution
python scripts/sync_fe_config.py                             # push paytable/reels into the client
math-sdk/env/bin/python scripts/make_story_books.py          # demo rounds for Storybook
```

## Client

```bash
cd web-sdk/apps/dumpster-duke
pnpm storybook       # http://localhost:6001 → MODE_BASE/book → random, press Action
pnpm build           # static build in ./build
```

## Art

Symbol art comes from the ChatGPT sheet in `art/source/symbols_sheet.webp`
(prompts in `docs/ART_PROMPTS.md`):

```bash
python art/slice_sheet.py art/source/symbols_sheet.webp   # cut tiles, remove background → art/raw/
python art/blank_cap.py                                   # clear the cap centre for the value
python art/generate.py --process                          # finishing pass → art/final/
python art/build_atlas.py                                 # pack into the client sprite sheet
python art/make_backgrounds.py art/source/backgrounds_sheet.webp   # backgrounds + free-spins splash
python art/make_font.py art/source/ui_sheet.webp          # "gold" bitmap font from the sheet's letters
python art/slice_ui.py art/source/ui_sheet.webp           # bottom-bar buttons, bonus panel and card
```

Reel spin: logic in `src/game/reelSpin/` (deterministic — the reels always land on
the server's board), rendering in `src/components/ReelSpinner.svelte`. All feel
values (speed, durations, stagger, overshoot, bounce, blur, stretch, shake) are in
`src/game/reelSpin/config.ts`, with turbo overrides.

The bottom bar is our own copy of the web-sdk UI package in
`web-sdk/apps/dumpster-duke/src/ui/` (restyled with the art above).
