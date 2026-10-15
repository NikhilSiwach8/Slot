"""Generate reel strips for Whisker Tilt.

Usage: python make_reels.py   (writes reels/*.csv)

6 strips of 300 per set, one per reel. Sideways tilts reuse the same strips:
lane i (a column when gravity is vertical, a row when it is horizontal) refills
from strip i. Strips are runs of 1-3 identical paying symbols, which gives the
clumping cluster pays need. Keys (S) are kept at least ROWS+1 apart so a reel
window never shows two; Snowflake Coins (C) are single.
"""

import csv
import os
import random

NUM_REELS = 6
ROWS = 6
STRIP_LEN = 300
RUN_LENGTHS = {1: 70, 2: 25, 3: 5}

REELSETS = {
    # name: (seed, symbol weights, keys per reel)
    "BR0": (101, {"H1": 5, "H2": 6, "H3": 7, "H4": 8, "L1": 11, "L2": 12, "L3": 13, "L4": 14, "C": 1.2}, 3),
    # Catnip (ante): more keys on the strips, so near-misses with 3 keys show up more often.
    "BRA": (111, {"H1": 5, "H2": 6, "H3": 7, "H4": 8, "L1": 11, "L2": 12, "L3": 13, "L4": 14, "C": 1.2}, 4),
    "FR0": (202, {"H1": 6, "H2": 7, "H3": 8, "H4": 9, "L1": 11, "L2": 12, "L3": 13, "L4": 14, "C": 16.0}, 2),
    # Super Snow Day: heavier coin strip.
    "FRS": (212, {"H1": 6, "H2": 7, "H3": 8, "H4": 9, "L1": 11, "L2": 12, "L3": 13, "L4": 14, "C": 22.0}, 2),
    # Rich strip for building max-win rounds.
    "WCAP": (303, {"H1": 14, "H2": 10, "H3": 8, "H4": 7, "L1": 6, "L2": 5, "L3": 4, "L4": 4, "C": 6.0}, 2),
}
SINGLES = {"S", "C"}


def weighted(rng, table):
    keys = list(table)
    return rng.choices(keys, [table[k] for k in keys])[0]


def build_strip(rng, weights, n_keys):
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
    # Keys: evenly spaced (with jitter) so a window never shows two; never replace a coin.
    gap = STRIP_LEN // n_keys
    for k in range(n_keys):
        pos = k * gap + rng.randrange(ROWS, gap - ROWS)
        while strip[pos] == "C":
            pos += 1
        strip[pos] = "S"
    return strip


def main():
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reels")
    os.makedirs(out_dir, exist_ok=True)
    for name, (seed, weights, n_keys) in REELSETS.items():
        rng = random.Random(seed)
        reels = [build_strip(rng, weights, n_keys) for _ in range(NUM_REELS)]
        with open(os.path.join(out_dir, f"{name}.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            for row in zip(*reels):
                writer.writerow(row)
        print(name, {s: sum(r.count(s) for r in reels) for s in list(weights) + ["S"]})


if __name__ == "__main__":
    main()
