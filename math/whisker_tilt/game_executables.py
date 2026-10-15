"""Whisker Tilt executables: the Tilt Tumble, Edge Keepers, Snowstorms and the feature entries."""

import random

from game_calculations import GameCalculations
from game_config import FREE, SUPER, MYSTERY, MAX_FREE_SPINS
from game_events import (
    tilt_event,
    snowstorm_event,
    settle_board_event,
    keeper_bank_event,
    keepers_init_event,
    mystery_reveal_event,
    crack_meter_event,
    shelf_result_event,
)
from src.calculations.statistics import get_random_outcome
from src.events.events import (
    reveal_event,
    win_info_event,
    set_win_event,
    set_total_event,
    update_tumble_win_event,
    update_freespin_event,
    fs_trigger_event,
    freespin_end_event,
)
from src.events.event_constants import EventConstants


class GameExecutables(GameCalculations):
    """Game specific executable functions."""

    # --- round state -------------------------------------------------------------

    def max_or_nothing(self) -> bool:
        return self.get_current_distribution_conditions()["max_or_nothing"]

    def start_keepers(self, value: int) -> None:
        self.keepers = [value] * 4
        if value:
            keepers_init_event(self)

    def reveal_board(self) -> None:
        """Board drawn from the strips (it lands along the current gravity), then floor coins bank."""
        self.init_lanes()
        reveal_event(self)

    # --- the Tilt Tumble -----------------------------------------------------------

    def quarter_turn(self, cause: str) -> None:
        """Mitten bats the box: gravity rotates clockwise; every 4th turn is a Snowstorm."""
        self.gravity = (self.gravity + 1) % 4
        self.turn += 1
        tilt_event(self, cause)
        if self.turn % 4 == 0:
            self.keepers = [min(self.config.keeper_cap, k * 2) for k in self.keepers]
            snowstorm_event(self)

    def bank_floor_coins(self) -> None:
        """Coins resting on the floor wall go to that wall's keeper; the gaps refill. Repeat."""
        while True:
            coins = self.coins_on_floor()
            if not coins:
                return
            self.keepers[self.gravity] += sum(v for _, _, v in coins)
            keeper_bank_event(self, coins)
            removed = {(r, c) for r, c, _ in coins}
            settle_board_event(self, removed, self.settle(removed), "bank")

    def evaluate_wins(self) -> None:
        self.win_data = self.evaluate_clusters()
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.emit_tumble_win_events()

    def play_cascade(self) -> None:
        """One spin after the reveal: bank, evaluate, and tilt again for as long as clusters win."""
        self.bank_floor_coins()
        self.evaluate_wins()
        while self.win_data["totalWin"] > 0 and not self.wincap_triggered:
            removed = {(p["reel"], p["row"]) for w in self.win_data["wins"] for p in w["positions"]}
            self.quarter_turn("cascade")
            settle_board_event(self, removed, self.settle(removed), "cascade")
            self.bank_floor_coins()
            self.evaluate_wins()

    # --- win events (Off the Shelf shows a crack meter instead of amounts) ----------

    def emit_tumble_win_events(self) -> None:
        if self.win_data["totalWin"] > 0:
            win_info_event(self, include_padding_index=False)
            if not self.max_or_nothing():
                update_tumble_win_event(self)
            self.evaluate_wincap()

    def set_end_tumble_event(self) -> None:
        if self.max_or_nothing():
            crack_meter_event(self)
            return
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)

    def settle_max_or_nothing(self) -> None:
        """Off the Shelf pays the cap or nothing: a round that fell short is zeroed."""
        if not self.max_or_nothing():
            return
        shattered = self.wincap_triggered
        if not shattered:
            self.win_manager.running_bet_win = 0.0
            self.win_manager.basegame_wins = 0.0
            self.win_manager.freegame_wins = 0.0
            self.win_manager.spin_win = 0.0
        shelf_result_event(self, shattered)

    # --- feature entry --------------------------------------------------------------

    def run_freespin_from_base(self, scatter_key: str = "scatter") -> None:
        keys = self.count_special_symbols(scatter_key)
        kind = self.get_current_distribution_conditions()["fs_kind"]
        if kind == "natural":
            kind = SUPER if keys >= self.config.super_trigger else FREE
        self.record({"kind": keys, "symbol": scatter_key, "gametype": self.gametype, "bonus": kind})

        if kind == MYSTERY:
            gift = get_random_outcome(self.config.mystery_gifts)
            self.fs_type, self.tot_fs = gift
        elif kind == SUPER:
            self.fs_type, self.tot_fs = SUPER, self.config.super_spins
        else:
            self.fs_type = FREE
            self.tot_fs = self.config.freespin_triggers[self.gametype][keys]
        fs_trigger_event(self, include_padding_index=False, basegame_trigger=True, freegame_trigger=False)
        if kind == MYSTERY:
            mystery_reveal_event(self, self.fs_type, self.tot_fs)
        self.run_freespin()

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """3+ keys: +3 spins, never past the lifetime cap."""
        extra = min(
            self.config.freespin_triggers[self.gametype][self.count_special_symbols(scatter_key)],
            MAX_FREE_SPINS - self.tot_fs,
        )
        if extra > 0:
            self.tot_fs += extra
            fs_trigger_event(self, include_padding_index=False, freegame_trigger=True, basegame_trigger=False)

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame. Keepers, gravity and turns persist."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.win_data = {"totalWin": 0, "wins": []}

    def end_freespin(self) -> None:
        if not self.max_or_nothing():
            freespin_end_event(self)
            return
        amount = self.config.wincap if self.wincap_triggered else 0
        self.book.add_event(
            {
                "index": len(self.book.events),
                "type": EventConstants.FREE_SPIN_END.value,
                "amount": int(amount * 100),
                "winLevel": self.config.get_win_level(amount, "endFeature"),
            }
        )
