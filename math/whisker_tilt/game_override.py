from game_executables import GameExecutables
from game_calculations import DOWN
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """Game-specific overrides of the universal state functions."""

    def reset_book(self):
        super().reset_book()
        self.gravity = DOWN
        self.turn = 0
        self.keepers = [0, 0, 0, 0]
        self.fs_type = None

    def reset_fs_spin(self):
        super().reset_fs_spin()
        self.gravity = DOWN
        self.turn = 0
        self.keepers = [0, 0, 0, 0]

    def assign_special_sym_function(self):
        self.special_symbol_functions = {"C": [self.assign_coin_value]}

    def assign_coin_value(self, symbol):
        """Snowflake Coin values come from the betmode conditions."""
        value = get_random_outcome(self.get_current_distribution_conditions()["mult_values"][self.gametype])
        symbol.assign_attribute({"multiplier": value})

    def check_repeat(self):
        super().check_repeat()
        if not self.repeat:
            # A bought or triggered bonus always pays something, and "basegame" books are wins.
            if self.criteria in ("freegame", "basegame") and self.final_win == 0:
                self.repeat = True
