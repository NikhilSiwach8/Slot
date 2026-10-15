"""Whisker Tilt calculations: gravity lanes, settling, coin banking and wall-multiplied clusters."""

import random

from src.executables.executables import Executables

DOWN, LEFT, UP, RIGHT = range(4)
SOUTH, WEST, NORTH, EAST = range(4)  # the wall each gravity direction falls onto


class GameCalculations(Executables):
    """Game specific calculations."""

    def lane_cells(self, gravity: int, lane: int) -> list:
        """Cells of one lane, ordered from the wall symbols enter at to the floor wall."""
        n = self.config.num_reels
        if gravity == DOWN:
            return [(lane, row) for row in range(n)]
        if gravity == UP:
            return [(lane, row) for row in reversed(range(n))]
        if gravity == LEFT:
            return [(reel, lane) for reel in reversed(range(n))]
        return [(reel, lane) for reel in range(n)]

    def on_wall(self, reel: int, row: int, wall: int) -> bool:
        last = self.config.num_reels - 1
        return (row == last, reel == 0, row == 0, reel == last)[wall]

    def init_lanes(self) -> None:
        """Strip pointers for refills. Falling down continues the drawn reels upward, exactly like
        a normal tumble; the other directions start from random stops on the same strips."""
        self.lane_pos = [[0] * self.config.num_reels for _ in range(4)]
        for lane in range(self.config.num_reels):
            self.lane_pos[DOWN][lane] = self.reel_positions[lane]
            for d in (LEFT, UP, RIGHT):
                self.lane_pos[d][lane] = random.randrange(len(self.reelstrip[lane]))

    def settle(self, removed: set) -> list:
        """Remove cells, slide survivors toward the floor, refill from the opposite wall.
        Returns the positions of the new symbols."""
        new_positions = []
        for lane in range(self.config.num_reels):
            cells = self.lane_cells(self.gravity, lane)
            survivors = [self.board[r][c] for r, c in cells if (r, c) not in removed]
            strip = self.reelstrip[lane]
            new_syms = []
            for _ in range(len(cells) - len(survivors)):
                pos = (self.lane_pos[self.gravity][lane] - 1) % len(strip)
                self.lane_pos[self.gravity][lane] = pos
                new_syms.insert(0, self.create_symbol(strip[pos]))
            for (r, c), sym in zip(cells, new_syms + survivors):
                self.board[r][c] = sym
            new_positions += cells[: len(new_syms)]
        self.get_special_symbols_on_board()
        return new_positions

    def coins_on_floor(self) -> list:
        return [
            (r, c, self.board[r][c].get_attribute("multiplier"))
            for r in range(self.config.num_reels)
            for c in range(self.config.num_rows[r])
            if self.board[r][c].name == "C" and self.on_wall(r, c, self.gravity)
        ]

    def find_clusters(self) -> list:
        """(symbol, [(reel, row), ...]) for every paying cluster on the board."""
        n_reels, seen, found = self.config.num_reels, set(), []
        for reel in range(n_reels):
            for row in range(self.config.num_rows[reel]):
                name = self.board[reel][row].name
                if (reel, row) in seen or (self.config.min_cluster, name) not in self.config.paytable:
                    continue
                seen.add((reel, row))
                stack, group = [(reel, row)], []
                while stack:
                    r, c = stack.pop()
                    group.append((r, c))
                    for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                        if (
                            0 <= nr < n_reels
                            and 0 <= nc < self.config.num_rows[nr]
                            and (nr, nc) not in seen
                            and self.board[nr][nc].name == name
                        ):
                            seen.add((nr, nc))
                            stack.append((nr, nc))
                if len(group) >= self.config.min_cluster:
                    found.append((name, sorted(group)))
        return found

    def evaluate_clusters(self) -> dict:
        """Each cluster pays paytable x max(1, sum of the keepers on every wall it touches)."""
        wins, total = [], 0.0
        for sym, group in self.find_clusters():
            walls = sorted({w for r, c in group for w in range(4) if self.on_wall(r, c, w)})
            mult = max(1, sum(self.keepers[w] for w in walls))
            base = self.config.paytable[(len(group), sym)]
            win = base * mult
            total += win
            centre = (
                int(round(sum(r for r, _ in group) / len(group))),
                int(round(sum(c for _, c in group) / len(group))),
            )
            wins.append(
                {
                    "symbol": sym,
                    "clusterSize": len(group),
                    "win": win,
                    "positions": [{"reel": r, "row": c} for r, c in group],
                    "meta": {
                        "globalMult": 1,
                        "clusterMult": mult,
                        "walls": walls,
                        "winWithoutMult": base,
                        "overlay": {"reel": centre[0], "row": centre[1]},
                    },
                }
            )
        return {"totalWin": total, "wins": wins}
