"""Main file for generating results for sample ways-pay game."""

import os

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs
from fixed_weights import write_all_or_nothing

FIXED_WEIGHT_MODES = ["max"]  # all-or-nothing modes: weights set exactly, not optimised

if __name__ == "__main__":

    num_threads = 4
    rust_threads = 4
    batching_size = 10000
    compression = True
    profiling = False

    all_sims = {
        "base": int(2e5),
        "ante": int(2e5),
        "bonus": int(1e5),
        "feature": int(2e5),
        "super": int(1e5),
        "mystery": int(1e5),
        "max": int(1e5),
    }
    # optional: python run.py ante   (only re-simulate/optimise the named modes)
    import sys

    chosen = sys.argv[1:] or list(all_sims)
    # SIMS_SCALE=0.01 for a quick smoke run
    scale = float(os.environ.get("SIMS_SCALE", "1"))
    num_sim_args = {m: max(1000, int(all_sims[m] * scale)) for m in chosen}

    run_conditions = {
        "run_sims": os.environ.get("SKIP_SIMS") != "1",  # SKIP_SIMS=1: re-optimise existing books
        "run_optimization": os.environ.get("SKIP_OPT") != "1",
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = chosen

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(
            config, [m for m in target_modes if m not in FIXED_WEIGHT_MODES], rust_threads
        )
        for mode in target_modes:
            if mode in FIXED_WEIGHT_MODES:
                write_all_or_nothing(config, mode)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        custom_keys = [{"symbol": "scatter"}]
        create_stat_sheet(gamestate, custom_keys=custom_keys)

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
