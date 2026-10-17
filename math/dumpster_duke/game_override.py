import random

from game_events import send_mystery_reveal_event
from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome
from src.events.events import reveal_event, update_global_mult_event, fs_trigger_event


class GameStateOverride(GameExecutables):
    """Game-specific overrides of the universal state functions."""

    def reset_book(self):
        super().reset_book()
        self.tumble_win = 0
        self.loot_bag = 0
        # base game: Haunted Spots clear every spin
        self.reset_haunted_spots()

    def reset_fs_spin(self):
        super().reset_fs_spin()
        self.global_multiplier = 1
        self.loot_bag = 0
        # the Haunted Raid starts with a clear grid; spots then stay for the whole raid
        self.reset_haunted_spots()
        # Super Raid / Mystery Bonus: the Loot Bag can start the raid already filled
        start = getattr(self, "pending_loot_bag", 0)
        self.pending_loot_bag = 0
        if start > 0:
            self.loot_bag = start
            self.global_multiplier = start
            update_global_mult_event(self)

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Set the raid's spins. Mystery Bonus draws spins and starting Loot Bag at random."""
        conditions = self.get_current_distribution_conditions()
        self.pending_loot_bag = 0
        if self.gametype == self.config.basegame_type and "mystery_spins" in conditions:
            self.tot_fs = get_random_outcome(conditions["mystery_spins"])
            self.pending_loot_bag = get_random_outcome(conditions["mystery_loot_bag"])
            send_mystery_reveal_event(self, self.tot_fs, self.pending_loot_bag)
            fs_trigger_event(self, basegame_trigger=True, freegame_trigger=False)
            return
        super().update_freespin_amount(scatter_key)
        if self.gametype == self.config.basegame_type and "start_loot_bag" in conditions:
            self.pending_loot_bag = get_random_outcome(conditions["start_loot_bag"])

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Feature Spin tease (3 Golden Trash Cans) and guaranteed Bottle Caps, then reveal."""
        conditions = self.get_current_distribution_conditions()
        tease = conditions.get("tease_scatters", 0)
        if (
            tease
            and self.gametype == self.config.basegame_type
            and not conditions["force_freegame"]
        ):
            self.force_special_board(trigger_symbol, tease)
        else:
            super().draw_board(emit_event=False, trigger_symbol=trigger_symbol)
        if self.gametype in conditions.get("guarantee_cap", ()):
            self.ensure_bottle_cap()
        if emit_event:
            reveal_event(self)

    def ensure_bottle_cap(self) -> None:
        """Put a Bottle Cap on a random non-special position if none landed."""
        if len(self.special_syms_on_board["multiplier"]) > 0:
            return
        spots = [
            (reel, row)
            for reel in range(len(self.board))
            for row in range(len(self.board[reel]))
            if not self.board[reel][row].defn.special
        ]
        reel, row = random.choice(spots)
        self.board[reel][row] = self.create_symbol("M")
        self.get_special_symbols_on_board()

    def assign_special_sym_function(self):
        self.special_symbol_functions = {"M": [self.assign_mult_property]}

    def assign_mult_property(self, symbol):
        """Use betmode conditions to assign a bottle-cap value to multiplier symbols."""
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["mult_values"][self.gametype]
        )
        symbol.assign_attribute({"multiplier": multiplier_value})

    def check_game_repeat(self):
        """Verify final win matches required betmode conditions."""
        if self.repeat == False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

    def check_repeat(self):
        """A Midnight Raid must always pay something: redraw bonus rounds that win 0."""
        super().check_repeat()
        if not self.repeat and self.criteria == "freegame" and self.final_win == 0:
            self.repeat = True
        # Max or Nothing is a single spin: never show a raid-triggering board
        if (
            not self.repeat
            and self.get_current_distribution_conditions().get("max_or_nothing")
            and self.count_special_symbols("scatter") >= min(self.config.freespin_triggers[self.gametype])
        ):
            self.repeat = True
