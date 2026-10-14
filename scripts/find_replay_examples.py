"""Pick example rounds (book ids) per bet mode for Stake's replay review:
normal win, big win, win cap, loss, bonus trigger. Only rounds that can actually
occur (weight > 0 in the published lookup table) are chosen.
Run with the math-sdk venv:  math-sdk/env/bin/python scripts/find_replay_examples.py
"""
import csv
import io
import json
import os

import zstandard

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLISH = os.path.join(ROOT, "math", "dumpster_duke", "library", "publish_files")


def examples(mode):
    weights = {}
    with open(os.path.join(PUBLISH, f"lookUpTable_{mode}_0.csv")) as f:
        for sim, weight, payout in csv.reader(f):
            weights[int(sim)] = (int(weight), int(payout) / 100)
    found = {}
    with open(os.path.join(PUBLISH, f"books_{mode}.jsonl.zst"), "rb") as f:
        for line in io.TextIOWrapper(zstandard.ZstdDecompressor().stream_reader(f), encoding="utf-8"):
            book = json.loads(line)
            weight, payout = weights.get(book["id"], (0, 0))
            if weight == 0:
                continue
            types = [e["type"] for e in book["events"]]
            # the round's biggest presented win level (setWin / freeSpinEnd carry it)
            level = max((e.get("winLevel", 0) for e in book["events"]), default=0)
            checks = {
                "loss": payout == 0,
                "normal win": 1 <= payout <= 5 and "freeSpinTrigger" not in types,
                "big win": level >= 6 and payout < 10000 and "freeSpinTrigger" not in types,
                "win cap": payout >= 10000,
                "bonus trigger": "freeSpinTrigger" in types and payout < 10000,
                "big bonus": "freeSpinTrigger" in types and level >= 8 and payout < 10000,
            }
            for name, ok in checks.items():
                if ok and name not in found:
                    found[name] = (book["id"], payout)
            if len(found) == len(checks):
                break
    return found


if __name__ == "__main__":
    for mode in ("base", "ante", "bonus"):
        print(mode)
        for name, (book_id, payout) in examples(mode).items():
            print(f"  {name:14s} event {book_id:>7}  pays {payout:g}x")
