"""Dumpster Duke calculations"""

from src.calculations.cluster import Cluster
from src.executables.executables import Executables


class GameCalculations(Executables):
    """Game specific calculations."""

    def get_board_multipliers(self, multiplier_key: str = "multiplier"):
        """Return (sum of bottle caps on screen, positions/values). Sum is 0 when none."""
        board_mult = 0
        mult_info = []
        for reel, _ in enumerate(self.board):
            for row, _ in enumerate(self.board[reel]):
                if self.board[reel][row].check_attribute(multiplier_key):
                    value = self.board[reel][row].get_attribute(multiplier_key)
                    board_mult += value
                    mult_info.append({"reel": reel, "row": row, "value": value})
        return board_mult, mult_info

    def evaluate_clusters_with_spots(self, clusters: dict) -> dict:
        """Cluster pays: every cluster of 5+ touching like symbols pays its size's value,
        multiplied by the Haunted Spots it sits on (sum of the x2..x128 spot values under
        it; 1 when it covers none). Winning symbols are marked to explode."""
        wins, total = [], 0.0
        for sym in clusters:
            for cluster in clusters[sym]:
                size = len(cluster)
                if (size, sym) not in self.config.paytable:
                    continue
                spot_mult = sum(v for v in (self.haunted_spots[r][c] for r, c in cluster) if v >= 2)
                spot_mult = max(spot_mult, 1)
                base = self.config.paytable[(size, sym)]
                win = base * spot_mult
                total += win
                positions = [{"reel": r, "row": c} for r, c in cluster]
                centre = Cluster.get_central_cluster_position(positions)
                wins.append(
                    {
                        "symbol": sym,
                        "clusterSize": size,
                        "win": win,
                        "positions": positions,
                        "meta": {
                            "globalMult": 1,
                            "clusterMult": spot_mult,
                            "winWithoutMult": base,
                            "overlay": {"reel": centre[0], "row": centre[1]},
                        },
                    }
                )
                for r, c in cluster:
                    self.board[r][c].explode = True
        return {"totalWin": total, "wins": wins}
