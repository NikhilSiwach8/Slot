"""Optimizer targets for the seven Whisker Tilt bet modes (RTP 96.5% each)."""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructFenceBias,
    ConstructConditions,
    verify_optimization_input,
)

RTP = 0.965
# Average Snow Day pays ~88x bet before optimisation; trigger rates below set its RTP share.
SNOW_DAY_AV = 88.0


def cond(**kw):
    return ConstructConditions(**kw).return_dict()


def params(test_spins, test_weights):
    return ConstructParameters(
        num_show=5000,
        num_per_fence=10000,
        min_m2m=4,
        max_m2m=8,
        pmb_rtp=1.0,
        sim_trials=5000,
        test_spins=test_spins,
        test_weights=test_weights,
        score_type="rtp",
        max_trial_dist=15,
    ).return_dict()


def scaling(*rules):
    return ConstructScaling(
        [{"criteria": c, "scale_factor": f, "win_range": r, "probability": 1.0} for c, f, r in rules]
    ).return_dict()


def base_like(cost, trigger_hr, base_hr, wincap_rtp=0.002):
    """Base and Catnip: the Snow Day share follows from its trigger rate, base wins carry the rest."""
    fs_rtp = round(SNOW_DAY_AV / (trigger_hr * cost), 3)
    return {
        "conditions": {
            "wincap": cond(rtp=wincap_rtp, av_win=10000, search_conditions=10000),
            "0": cond(rtp=0, av_win=0, search_conditions=0),
            "freegame": cond(rtp=fs_rtp, hr=trigger_hr, search_conditions={"symbol": "scatter"}),
            "basegame": cond(hr=base_hr, rtp=round(RTP - wincap_rtp - fs_rtp, 5)),
        },
        "scaling": scaling(
            ("basegame", 1.2, (1, 2)),
            ("basegame", 1.5, (10, 20)),
            ("freegame", 0.8, (2000, 5000)),
            ("freegame", 1.2, (5000, 9000)),
        ),
        "parameters": params([50, 100, 200], [0.3, 0.4, 0.3]),
        "distribution_bias": ConstructFenceBias(
            applied_criteria=["basegame"], bias_ranges=[(3.0, 5.0)], bias_weights=[0.5]
        ).return_dict(),
    }


def buy(cost, wincap_rtp):
    return {
        "conditions": {
            "wincap": cond(rtp=wincap_rtp, av_win=10000, search_conditions=10000),
            "freegame": cond(rtp=round(RTP - wincap_rtp, 5), hr="x"),
        },
        "scaling": scaling(("freegame", 1.2, (5000, 9000))),
        "parameters": params([10, 20, 50], [0.6, 0.2, 0.2]),
        "distribution_bias": ConstructFenceBias(
            applied_criteria=["freegame"], bias_ranges=[(0.9 * cost, 1.5 * cost)], bias_weights=[0.1]
        ).return_dict(),
    }


class OptimizationSetup:
    """Handle all game mode optimization parameters."""

    def __init__(self, game_config):
        self.game_config = game_config
        feature_cost = 5.0
        feature_fs_hr = 200
        feature_fs_rtp = round(SNOW_DAY_AV / (feature_fs_hr * feature_cost), 3)
        self.game_config.opt_params = {
            "base": base_like(1.0, trigger_hr=240, base_hr=3.5),
            # Catnip: 1.25x cost, Snow Day twice as often.
            "ante": base_like(1.25, trigger_hr=120, base_hr=4.5),
            # Paw Spins: every spin wins, so the base-game share has no hit-rate target.
            "feature": {
                "conditions": {
                    "wincap": cond(rtp=0.002, av_win=10000, search_conditions=10000),
                    "freegame": cond(rtp=feature_fs_rtp, hr=feature_fs_hr, search_conditions={"symbol": "scatter"}),
                    "basegame": cond(rtp=round(RTP - 0.002 - feature_fs_rtp, 5), hr="x"),
                },
                "scaling": scaling(("basegame", 1.2, (5, 20))),
                "parameters": params([50, 100, 200], [0.3, 0.4, 0.3]),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"], bias_ranges=[(4.0, 8.0)], bias_weights=[0.3]
                ).return_dict(),
            },
            "bonus": buy(100.0, wincap_rtp=0.001),
            "super": buy(250.0, wincap_rtp=0.004),
            "mystery": buy(140.0, wincap_rtp=0.002),
            # Off the Shelf: all of the RTP sits on the cap; P(cap) = 0.965 * 200 / 10,000 = 1 in ~52.
            "max_or_nothing": {
                "conditions": {
                    "wincap": cond(rtp=RTP, av_win=10000, search_conditions=10000),
                    "0": cond(rtp=0, av_win=0, search_conditions=0),
                },
                "scaling": scaling(),
                "parameters": params([10, 20, 50], [0.6, 0.2, 0.2]),
                "distribution_bias": ConstructFenceBias(applied_criteria=[], bias_ranges=[], bias_weights=[]).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
