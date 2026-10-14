#!/usr/bin/env bash
# Restore the Stake Engine SDKs around this repo's game folders.
#
#   math/dumpster_duke          -> linked into math-sdk/games/dumpster_duke
#   web-sdk/apps/dumpster-duke  -> the rest of web-sdk is filled in around it
#
# Usage: scripts/setup.sh        (idempotent; needs git, python3.12+, make, node 22, pnpm 10)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MATH_SDK_COMMIT=a6dccd86de740cc5d318079483cb6204cc5c19bc
WEB_SDK_COMMIT=1843d60cedb94b390e641b563f32ad64353bec5e

fetch() { # repo commit dest
  local tmp; tmp="$(mktemp -d)"
  git -C "$tmp" init -q
  git -C "$tmp" remote add origin "$1"
  git -C "$tmp" fetch -q --depth 1 origin "$2" || git -C "$tmp" fetch -q --depth 1 origin HEAD
  git -C "$tmp" checkout -q FETCH_HEAD
  rm -rf "$tmp/.git"
  echo "$tmp"
}

# --- math-sdk -------------------------------------------------------------
if [ ! -f "$ROOT/math-sdk/Makefile" ]; then
  src="$(fetch https://github.com/StakeEngine/math-sdk.git "$MATH_SDK_COMMIT")"
  rm -rf "$ROOT/math-sdk" && mv "$src" "$ROOT/math-sdk"
fi
ln -sfn "$ROOT/math/dumpster_duke" "$ROOT/math-sdk/games/dumpster_duke"
[ -x "$ROOT/math-sdk/env/bin/python" ] || make -C "$ROOT/math-sdk" setup

# --- web-sdk --------------------------------------------------------------
if [ ! -f "$ROOT/web-sdk/package.json" ]; then
  src="$(fetch https://github.com/StakeEngine/web-sdk.git "$WEB_SDK_COMMIT")"
  # copy upstream around our app without touching it
  (cd "$src" && tar cf - --exclude=./apps/dumpster-duke .) | (cd "$ROOT/web-sdk" && tar xf -)
  # Template art (backgrounds, frames, fonts, sounds) that hasn't been replaced yet;
  # never overwrite files we track ourselves.
  (cd "$src/apps/scatter/static" && tar cf - .) | (cd "$ROOT/web-sdk/apps/dumpster-duke/static" && tar xf - --skip-old-files)
  rm -rf "$src"
fi
(cd "$ROOT/web-sdk" && pnpm install)

echo "Ready. Math:     cd math-sdk && env/bin/python games/dumpster_duke/run.py"
echo "       Frontend: cd web-sdk && pnpm turbo run dev --filter=dumpster-duke"
