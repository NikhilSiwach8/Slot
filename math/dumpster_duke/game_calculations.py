"""Dumpster Duke calculations"""

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
