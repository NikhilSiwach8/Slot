"""Exact lookup-table weights for all-or-nothing modes (no optimiser needed).

Max or Nothing only has two outcomes: the mode's max win or 0. The chance of the
prize is set so the mode returns exactly its RTP: P(prize) = rtp * cost / prize.
"""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "library")
BASE_WEIGHT = 1_000_000  # weight of each 0x book; cap books get the matching larger weight


def write_all_or_nothing(config, mode_name):
    mode = next(m for m in config.bet_modes if m.get_name() == mode_name)
    prize = mode.get_wincap()
    p_cap = mode.get_rtp() * mode.get_cost() / prize
    rows = list(csv.reader(open(os.path.join(LIB, "lookup_tables", f"lookUpTable_{mode_name}.csv"))))
    cap = [r for r in rows if int(r[2]) >= int(prize * 100)]
    zero = [r for r in rows if int(r[2]) == 0]
    assert len(cap) + len(zero) == len(rows), "all-or-nothing books must pay 0 or the cap"
    cap_weight = round(BASE_WEIGHT * p_cap * len(zero) / ((1 - p_cap) * len(cap)))
    out = os.path.join(LIB, "publish_files", f"lookUpTable_{mode_name}_0.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow([r[0], cap_weight if int(r[2]) > 0 else BASE_WEIGHT, r[2]])
    total = cap_weight * len(cap) + BASE_WEIGHT * len(zero)
    rtp = cap_weight * len(cap) * prize / total / mode.get_cost()
    print(f"{mode_name}: {len(cap)} cap books, {len(zero)} zero books, P(cap) 1 in {total / (cap_weight * len(cap)):.2f}, RTP {rtp:.5%}")
