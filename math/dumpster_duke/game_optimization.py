"""Set conditions/parameters for optimization program program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructFenceBias,
    ConstructConditions,
    verify_optimization_input,
)


class OptimizationSetup:
    """Handle all game mode optimization parameters."""

    def __init__(self, game_config):
        self.game_config = game_config
        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.0075, av_win=60000, search_conditions=60000).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.370, hr=210, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.5875).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.2,
                            "win_range": (1, 2),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.5,
                            "win_range": (10, 20),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.8,
                            "win_range": (2000, 5000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (5000, 50000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                    max_trial_dist=15,
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(3.0, 5.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
            # Ante: cost 1.25, raid hit rate doubled (1 in 105). The raid's average pay stays ~77.7x bet,
            # so its RTP share is 77.7 / (105 * 1.25) = 0.592 and base-game wins carry the rest.
            "ante": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.0075, av_win=60000, search_conditions=60000).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.592, hr=105, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=4.5, rtp=0.3655).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.2,
                            "win_range": (1, 2),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.5,
                            "win_range": (10, 20),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.8,
                            "win_range": (2000, 5000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (5000, 50000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                    max_trial_dist=15,
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(3.0, 5.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
            "bonus": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.006, av_win=60000, search_conditions=60000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.959, hr="x").return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (5000, 50000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[10, 20, 50],
                    test_weights=[0.6, 0.2, 0.2],
                    score_type="rtp",
                    max_trial_dist=15,
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["freegame"],
                    bias_ranges=[(90.0, 150.0)],
                    bias_weights=[0.1],
                ).return_dict(),
            },
            # Feature Spin (5x): raid ~1 in 23, base-game wins carry ~10% of the RTP.
            "feature": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.012, av_win=60000, search_conditions=60000).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.853, hr=23, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=7.0, rtp=0.100).return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.2,
                            "win_range": (1, 2),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "basegame",
                            "scale_factor": 1.5,
                            "win_range": (10, 20),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 0.8,
                            "win_range": (2000, 5000),
                            "probability": 1.0,
                        },
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (5000, 50000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[50, 100, 200],
                    test_weights=[0.3, 0.4, 0.3],
                    score_type="rtp",
                    max_trial_dist=15,
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["basegame"],
                    bias_ranges=[(1.0, 3.0)],
                    bias_weights=[0.5],
                ).return_dict(),
            },
            # Super Raid (250x) and Mystery Bonus (100x): bonus buys like "bonus".
            "super": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.012, av_win=60000, search_conditions=60000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.953, hr="x").return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (5000, 50000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[10, 20, 50],
                    test_weights=[0.6, 0.2, 0.2],
                    score_type="rtp",
                    max_trial_dist=15,
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["freegame"],
                    bias_ranges=[(200.0, 300.0)],
                    bias_weights=[0.1],
                ).return_dict(),
            },
            "mystery": {
                "conditions": {
                    "wincap": ConstructConditions(rtp=0.006, av_win=60000, search_conditions=60000).return_dict(),
                    "freegame": ConstructConditions(rtp=0.959, hr="x").return_dict(),
                },
                "scaling": ConstructScaling(
                    [
                        {
                            "criteria": "freegame",
                            "scale_factor": 1.2,
                            "win_range": (5000, 50000),
                            "probability": 1.0,
                        },
                    ]
                ).return_dict(),
                "parameters": ConstructParameters(
                    num_show=5000,
                    num_per_fence=10000,
                    min_m2m=4,
                    max_m2m=8,
                    pmb_rtp=1.0,
                    sim_trials=5000,
                    test_spins=[10, 20, 50],
                    test_weights=[0.6, 0.2, 0.2],
                    score_type="rtp",
                    max_trial_dist=15,
                ).return_dict(),
                "distribution_bias": ConstructFenceBias(
                    applied_criteria=["freegame"],
                    bias_ranges=[(90.0, 150.0)],
                    bias_weights=[0.1],
                ).return_dict(),
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
