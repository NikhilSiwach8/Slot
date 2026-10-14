"""Quick per-criteria profiler: python profile_criteria.py <mode> <criteria> <n>
Prints time per sim, repeat counts, and payout stats (no files written)."""
import sys, time, statistics
from gamestate import GameState
from game_config import GameConfig
from src.wins.win_manager import WinManager

mode, crit, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
config = GameConfig()
gs = GameState(config)
bm = [b for b in config.bet_modes if b._name == mode][0]
gs.win_manager = WinManager(config.basegame_type, config.freegame_type, bm._wincap)
gs.library, gs.recorded_events, gs.betmode = {}, {}, mode
gs.criteria = crit
wins, reps, fs = [], [], 0
t = time.time()
for sim in range(n):
    gs.repeat_count = 0
    gs.run_spin(sim)
    wins.append(gs.final_win)
    reps.append(gs.repeat_count)
dt = time.time() - t
print(f"{mode}/{crit}: {dt/n*1000:.1f} ms/sim, mean repeats {statistics.mean(reps):.1f}, max {max(reps)}")
print(f"  mean win {statistics.mean(wins):.3f}  hit {sum(w>0 for w in wins)/n:.3f}  max {max(wins)}")
buckets = [(0, 100), (100, 500), (500, 2000), (2000, 5000), (5000, 10000), (10000, 1e9)]
print("  raw counts:", {f"{lo:g}-{hi:g}": sum(lo <= w < hi for w in wins) for lo, hi in buckets})
