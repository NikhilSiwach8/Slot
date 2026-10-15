"""Optimizer targets for the four Whisker Tilt buy modes (RTP 96.5% each).

Base, Catnip and Paw Spins are weighted by natural_weights.py instead."""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructFenceBias,
    ConstructConditions,
    verify_optimization_input,
)

RTP = 0.965


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
        # base, ante and feature are weighted by natural_weights.py, not the optimizer.
        self.game_config.opt_params = {
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
