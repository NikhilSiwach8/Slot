"""Whisker Tilt — core-mechanic prototype (not the math model).

Plays the Tilt Tumble on a 6x6 cluster-pays board with the four Edge Keepers,
so the mechanic can be watched and its rhythm measured before any math-sdk work.
Symbols are drawn from flat weights, not reel strips, and the paytable is a
placeholder: the stats this prints are about feel (tilts per spin, keeper
growth, Snowstorm frequency), never RTP.

    python tilt.py --demo 158                  # play one spin step by step
    python tilt.py --mode base --sims 20000    # mechanic stats; modes: base ante feature bonus super mystery
"""
import argparse
import random
from collections import Counter

SIZE = 6
MIN_CLUSTER = 5
# Gravity directions, clockwise: the cat's paw turns the globe a quarter each tilt.
DOWN, LEFT, UP, RIGHT = range(4)
DIR_NAMES = ["down", "left", "up", "right"]
EDGE_NAMES = ["South", "West", "North", "East"]  # the edge each direction falls onto

WEIGHTS = {
    "H1": 4, "H2": 5, "H3": 6, "H4": 7,
    "L1": 10, "L2": 11, "L3": 12, "L4": 13,
    "S": 1.25, "C": 2.2,
}
COIN_VALUES = {2: 50, 3: 25, 5: 15, 10: 7, 25: 2, 50: 1}
PAYS = {  # placeholder, x bet for cluster sizes 5,6,7,8,9-10,11-12,13-15,16+
    "H1": [1, 1.5, 2, 3, 5, 10, 25, 100], "H2": [0.8, 1.2, 1.6, 2.4, 4, 8, 20, 60],
    "H3": [0.6, 1, 1.4, 2, 3, 6, 15, 40], "H4": [0.5, 0.8, 1.2, 1.6, 2.5, 5, 12, 30],
    "L1": [0.3, 0.5, 0.8, 1, 1.5, 3, 8, 20], "L2": [0.25, 0.4, 0.6, 0.8, 1.2, 2.5, 6, 15],
    "L3": [0.2, 0.3, 0.5, 0.7, 1, 2, 5, 12], "L4": [0.2, 0.3, 0.4, 0.6, 0.9, 1.8, 4, 10],
}
SNOWSTORM_CAP = 1000  # a keeper never grows past this


def pay_for(sym, size):
    idx = min(size, 9) - 5 if size < 9 else (4 if size <= 10 else 5 if size <= 12 else 6 if size <= 15 else 7)
    return PAYS[sym][idx]


class Cell:
    __slots__ = ("sym", "value")

    def __init__(self, sym, value=0):
        self.sym, self.value = sym, value

    def __repr__(self):
        return f"C{self.value}" if self.sym == "C" else self.sym


def draw(rng):
    syms, w = zip(*WEIGHTS.items())
    sym = rng.choices(syms, w)[0]
    if sym == "C":
        vals, vw = zip(*COIN_VALUES.items())
        return Cell("C", rng.choices(vals, vw)[0])
    return Cell(sym)


def rotate_cw(b):
    return [list(r) for r in zip(*b[::-1])]


def rotate_ccw(b):
    return [list(r) for r in zip(*b)][::-1]


def to_frame(b, d):
    """Rotate the board so gravity `d` points down. LEFT needs the left edge at the bottom: ccw."""
    for _ in range({DOWN: 0, LEFT: 3, UP: 2, RIGHT: 1}[d]):
        b = rotate_cw(b)
    return b


def from_frame(b, d):
    for _ in range({DOWN: 0, LEFT: 3, UP: 2, RIGHT: 1}[d]):
        b = rotate_ccw(b)
    return b


def settle(board, d, rng):
    """Slide every cell toward gravity `d` and refill from the opposite side (snowfall)."""
    f = to_frame(board, d)
    for c in range(SIZE):
        col = [f[r][c] for r in range(SIZE) if f[r][c] is not None]
        col = [draw(rng) for _ in range(SIZE - len(col))] + col
        for r in range(SIZE):
            f[r][c] = col[r]
    return from_frame(f, d)


def on_edge(r, c, edge):
    return (r == SIZE - 1, c == 0, r == 0, c == SIZE - 1)[edge]


def collect_coins(board, d, keepers, rng, log):
    """Coins resting on the floor edge are banked by that edge's keeper, then the gap refills."""
    while True:
        hits = [(r, c) for r in range(SIZE) for c in range(SIZE)
                if board[r][c].sym == "C" and on_edge(r, c, d)]
        if not hits:
            return board
        for r, c in hits:
            keepers[d] += board[r][c].value
            log(f"  {EDGE_NAMES[d]} Keeper banks x{board[r][c].value} -> x{keepers[d]}")
            board[r][c] = None
        board = settle(board, d, rng)


