"""Sample Whisker Tilt rounds from the published books (by lookup-table weight) for the offline demo.

Usage: python scripts/make_demo_books_whisker_tilt.py [publish_dir] [out.js] [extra ids as mode:id ...]
Extra ids are always included (so ?demoBook=mode:id can force them while testing).
"""
import io
import json
import random
import sys

import zstandard

MATH = sys.argv[1] if len(sys.argv) > 1 else "math/whisker_tilt/library/publish_files"
OUT = sys.argv[2] if len(sys.argv) > 2 else "dist/whisker-tilt-demo/demo_books.js"
EXTRA = sys.argv[3:]
DRAWS = {"base": 1500, "ante": 600, "feature": 400, "bonus": 120, "super": 60, "mystery": 80, "max_or_nothing": 80}
COSTS = {"base": 1, "ante": 1.25, "feature": 5, "bonus": 100, "super": 250, "mystery": 140, "max_or_nothing": 200}
random.seed(7)


def lut(mode):
    ids, w = [], []
    for line in open(f"{MATH}/lookUpTable_{mode}_0.csv"):
        i, weight, _ = line.strip().split(",")
        ids.append(int(i))
        w.append(int(weight))
    return ids, w


out = {}
for mode, n in DRAWS.items():
    ids, w = lut(mode)
    picks = random.choices(ids, weights=w, k=n)
    want = set(picks) | {int(e.split(":")[1]) for e in EXTRA if e.startswith(f"{mode}:")}
    books = {}
    with open(f"{MATH}/books_{mode}.jsonl.zst", "rb") as f:
        for line in io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(f)):
            b = json.loads(line)
            if b["id"] in want:
                books[b["id"]] = {"p": b["payoutMultiplier"], "e": b["events"]}
            if len(books) == len(want):
                break
    out[mode] = {"picks": picks, "books": books}
    print(mode, len(books), "books", file=sys.stderr)

with open(OUT, "w") as f:
    f.write("window.__DEMO_COSTS__=" + json.dumps(COSTS) + ";\n")
    f.write("window.__DEMO_BOOKS__=" + json.dumps(out, separators=(",", ":")) + ";\n")
