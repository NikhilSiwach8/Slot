"""Dumpster Duke — 6x5 pay-anywhere tumbling game with bottle-cap multipliers."""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


# Costs (x bet) of the extra modes. Measured from the natural round averages and checked by
# analyze.py; the optimiser then tunes weights to the 96.5% RTP at these prices.
FEATURE_COST = 5.0
SUPER_COST = 250.0
MYSTERY_COST = 100.0
MAX_COST = 200.0
# Max or Nothing pays this or nothing. Kept under 5,000x so the mode passes Stake's tail
# checks (P(win >= 5,000x) and the RTP share of 10,000x wins); 1 in 20.7 at 200x.
MAX_OR_NOTHING_WIN = 4000
# Max or Nothing: every Candy Cap on its spin is a MAX cap. Its value only has to lift the
# smallest win (0.4x) to the 10,000x max win; the client shows it as "MAX".
MAX_CAP = 25000


class GameConfig(Config):
    """Load all game specific parameters and elements"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "dumpster_duke"
        self.game_name = "dumpster_duke"
        self.provider_name = "nyxhilx"
        self.provider_number = 0
        self.working_name = "Dumpster Duke"
        self.wincap = 10000.0
        self.win_type = "scatter"
        self.rtp = 0.965
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 6
        self.num_rows = [5] * self.num_reels

        # Pay anywhere: 8+ of a kind, grouped by count on board
        t1, t2, t3, t4 = (8, 9), (10, 11), (12, 14), (15, 30)
        pay_group = {
            (t1, "H1"): 10.0,
            (t2, "H1"): 25.0,
            (t3, "H1"): 50.0,
            (t4, "H1"): 100.0,
            (t1, "H2"): 2.5,
            (t2, "H2"): 10.0,
            (t3, "H2"): 25.0,
            (t4, "H2"): 50.0,
            (t1, "H3"): 2.0,
            (t2, "H3"): 5.0,
            (t3, "H3"): 15.0,
            (t4, "H3"): 40.0,
            (t1, "H4"): 1.5,
            (t2, "H4"): 2.0,
            (t3, "H4"): 12.0,
            (t4, "H4"): 30.0,
            (t1, "L1"): 1.0,
            (t2, "L1"): 1.5,
            (t3, "L1"): 10.0,
            (t4, "L1"): 20.0,
            (t1, "L2"): 0.8,
            (t2, "L2"): 1.2,
            (t3, "L2"): 8.0,
            (t4, "L2"): 16.0,
            (t1, "L3"): 0.5,
            (t2, "L3"): 1.0,
            (t3, "L3"): 5.0,
            (t4, "L3"): 12.0,
            (t1, "L4"): 0.4,
            (t2, "L4"): 0.9,
            (t3, "L4"): 4.0,
            (t4, "L4"): 10.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        # No wild in this game; the key must exist for the scatter-pay calculator.
        self.special_symbols = {"wild": ["W"], "scatter": ["S"], "multiplier": ["M"]}

        self.freespin_triggers = {
            self.basegame_type: {4: 10, 5: 12, 6: 15},
            self.freegame_type: {3: 5, 4: 5, 5: 5, 6: 5},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]

        base_caps = {2: 300, 3: 150, 4: 80, 5: 40, 8: 15, 10: 8, 15: 4, 20: 2, 25: 1, 50: 0.4, 100: 0.1}
        fs_caps = {2: 200, 3: 120, 4: 80, 5: 60, 8: 30, 10: 20, 15: 12, 20: 8, 25: 6, 50: 3, 100: 1.5}
        wincap_caps = {10: 20, 15: 20, 20: 30, 25: 30, 50: 40, 100: 30}

        # Every bottle-cap value a player can see, for the rules screen.
        self.cap_values = sorted(set(base_caps) | set(fs_caps) | set(wincap_caps))

        mode_maxwins = {m: 10000 for m in ("base", "ante", "feature", "bonus", "super", "mystery")}
        mode_maxwins["max"] = MAX_OR_NOTHING_WIN

        def wincap_dist(scatter_triggers, extra=None, quota=0.001):
            return Distribution(
                criteria="wincap",
                quota=quota,
                win_criteria=mode_maxwins["base"],
                conditions={
                    "reel_weights": {
                        self.basegame_type: {"BR0": 1},
                        self.freegame_type: {"FR0": 1, "WCAP": 4},
                    },
                    "mult_values": {self.basegame_type: base_caps, self.freegame_type: wincap_caps},
                    "scatter_triggers": scatter_triggers,
                    "force_wincap": True,
                    "force_freegame": True,
                    **(extra or {}),
                },
            )

        def freegame_dist(quota, scatter_triggers, extra=None):
            return Distribution(
                criteria="freegame",
                quota=quota,
                conditions={
                    "reel_weights": {
                        self.basegame_type: {"BR0": 1},
                        # The rich WCAP strip shows up now and then so huge raids are reachable.
                        self.freegame_type: {"FR0": 40, "WCAP": 1},
                    },
                    "scatter_triggers": scatter_triggers,
                    "mult_values": {self.basegame_type: base_caps, self.freegame_type: fs_caps},
                    "force_wincap": False,
                    "force_freegame": True,
                    **(extra or {}),
                },
            )

        def base_dists(freegame_quota=0.1, extra=None):
            return [
                    wincap_dist({5: 1, 6: 2}, extra),
                    freegame_dist(freegame_quota, {4: 20, 5: 4, 6: 1}, extra),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {self.basegame_type: base_caps, self.freegame_type: fs_caps},
                            "force_wincap": False,
                            "force_freegame": False,
                            **(extra or {}),
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {self.basegame_type: base_caps, self.freegame_type: fs_caps},
                            "force_wincap": False,
                            "force_freegame": False,
                            **(extra or {}),
                        },
                    ),
                ]

        super_raid = {"start_loot_bag": {10: 1}, "guarantee_cap": [self.freegame_type]}
        mystery = {
            "mystery_spins": {5: 30, 8: 25, 10: 20, 12: 12, 15: 8, 20: 4, 25: 1},
            "mystery_loot_bag": {0: 30, 2: 25, 3: 15, 5: 12, 8: 8, 10: 6, 15: 3, 20: 1},
        }

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=base_dists(),
            ),
            # Ante: 25% extra stake, Midnight Raid lands twice as often (hit rates set in game_optimization.py)
            BetMode(
                name="ante",
                cost=1.25,
                rtp=self.rtp,
                max_win=mode_maxwins["ante"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=base_dists(freegame_quota=0.15),
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    wincap_dist({5: 1, 6: 2}),
                    freegame_dist(0.999, {4: 20, 5: 4, 6: 1}),
                ],
            ),
            # Feature Spin: stays on like Double Chance. Every spin shows 3 Golden Trash Cans
            # (one short of the raid) and at least one Bottle Cap.
            BetMode(
                name="feature",
                cost=FEATURE_COST,
                rtp=self.rtp,
                max_win=mode_maxwins["feature"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=base_dists(
                    freegame_quota=0.15,
                    extra={"tease_scatters": 3, "guarantee_cap": [self.basegame_type]},
                ),
            ),
            # Super Raid: the Loot Bag starts at x10 and every free spin shows a Bottle Cap.
            BetMode(
                name="super",
                cost=SUPER_COST,
                rtp=self.rtp,
                max_win=mode_maxwins["super"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    wincap_dist({5: 1, 6: 2}, super_raid),
                    freegame_dist(0.999, {4: 20, 5: 4, 6: 1}, super_raid),
                ],
            ),
            # Mystery Bonus: a chest reveals 5-25 free spins and a starting Loot Bag of x0-x20.
            BetMode(
                name="mystery",
                cost=MYSTERY_COST,
                rtp=self.rtp,
                max_win=mode_maxwins["mystery"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    wincap_dist({5: 1, 6: 2}, mystery),
                    freegame_dist(0.999, {4: 20, 5: 4, 6: 1}, mystery),
                ],
            ),
            # Max or Nothing: one paid spin, no free spins. Every board shows a MAX cap; if the
            # spin wins anything at all (with tumbles), the MAX cap lifts it to this mode's max
            # win (MAX_OR_NOTHING_WIN). A dead spin pays 0.
            BetMode(
                name="max",
                cost=MAX_COST,
                rtp=self.rtp,
                max_win=mode_maxwins["max"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria=criteria,
                        quota=quota,
                        win_criteria=win,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "mult_values": {self.basegame_type: {MAX_CAP: 1}, self.freegame_type: fs_caps},
                            "force_wincap": False,
                            "force_freegame": False,
                            "guarantee_cap": [self.basegame_type],
                            "max_or_nothing": True,
                        },
                    )
                    for criteria, quota, win in (("max", 0.02, float(MAX_OR_NOTHING_WIN)), ("0", 0.98, 0.0))
                ],
            ),
        ]