def clusters(board):
    seen, out = set(), []
    for r in range(SIZE):
        for c in range(SIZE):
            sym = board[r][c].sym
            if (r, c) in seen or sym not in PAYS:
                continue
            stack, group = [(r, c)], []
            seen.add((r, c))
            while stack:
                y, x = stack.pop()
                group.append((y, x))
                for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                    if 0 <= ny < SIZE and 0 <= nx < SIZE and (ny, nx) not in seen and board[ny][nx].sym == sym:
                        seen.add((ny, nx))
                        stack.append((ny, nx))
            if len(group) >= MIN_CLUSTER:
                out.append((sym, group))
    return out


def cluster_multiplier(group, keepers):
    touched = {e for r, c in group for e in range(4) if on_edge(r, c, e)}
    return max(1, sum(keepers[e] for e in touched)), touched


def show(board, d, keepers, log):
    log(f"  gravity {DIR_NAMES[d]:>5} | keepers S x{keepers[0]} W x{keepers[1]} N x{keepers[2]} E x{keepers[3]}")
    for row in board:
        log("   " + " ".join(f"{str(x):>3}" for x in row))


def snowstorm(keepers, log):
    for e in range(4):
        keepers[e] = min(SNOWSTORM_CAP, keepers[e] * 2)
    log("  *** SNOWSTORM (full turn) — every keeper doubles")


def play_spin(rng, keepers=None, d=DOWN, turn=0, paw=False, log=lambda s: None):
    """One spin. Free spins pass keepers, gravity `d` and the quarter-turn count `turn` back in,
    and set `paw`: the cat bats the globe a quarter turn before the symbols drop."""
    keepers = keepers if keepers is not None else [0, 0, 0, 0]
    storms = 0
    if paw:
        d, turn = (d + 1) % 4, turn + 1
        if turn % 4 == 0:
            storms += 1
            snowstorm(keepers, log)
    board = [[None] * SIZE for _ in range(SIZE)]
    board = settle(board, d, rng)
    board = collect_coins(board, d, keepers, rng, log)
    win, tilts = 0.0, 0
    show(board, d, keepers, log)
    while True:
        found = clusters(board)
        if not found:
            break
        for sym, group in found:
            mult, touched = cluster_multiplier(group, keepers)
            amount = pay_for(sym, len(group)) * mult
            win += amount
            edges = ",".join(EDGE_NAMES[e] for e in sorted(touched)) or "none"
            log(f"  {sym} x{len(group)} touches [{edges}] -> {pay_for(sym, len(group))} * {mult} = {amount:g}")
            for r, c in group:
                board[r][c] = None
        d = (d + 1) % 4
        tilts += 1
        turn += 1
        if turn % 4 == 0:  # a full turn of the globe: Snowstorm
            storms += 1
            snowstorm(keepers, log)
        log(f" tilt {tilts}: paw turns the globe, gravity now {DIR_NAMES[d]}")
        board = settle(board, d, rng)
        board = collect_coins(board, d, keepers, rng, log)
        show(board, d, keepers, log)
    scatters = sum(cell.sym == "S" for row in board for cell in row)
    return dict(win=win, tilts=tilts, storms=storms, keepers=keepers, d=d, turn=turn, scatters=scatters)


FS_SPINS = {4: 10, 5: 12}  # keys landed -> free spins; 6+ keys -> Super Snow Day
SUPER_SPINS = 12
SUPER_KEEPERS = 2  # Super Snow Day: every wall starts lit at x2
MYSTERY_GIFTS = [  # (kind, spins, weight) revealed from Mitten's present
    ("free", 8, 30), ("free", 10, 25), ("free", 12, 20), ("free", 15, 12),
    ("super", 10, 9), ("super", 12, 4),
]
ANTE_KEY_BOOST = 1.2
FEATURE_KEEPERS = 2  # Feature Spins: every wall starts lit at x2 and the spin always wins


def play_bonus(rng, spins=10, start_keeper=0):
    """Free spins: keepers, gravity and the turn count never reset; 3+ scatters give +3 spins."""
    keepers, d, turn, win, storms, played = [start_keeper] * 4, DOWN, 0, 0.0, 0, 0
    while played < spins and played < 50:
        res = play_spin(rng, keepers, d, turn, paw=True)
        d, turn = res["d"], res["turn"]
        win += res["win"]
        storms += res["storms"]
        played += 1
        if res["scatters"] >= 3:
            spins += 3
    return dict(win=win, storms=storms, keepers=keepers, spins=played)


