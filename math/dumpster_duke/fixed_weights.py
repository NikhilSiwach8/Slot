"""Exact lookup-table weights for prize-or-nothing modes (no optimiser needed).

Max or Nothing only pays a few fixed prizes or 0. Each prize gets its share of the RTP
(MAX_OR_NOTHING_RTP_SHARE), so its chance is P(prize) = share * cost / prize and the mode
returns exactly its RTP.
"""
import csv
import os

from game_config import MAX_OR_NOTHING_RTP_SHARE

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "library")
TOTAL_WEIGHT = 10**12  # sum of all weights in the table


def write_all_or_nothing(config, mode_name):
    mode = next(m for m in config.bet_modes if m.get_name() == mode_name)
    cost = mode.get_cost()
    assert abs(sum(MAX_OR_NOTHING_RTP_SHARE.values()) - mode.get_rtp()) < 1e-9, "prize RTP shares must sum to the RTP"
    rows = list(csv.reader(open(os.path.join(LIB, "lookup_tables", f"lookUpTable_{mode_name}.csv"))))
    books = {0: [r for r in rows if int(r[2]) == 0]}
    for prize in MAX_OR_NOTHING_RTP_SHARE:
        books[prize] = [r for r in rows if int(r[2]) == int(prize * 100)]
    assert sum(len(b) for b in books.values()) == len(rows), "books must pay 0 or one of the prizes"

    chance = {prize: share * cost / prize for prize, share in MAX_OR_NOTHING_RTP_SHARE.items()}
    chance[0] = 1 - sum(chance.values())
    weight = {prize: round(TOTAL_WEIGHT * p / len(books[prize])) for prize, p in chance.items()}

    out = os.path.join(LIB, "publish_files", f"lookUpTable_{mode_name}_0.csv")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        for r in rows:
            w.writerow([r[0], weight[int(r[2]) // 100], r[2]])

    total = sum(weight[p] * len(books[p]) for p in books)
    rtp = sum(weight[p] * len(books[p]) * p for p in books) / total / cost
    odds = ", ".join(f"{p:g}x 1 in {total / (weight[p] * len(books[p])):.1f}" for p in MAX_OR_NOTHING_RTP_SHARE)
    print(f"{mode_name}: {odds}, RTP {rtp:.5%}")
