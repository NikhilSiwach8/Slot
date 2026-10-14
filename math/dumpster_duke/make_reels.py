"""Generate reel strips for Dumpster Duke.

Usage: python make_reels.py   (writes reels/BR0.csv, FR0.csv, WCAP.csv)

Strips are built from runs of 1-3 identical paying symbols to create the
clumping pay-anywhere games need. Scatters (S) are kept at least ROWS+1 apart
so a reel can never show two scatters at once; multipliers (M) are single.
"""

import csv
import os
import random

NUM_REELS = 6
ROWS = 5
STRIP_LEN = 300
RUN_LENGTHS = {1: 80, 2: 18, 3: 2}

REELSETS = {
    # name: (seed, symbol weights, scatters per reel)
    "BR0": (101, {"H1": 5, "H2": 7, "H3": 8, "H4": 9, "L1": 11, "L2": 12, "L3": 13, "L4": 14, "M": 0.35}, 3),
    "FR0": (202, {"H1": 6, "H2": 7, "H3": 8, "H4": 9, "L1": 11, "L2": 12, "L3": 13, "L4": 14, "M": 2.0}, 2),
    "WCAP": (303, {"H1": 16, "H2": 10, "H3": 8, "H4": 7, "L1": 6, "L2": 5, "L3": 4, "L4": 4, "M": 5.0}, 2),
}
SINGLES = {"S", "M"}


def weighted(rng, table):
    keys = list(table)
    return rng.choices(keys, [table[k] for k in keys])[0]


def build_strip(rng, weights, n_scatter):
    strip = []
    while len(strip) < STRIP_LEN:
        sym = weighted(rng, weights)
        if sym in SINGLES:
            if strip and strip[-1] in SINGLES:
                continue
            strip.append(sym)
        else:
            if strip and strip[-1] == sym:
                continue
            strip.extend([sym] * weighted(rng, RUN_LENGTHS))
    strip = strip[:STRIP_LEN]
    # Scatters: evenly spaced (with jitter) so a window never shows two, and they
    # never replace a multiplier.
    gap = STRIP_LEN // n_scatter
    for k in range(n_scatter):
        pos = k * gap + rng.randrange(ROWS, gap - ROWS)
        while strip[pos] == "M":
            pos += 1
        strip[pos] = "S"
    return strip


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reels")
    os.makedirs(out_dir, exist_ok=True)
    for name, (seed, weights, n_scatter) in REELSETS.items():
        rng = random.Random(seed)
        reels = [build_strip(rng, weights, n_scatter) for _ in range(NUM_REELS)]
        with open(os.path.join(out_dir, f"{name}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            for row in zip(*reels):
                writer.writerow(row)
        print(name, {s: sum(r.count(s) for r in reels) for s in list(weights) + ["S"]})


if __name__ == "__main__":
    main()
