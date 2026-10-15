#!/usr/bin/env bash
# Builds dist/whisker-tilt-demo: the Whisker Tilt client plus the in-page demo RGS, playable
# offline with play money. Needs the math run (math/whisker_tilt/library) and a client build.
#   scripts/make_demo_whisker_tilt.sh [mode:id ...]   # extra books to include for ?demoBook=
# Open: dist/whisker-tilt-demo/index.html?sessionID=demo&rgs_url=demo.local&lang=en&device=desktop
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=dist/whisker-tilt-demo
rm -rf "$OUT" && mkdir -p "$OUT"
cp -r web-sdk/apps/whisker-tilt/build/. "$OUT/"
MATH_SDK=math-sdk math-sdk/env/bin/python scripts/make_demo_books_whisker_tilt.py \
  math/whisker_tilt/library/publish_files "$OUT/demo_books.js" "$@"
cp scripts/demo_rgs.js "$OUT/demo_rgs.js"
python3 - "$OUT/index.html" <<'PY'
import sys
p = sys.argv[1]
s = open(p).read()
tag = '<script src="./demo_books.js"></script><script src="./demo_rgs.js"></script>'
s = s.replace("<head>", "<head>\n\t\t" + tag, 1)
open(p, "w").write(s)
PY
du -sh "$OUT"
