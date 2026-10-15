"""Simulate, optimise and verify all Whisker Tilt bet modes.

    python run.py                    # every mode at full size
    python run.py bonus super        # only the named modes
    SIM_SCALE=0.05 python run.py     # quick smoke run at 5% of the sims
    SKIP_SIMS=1 python run.py        # re-optimise existing books
"""

import os
import sys

from gamestate import GameState
from game_config import GameConfig
from game_optimization import OptimizationSetup
from optimization_program.run_script import OptimizationExecution
from utils.game_analytics.run_analysis import create_stat_sheet
from utils.rgs_verification import execute_all_tests
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":

    num_threads = 4
    rust_threads = 4
    batching_size = 5000  # free-spin books are large; smaller batches keep workers in memory
    compression = True
    profiling = False

    all_sims = {
        "base": int(2e5),
        "ante": int(2e5),
        "feature": int(2e5),
        "bonus": int(1e5),
        "super": int(1e5),
        "mystery": int(1e5),
        "max_or_nothing": int(1e5),
    }
    scale = float(os.environ.get("SIM_SCALE", "1"))
    chosen = sys.argv[1:] or list(all_sims)
    num_sim_args = {m: int(all_sims[m] * scale) for m in chosen}

    run_conditions = {
        "run_sims": os.environ.get("SKIP_SIMS") != "1",
        "run_optimization": True,
        "run_analysis": True,
        "run_format_checks": True,
    }
    target_modes = chosen

    config = GameConfig()
    gamestate = GameState(config)
    if run_conditions["run_optimization"] or run_conditions["run_analysis"]:
        optimization_setup_class = OptimizationSetup(config)

    if run_conditions["run_sims"]:
        create_books(gamestate, config, num_sim_args, batching_size, num_threads, compression, profiling)

    generate_configs(gamestate)

    if run_conditions["run_optimization"]:
        OptimizationExecution().run_all_modes(config, target_modes, rust_threads)
        generate_configs(gamestate)

    if run_conditions["run_analysis"]:
        # The SDK's xlsx sheet assumes every mode has base-game wins, which Off the Shelf
        # never has; analyze.py reports the numbers we need either way.
        try:
            create_stat_sheet(gamestate, custom_keys=[{"symbol": "scatter"}])
        except UnboundLocalError as err:
            print(f"Skipped the xlsx stat sheet ({err}); run analyze.py for the mode summary.")

    if run_conditions["run_format_checks"]:
        execute_all_tests(config)
