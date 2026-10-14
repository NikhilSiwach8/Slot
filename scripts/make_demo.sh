#!/usr/bin/env bash
# Builds dist/demo: the release frontend plus an in-page demo RGS, playable offline with play money.
# Run scripts/package_release.sh first.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf dist/demo && mkdir -p dist/demo
cp -r dist/frontend/. dist/demo/
MATH_SDK=math-sdk math-sdk/env/bin/python scripts/make_demo_books.py dist/math dist/demo/demo_books.js
cp scripts/demo_rgs.js dist/demo/demo_rgs.js
python3 - <<'PY'
p = "dist/demo/index.html"
s = open(p).read()
tag = '<script src="./demo_books.js"></script><script src="./demo_rgs.js"></script>'
s = s.replace("<head>", "<head>\n\t\t" + tag, 1)
open(p, "w").write(s)
PY
du -sh dist/demo
