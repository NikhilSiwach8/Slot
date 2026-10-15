from game_override import GameStateOverride
from game_config import SUPER


class GameState(GameStateOverride):
    """Gamestate for a single spin"""

    def run_spin(self, sim: int, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.start_keepers(self.get_current_distribution_conditions()["base_keeper"])
            self.draw_board(emit_event=False)
            self.reveal_board()
            self.play_cascade()
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if not self.wincap_triggered and self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.settle_max_or_nothing()
            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        self.start_keepers(self.config.super_start_keeper if self.fs_type == SUPER else 0)
        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            # The Paw: Mitten turns the box before every free spin drops.
            self.quarter_turn("paw")
            self.draw_board(emit_event=False)
            self.reveal_board()
            self.play_cascade()
            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if not self.wincap_triggered and self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
