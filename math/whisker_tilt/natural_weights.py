"""Weight the simulated books by their natural frequency instead of the optimizer's curve fit.

The Rust optimizer builds each criteria's win distribution out of random bell curves centred
on the target average. For this game that bunched base-mode bonuses around ~85x and starved
1-5x base wins. Here every book in a criteria gets the same weight; only the criteria totals
are set (trigger rate, max-win rate) and one criteria is solved so the mode hits the RTP.

    python natural_weights.py            # base, ante, feature
    python natural_weights.py base       # one mode
"""

import csv
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "library")
TOTAL_WEIGHT = 2**50
RTP = 0.965

# fixed: probability per round; solve: criteria whose share sets the RTP;
# rest: criteria that takes the remaining probability (None = the solved one does).
MODES = {
    "base": {"cost": 1.0, "fixed": {"wincap": 1 / 5e6, "freegame": 1 / 240}, "solve": "basegame", "rest": "0"},
    "ante": {"cost": 1.25, "fixed": {"wincap": 1 / 4e6, "freegame": 1 / 120}, "solve": "basegame", "rest": "0"},
    "feature": {"cost": 5.0, "fixed": {"wincap": 1 / 1e6}, "solve": "freegame", "rest": "basegame"},
}


def load(mode):
    pays, crit = {}, {}
    with open(os.path.join(LIB, "lookup_tables", f"lookUpTable_{mode}.csv")) as f:
        for sim, _w, pay in csv.reader(f):
            pays[int(sim)] = int(pay)
    with open(os.path.join(LIB, "lookup_tables", f"lookUpTableSegmented_{mode}.csv")) as f:
        for sim, c, _b, _fr in csv.reader(f):
            crit[int(sim)] = c
    return pays, crit


def solve_shares(spec, means):
    target = RTP * spec["cost"]
    fixed = dict(spec["fixed"])
    fixed_p = sum(fixed.values())
    fixed_ev = sum(p * means[c] for c, p in fixed.items())
    s, r = spec["solve"], spec["rest"]
    m_s, m_r = means[s], means[r]
    # p_s * m_s + (1 - fixed_p - p_s) * m_r = target - fixed_ev
    p_s = (target - fixed_ev - (1 - fixed_p) * m_r) / (m_s - m_r)
    shares = {**fixed, s: p_s, r: 1 - fixed_p - p_s}
    if not 0 < p_s < 1 - fixed_p:
        raise ValueError(f"no valid share for {s}: {p_s:.5f} (means {means})")
    return shares


def weight_mode(mode):
    spec = MODES[mode]
    pays, crit = load(mode)
    by_crit = defaultdict(list)
    for sim, c in crit.items():
        by_crit[c].append(sim)
    means = {c: sum(pays[s] for s in sims) / 100 / len(sims) for c, sims in by_crit.items()}
    shares = solve_shares(spec, means)

    weights = {}
    for c, sims in by_crit.items():
        w = max(1, int(TOTAL_WEIGHT * shares[c] / len(sims)))
        for s in sims:
            weights[s] = w
    out = os.path.join(LIB, "publish_files", f"lookUpTable_{mode}_0.csv")
    with open(out, "w", newline="") as f:
        writer = csv.writer(f)
        for sim in sorted(pays):
            writer.writerow([sim, weights[sim], pays[sim]])

    tot = sum(weights.values())
    rtp = sum(weights[s] * pays[s] for s in pays) / 100 / tot / spec["cost"]
    print(f"[{mode}] RTP {rtp * 100:.4f}%  " + "  ".join(f"{c}: 1 in {1 / p:,.1f} (avg {means[c]:.2f}x)" for c, p in shares.items()))
    return rtp


if __name__ == "__main__":
    for m in sys.argv[1:] or list(MODES):
        weight_mode(m)
