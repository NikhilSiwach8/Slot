"""Sample rounds from the published books (by their lookup-table weights) for the offline demo."""
import io, json, random, sys
import zstandard

MATH = sys.argv[1] if len(sys.argv) > 1 else "dist/math"
OUT = sys.argv[2] if len(sys.argv) > 2 else "dist/demo/demo_books.js"
DRAWS = {"base": 1500, "bonus": 250}
random.seed(7)

def lut(mode):
    ids, w = [], []
    for line in open(f"{MATH}/lookUpTable_{mode}_0.csv"):
        i, weight, _ = line.strip().split(",")
        ids.append(int(i)); w.append(int(weight))
    return ids, w

out = {}
for mode, n in DRAWS.items():
    ids, w = lut(mode)
    picks = random.choices(ids, weights=w, k=n)
    want = set(picks)
    books = {}
    with open(f"{MATH}/books_{mode}.jsonl.zst", "rb") as f:
        for line in io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(f)):
            b = json.loads(line)
            if b["id"] in want:
                books[b["id"]] = {"p": b["payoutMultiplier"], "e": b["events"]}
    out[mode] = {"picks": picks, "books": books}
    print(mode, len(books), "unique of", n, file=sys.stderr)

with open(OUT, "w") as f:
    f.write("window.__DEMO_BOOKS__=" + json.dumps(out, separators=(",", ":")) + ";\n")
