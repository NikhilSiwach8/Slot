"""Dumpster Duke executables: bottle-cap multipliers and the Loot Bag."""

from copy import copy

from game_calculations import GameCalculations
from game_events import send_haunted_spots_event, send_max_boost_event, send_mult_info_event
from src.events.events import (
    set_win_event,
    set_total_event,
    update_tumble_win_event,
    update_global_mult_event,
    update_freespin_event,
)


class GameExecutables(GameCalculations):
    """Game specific executable functions."""

    def set_end_tumble_event(self):
        """After all tumbles, apply bottle caps.

        Base game: a winning spin is multiplied by the sum of caps on screen.
        Free spins: caps on screen are added to the persistent Loot Bag, and a winning
        spin is multiplied by the whole Loot Bag total.
        """
        base_tumble_win = copy(self.win_manager.spin_win)
        if self.get_current_distribution_conditions().get("max_or_nothing"):
            self.apply_max_cap(base_tumble_win)
            return
        if base_tumble_win > 0:
            board_sum, mult_info = self.get_board_multipliers()
            if self.gametype == self.config.freegame_type:
                if board_sum > 0:
                    self.loot_bag += board_sum
                    self.global_multiplier = self.loot_bag
                    update_global_mult_event(self)
                applied_mult = self.loot_bag
            else:
                applied_mult = board_sum

            if applied_mult > 0:
                self.win_manager.set_spin_win(base_tumble_win * applied_mult)
                send_mult_info_event(self, applied_mult, mult_info, base_tumble_win, self.win_manager.spin_win)
                update_tumble_win_event(self)
                self.evaluate_wincap()

        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)

    def apply_max_cap(self, base_tumble_win):
        """Max or Nothing: after the tumbles, the MAX cap(s) on screen lift any win to this
        round's prize: the max win or the MAX BOOST prize."""
        _, mult_info = self.get_board_multipliers()
        if base_tumble_win > 0 and mult_info:
            max_cap = mult_info[0]["value"]
            prize = self.get_current_distribution_conditions().get("max_prize") or self.get_current_betmode().get_wincap()
            self.win_manager.set_spin_win(base_tumble_win * max_cap)
            send_mult_info_event(self, max_cap, mult_info, base_tumble_win, self.win_manager.spin_win)
            self.win_manager.set_spin_win(prize)
            update_tumble_win_event(self)
            send_max_boost_event(self, base_tumble_win, prize)
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)

    def get_cluster_wins_update(self):
        """Evaluate cluster wins (with Haunted Spot multipliers). The Candy Caps are applied
        once at the end of the spin, not per tumble."""
        from src.calculations.cluster import Cluster

        clusters = Cluster.get_clusters(self.board, "wild")
        self.win_data = self.evaluate_clusters_with_spots(clusters)
        Cluster.record_cluster_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])

    def reset_haunted_spots(self):
        """0 = clear, 1 = haunted (no multiplier yet), 2..HAUNTED_SPOT_MAX = multiplier."""
        self.haunted_spots = [[0] * self.config.num_rows[r] for r in range(self.config.num_reels)]

    def update_haunted_spots(self):
        """Every position a winning symbol explodes from becomes haunted; a haunted spot that
        wins again becomes x2, and doubles on every further win there (up to the cap)."""
        if self.win_data["totalWin"] <= 0:
            return
        for win in self.win_data["wins"]:
            for pos in win["positions"]:
                v = self.haunted_spots[pos["reel"]][pos["row"]]
                self.haunted_spots[pos["reel"]][pos["row"]] = 1 if v == 0 else min(max(2, v * 2), self.config.haunted_spot_max)
        send_haunted_spots_event(self)

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame. The Loot Bag persists."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.tumblewin_mult = 0
        self.win_data = {}
