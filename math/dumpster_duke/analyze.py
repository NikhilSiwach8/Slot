"""Summarise the optimized lookup tables: RTP, hit rate, bonus frequency, max win.
Usage (from math-sdk root or anywhere): python analyze.py"""
import csv, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "library")
COST = {"base": 1.0, "ante": 1.25, "feature": 5.0, "bonus": 100.0, "super": 250.0, "mystery": 100.0, "max": 200.0}
WINCAP = 60000.0


def load(mode):
    weights = {}
    with open(os.path.join(LIB, "publish_files", f"lookUpTable_{mode}_0.csv")) as f:
        for sim, w, pay in csv.reader(f):
            weights[int(sim)] = (int(w), int(pay) / 100)
    criteria = {}
    with open(os.path.join(LIB, "lookup_tables", f"lookUpTableSegmented_{mode}.csv")) as f:
        for sim, crit, _base, _free in csv.reader(f):
            criteria[int(sim)] = crit
    return weights, criteria


for mode, cost in COST.items():
    weights, criteria = load(mode)
    tot = sum(w for w, _ in weights.values())
    ev = sum(w * p for w, p in weights.values()) / tot
    ev2 = sum(w * p * p for w, p in weights.values()) / tot
    hit = sum(w for w, p in weights.values() if p > 0) / tot
    fs = sum(weights[s][0] for s in weights if criteria[s] in ("freegame", "wincap")) / tot
    maxw = max(p for w, p in weights.values() if w > 0)
    p_max = sum(w for w, p in weights.values() if p >= WINCAP) / tot
    nonzero = sum(1 for w, p in weights.values() if w > 0)
    print(f"[{mode}] cost {cost:g}x")
    print(f"  RTP            {ev / cost * 100:.3f}%")
    print(f"  hit rate       1 in {1 / hit:.2f}" if hit else "  hit rate 0")
    if mode == "base":
        print(f"  bonus trigger  1 in {1 / fs:.0f}" if fs else "  bonus trigger never")
    print(f"  std dev        {math.sqrt(ev2 - ev * ev) / cost:.2f} (per unit cost)")
    print(f"  max win        {maxw:g}x bet, P(>= cap) = 1 in {1 / p_max:,.0f}" if p_max else f"  max win {maxw:g}x (cap never hit)")
    print(f"  outcomes with weight > 0: {nonzero:,} of {len(weights):,}")
    edges = [0, 1e-9, 1, 5, 20, 100, 500, 2000, WINCAP, float("inf")]
    edges = [e * cost for e in edges[:-1]] + [float("inf")] if mode == "bonus" else edges
    print("  win distribution (x bet):")
    for lo, hi in zip(edges, edges[1:]):
        share = sum(w for w, p in weights.values() if lo <= p < hi) / tot
        if share:
            print(f"    [{lo:>8g}, {hi:>8g})  1 in {1 / share:>12,.1f}")
