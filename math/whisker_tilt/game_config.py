"""Whisker Tilt — 6x6 cluster tumble where gravity turns 90 degrees after every win.

Design: concepts/whisker-tilt/CONCEPT.md
"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode

BOARD = 6
MAX_FREE_SPINS = 50
FREE_RETRIGGER = 3

# Free-spin kinds a trigger can award.
FREE, SUPER, MYSTERY = "free", "super", "mystery"


class GameConfig(Config):
    """Load all game specific parameters and elements"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "whisker_tilt"
        self.game_name = "whisker_tilt"
        self.provider_name = "nyxhilx"
        self.provider_number = 0
        self.working_name = "Whisker Tilt"
        self.wincap = 10000.0
        self.win_type = "cluster"
        self.rtp = 0.965
        self.construct_paths()

        # Game dimensions. The board is square so every quarter turn keeps its shape.
        self.num_reels = BOARD
        self.num_rows = [BOARD] * self.num_reels

        # Cluster pays: 5+ orthogonally connected, grouped by cluster size.
        sizes = [(5, 5), (6, 6), (7, 7), (8, 8), (9, 10), (11, 12), (13, 15), (16, 36)]
        pays = {
            "H1": [1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 25.0, 100.0],
            "H2": [0.8, 1.2, 1.6, 2.4, 4.0, 8.0, 20.0, 60.0],
            "H3": [0.6, 1.0, 1.4, 2.0, 3.0, 6.0, 15.0, 40.0],
            "H4": [0.5, 0.8, 1.2, 1.6, 2.5, 5.0, 12.0, 30.0],
            "L1": [0.3, 0.5, 0.8, 1.0, 1.5, 3.0, 8.0, 20.0],
            "L2": [0.25, 0.4, 0.6, 0.8, 1.2, 2.5, 6.0, 15.0],
            "L3": [0.2, 0.3, 0.5, 0.7, 1.0, 2.0, 5.0, 12.0],
            "L4": [0.2, 0.3, 0.4, 0.6, 0.9, 1.8, 4.0, 10.0],
        }
        pay_scale = 3.0
        # Stake needs every payout in 0.1x steps: pays are rounded to 0.1, keepers are whole numbers.
        pay_group = {(size, sym): round(values[i] * pay_scale + 1e-9, 1) for sym, values in pays.items() for i, size in enumerate(sizes)}
        self.paytable = self.convert_range_table(pay_group)
        self.min_cluster = min(s[0] for s in sizes)

        # No padding: symbols enter from whichever wall is opposite the floor, so a fixed
        # row above/below the board means nothing here.
        self.include_padding = False
        # S = Wind-up Key (scatter), C = Snowflake Coin (value in the "multiplier" attribute).
        self.special_symbols = {"scatter": ["S"], "multiplier": ["C"]}

        # Sideways refills read other strips, so a board can hold more than 6 keys.
        self.freespin_triggers = {
            self.basegame_type: {n: (10 if n == 4 else 12) for n in range(4, BOARD * BOARD + 1)},
            self.freegame_type: {n: FREE_RETRIGGER for n in range(3, BOARD * BOARD + 1)},
        }
        self.super_trigger = 6  # 6+ keys in the base game award Super Snow Day
        self.super_spins = 12
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        # Edge Keepers
        self.super_start_keeper = 5  # Super Snow Day: every wall starts lit at x5
        self.feature_start_keeper = 2  # Paw Spins: every wall starts lit at x2
        self.keeper_cap = 1000  # a Snowstorm never doubles a keeper past this

        # Mitten's Gift: what the present can hold, (kind, spins): weight
        self.mystery_gifts = {
            (FREE, 8): 20,
            (FREE, 10): 25,
            (FREE, 12): 20,
            (FREE, 15): 15,
            (SUPER, 10): 12,
            (SUPER, 12): 8,
        }

        reels = {r: f"{r}.csv" for r in ("BR0", "BRA", "FR0", "FRS", "WCAP")}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))
        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]

        # Snowflake Coin values
        base_coins = {2: 50, 3: 25, 5: 15, 10: 6, 25: 1.5, 50: 0.5}
        fs_coins = {2: 40, 3: 25, 5: 18, 10: 10, 25: 3, 50: 1}
        wincap_coins = {5: 20, 10: 30, 25: 30, 50: 20}
        self.coin_values = sorted(set(base_coins) | set(fs_coins) | set(wincap_coins))

        def conditions(base_reels, fs_reels, fs_coin_values=fs_coins, **extra):
            cond = {
                "reel_weights": {self.basegame_type: base_reels, self.freegame_type: fs_reels},
                "mult_values": {self.basegame_type: base_coins, self.freegame_type: fs_coin_values},
                "force_wincap": False,
                "force_freegame": False,
                "fs_kind": "natural",  # natural: 4-5 keys Snow Day, 6+ Super Snow Day
                "base_keeper": 0,
                "max_or_nothing": False,
            }
            cond.update(extra)
            return cond

        def wincap_dist(base_reels, scatter_triggers, quota=0.001, **extra):
            return Distribution(
                criteria="wincap",
                quota=quota,
                win_criteria=self.wincap,
                conditions=conditions(
                    base_reels,
                    {"FR0": 1, "FRS": 1, "WCAP": 4},
                    wincap_coins,
                    scatter_triggers=scatter_triggers,
                    force_wincap=True,
                    force_freegame=True,
                    **extra,
                ),
            )

        def freegame_dist(base_reels, quota, scatter_triggers, fs_reels=None, **extra):
            return Distribution(
                criteria="freegame",
                quota=quota,
                conditions=conditions(
                    base_reels,
                    fs_reels or {"FR0": 40, "WCAP": 1},
                    scatter_triggers=scatter_triggers,
                    force_freegame=True,
                    **extra,
                ),
            )

        def base_dists(base_reels, freegame_quota=0.1):
            return [
                wincap_dist(base_reels, {5: 1, 6: 2}),
                freegame_dist(base_reels, freegame_quota, {4: 20, 5: 4, 6: 1}),
                Distribution(criteria="0", quota=0.4, win_criteria=0.0, conditions=conditions(base_reels, {"FR0": 1})),
                Distribution(criteria="basegame", quota=0.5, conditions=conditions(base_reels, {"FR0": 1})),
            ]

        br0 = {"BR0": 1}
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=base_dists(br0),
            ),
            # Catnip: 1.25x, Snow Day twice as often (hit rates set in game_optimization.py).
            BetMode(
                name="ante",
                cost=1.25,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=base_dists({"BRA": 1}, freegame_quota=0.15),
            ),
            # Paw Spins: walls start at x2 and every spin wins (no "0" books).
            BetMode(
                name="feature",
                cost=5.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    wincap_dist(br0, {5: 1, 6: 2}, base_keeper=self.feature_start_keeper),
                    freegame_dist(br0, 0.1, {4: 20, 5: 4, 6: 1}, base_keeper=self.feature_start_keeper),
                    Distribution(
                        criteria="basegame",
                        quota=0.9,
                        conditions=conditions(br0, {"FR0": 1}, base_keeper=self.feature_start_keeper),
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    wincap_dist(br0, {4: 5, 5: 1}, fs_kind=FREE),
                    freegame_dist(br0, 0.999, {4: 5, 5: 1}, fs_kind=FREE),
                ],
            ),
            BetMode(
                name="super",
                cost=250.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    wincap_dist(br0, {6: 1}, quota=0.003, fs_kind=SUPER),
                    freegame_dist(br0, 0.997, {6: 1}, fs_reels={"FRS": 40, "WCAP": 1}, fs_kind=SUPER),
                ],
            ),
            BetMode(
                name="mystery",
                cost=140.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    wincap_dist(br0, {4: 1}, quota=0.002, fs_kind=MYSTERY),
                    freegame_dist(br0, 0.998, {4: 1}, fs_kind=MYSTERY),
                ],
            ),
            # Off the Shelf: a Super Snow Day that pays 10,000x if it reaches the cap, else 0.
            BetMode(
                name="max_or_nothing",
                cost=200.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    wincap_dist(br0, {6: 1}, quota=0.05, fs_kind=SUPER, max_or_nothing=True),
                    Distribution(
                        criteria="0",
                        quota=0.95,
                        win_criteria=0.0,
                        conditions=conditions(
                            br0,
                            {"FRS": 40, "WCAP": 1},
                            scatter_triggers={6: 1},
                            force_freegame=True,
                            fs_kind=SUPER,
                            max_or_nothing=True,
                        ),
                    ),
                ],
            ),
        ]