def bonus_entry(keys):
    """What a natural trigger awards: ("free"|"super", spins)."""
    return ("super", SUPER_SPINS) if keys >= 6 else ("free", FS_SPINS[keys])


def play_mystery(rng):
    kinds, spins, w = zip(*MYSTERY_GIFTS)
    i = rng.choices(range(len(w)), w)[0]
    res = play_bonus(rng, spins[i], SUPER_KEEPERS if kinds[i] == "super" else 0)
    res["gift"] = f"{kinds[i]} {spins[i]}"
    return res


def play_feature_spin(rng):
    """Feature Spins: walls start at x2, and only winning spins are dealt (the book set has no 0 wins)."""
    while True:
        res = play_spin(rng, [FEATURE_KEEPERS] * 4)
        if res["win"] > 0:
            return res


def report_rounds(title, rounds):
    n = len(rounds)
    print(f"{n} {title} (placeholder weights/paytable — feel only, not RTP)")
    print(f"spins played        avg {sum(r['spins'] for r in rounds) / n:.1f}")
    print(f"snowstorms/round    avg {sum(r['storms'] for r in rounds) / n:.2f}, "
          f"at least one {sum(r['storms'] > 0 for r in rounds) / n:.0%}")
    top = sorted(max(r["keepers"]) for r in rounds)
    print(f"biggest keeper      median x{top[n // 2]}, p90 x{top[n * 9 // 10]}, p99 x{top[n * 99 // 100]}")
    print(f"edges lit at end    avg {sum(sum(k > 0 for k in r['keepers']) for r in rounds) / n:.2f} of 4")
    if "gift" in rounds[0]:
        gifts = Counter(r["gift"] for r in rounds)
        print("gifts               " + "  ".join(f"{g}:{v / n:.0%}" for g, v in sorted(gifts.items())))


def report_spins(title, spins, triggers=None):
    n = len(spins)
    tilts = Counter(r["tilts"] for r in spins)
    lit = Counter(sum(k > 0 for k in r["keepers"]) for r in spins)
    print(f"{n} {title} (placeholder weights/paytable — feel only, not RTP)")
    print(f"hit rate            1 in {n / max(sum(r['win'] > 0 for r in spins), 1):.2f}")
    print("tilts per spin      " + "  ".join(f"{k}:{v / n:.1%}" for k, v in sorted(tilts.items())))
    print(f"full turn (storm)   1 in {n / max(sum(r['storms'] > 0 for r in spins), 1):.0f} spins")
    print("keepers lit at end  " + "  ".join(f"{k}:{v / n:.1%}" for k, v in sorted(lit.items())))
    if triggers is not None:
        print(f"bonus trigger       1 in {n / max(sum(triggers.values()), 1):.0f} spins  "
              + "  ".join(f"{k}:{v}" for k, v in sorted(triggers.items())))


MODES = ["base", "ante", "feature", "bonus", "super", "mystery"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", type=int, help="seed of one spin to print step by step")
    ap.add_argument("--sims", type=int, default=20000)
    ap.add_argument("--mode", choices=MODES, default="base",
                    help="max-or-nothing has no prototype: it is a book-distribution choice, see CONCEPT.md")
    args = ap.parse_args()
    if args.demo is not None:
        res = play_spin(random.Random(args.demo), log=print)
        print(f"total win {res['win']:g}x, tilts {res['tilts']}, snowstorms {res['storms']}")
        return
    rng = random.Random(1)
    n = args.sims
    if args.mode in ("base", "ante"):
        if args.mode == "ante":  # Double Chance: 4+ keys need ~4 of them, so 2^(1/4) more keys ~ 2x triggers
            WEIGHTS["S"] *= ANTE_KEY_BOOST
        spins = [play_spin(rng) for _ in range(n)]
        triggers = Counter(bonus_entry(r["scatters"]) for r in spins if r["scatters"] >= 4)
        report_spins(f"{args.mode} spins", spins, Counter({f"{k} {v}": c for (k, v), c in triggers.items()}))
    elif args.mode == "feature":
        report_spins("feature spins", [play_feature_spin(rng) for _ in range(n)])
    elif args.mode == "bonus":
        report_rounds("Snow Day rounds of 10", [play_bonus(rng, 10) for _ in range(n)])
    elif args.mode == "super":
        report_rounds(f"Super Snow Day rounds of {SUPER_SPINS}",
                      [play_bonus(rng, SUPER_SPINS, SUPER_KEEPERS) for _ in range(n)])
    else:
        report_rounds("Mystery Snow Day rounds", [play_mystery(rng) for _ in range(n)])


if __name__ == "__main__":
    main()
