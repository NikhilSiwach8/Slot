#!/usr/bin/env bash
# Build everything Stake Engine needs into dist/:
#   dist/math/      index.json + books_*.jsonl.zst + lookUpTable_*_0.csv   (upload as the math files)
#   dist/frontend/  static build of the game client                         (upload as the frontend)
# Run scripts/setup.sh once first, and the math run (see README) if library/ is missing.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PUBLISH="$ROOT/math/dumpster_duke/library/publish_files"
DIST="$ROOT/dist"

for f in index.json books_base.jsonl.zst books_bonus.jsonl.zst lookUpTable_base_0.csv lookUpTable_bonus_0.csv; do
  [ -f "$PUBLISH/$f" ] || { echo "missing math output: $PUBLISH/$f (run the math first)" >&2; exit 1; }
done

rm -rf "$DIST" && mkdir -p "$DIST/math"
cp "$PUBLISH"/index.json "$PUBLISH"/books_*.jsonl.zst "$PUBLISH"/lookUpTable_*_0.csv "$DIST/math/"

# keep the client in sync with the math before building
(cd "$ROOT" && math-sdk/env/bin/python scripts/sync_fe_config.py)
# `vite build` writes the site but then never exits (a lingering esbuild service
# handle, also seen with the untouched web-sdk template), so wait for SvelteKit's
# "done" line and stop it ourselves.
LOG="$(mktemp)"
(cd "$ROOT/web-sdk/apps/dumpster-duke" && exec pnpm build >"$LOG" 2>&1) &
BUILD_PID=$!
until grep -q "Wrote site" "$LOG" && grep -q "done" "$LOG"; do
  if ! kill -0 "$BUILD_PID" 2>/dev/null; then cat "$LOG"; echo "build failed" >&2; exit 1; fi
  if grep -qE "error during build|ELIFECYCLE" "$LOG"; then cat "$LOG"; echo "build failed" >&2; exit 1; fi
  sleep 2
done
pkill -P "$BUILD_PID" 2>/dev/null || true
kill "$BUILD_PID" 2>/dev/null || true
cp -r "$ROOT/web-sdk/apps/dumpster-duke/build" "$DIST/frontend"

# the build must not reference sample assets or load anything from other origins
if grep -rqE "typekit\.net/[a-z0-9]+\.(css|js)\"" "$DIST/frontend/index.html"; then
  echo "external font link found in index.html" >&2; exit 1
fi

echo
echo "dist/math:"; ls -la "$DIST/math"
echo "dist/frontend: $(du -sh "$DIST/frontend" | cut -f1)"
