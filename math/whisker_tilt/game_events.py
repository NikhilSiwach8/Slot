"""Whisker Tilt book events (on top of the SDK's reveal / winInfo / freeSpin events).

Positions are screen coordinates: reel = column (0 = West), row = 0 at the North wall.
Gravity and walls use the same index: 0 down/South, 1 left/West, 2 up/North, 3 right/East.
"""

from src.events.events import json_ready_sym

TILT = "tilt"
SNOWSTORM = "snowstorm"
SETTLE_BOARD = "settleBoard"
KEEPER_BANK = "keeperBank"
KEEPERS_INIT = "keepersInit"
MYSTERY_REVEAL = "mysteryReveal"
CRACK_METER = "crackMeter"
SHELF_RESULT = "shelfResult"

GRAVITY_NAMES = ["down", "left", "up", "right"]
WALL_NAMES = ["south", "west", "north", "east"]


def _add(gamestate, event_type, **fields):
    gamestate.book.add_event({"index": len(gamestate.book.events), "type": event_type, **fields})


def tilt_event(gamestate, cause):
    """Mitten turns the box a quarter turn: cause is "cascade" (after a win) or "paw" (free-spin start)."""
    _add(gamestate, TILT, gravity=GRAVITY_NAMES[gamestate.gravity], turn=gamestate.turn, cause=cause)


def snowstorm_event(gamestate):
    _add(gamestate, SNOWSTORM, turn=gamestate.turn, keepers=list(gamestate.keepers))


def settle_board_event(gamestate, removed, new_positions, cause):
    """Removed cells are gone, survivors slid toward the floor (the client replays the slide from
    `removed` + `gravity`), and new symbols fell in from the far wall at `newSymbols`."""
    attrs = list(gamestate.config.special_symbols.keys())
    _add(
        gamestate,
        SETTLE_BOARD,
        cause=cause,
        gravity=GRAVITY_NAMES[gamestate.gravity],
        removed=[{"reel": r, "row": c} for r, c in sorted(removed)],
        newSymbols=[
            {"reel": r, "row": c, **json_ready_sym(gamestate.board[r][c], attrs)} for r, c in new_positions
        ],
    )


def keeper_bank_event(gamestate, coins):
    _add(
        gamestate,
        KEEPER_BANK,
        wall=WALL_NAMES[gamestate.gravity],
        coins=[{"reel": r, "row": c, "value": v} for r, c, v in coins],
        keepers=list(gamestate.keepers),
    )


def keepers_init_event(gamestate):
    _add(gamestate, KEEPERS_INIT, keepers=list(gamestate.keepers))


def mystery_reveal_event(gamestate, kind, spins):
    _add(gamestate, MYSTERY_REVEAL, kind=kind, spins=spins)


def crack_meter_event(gamestate):
    """Off the Shelf: progress toward the 10,000x cap, shown instead of win amounts."""
    progress = min(1.0, gamestate.win_manager.running_bet_win / gamestate.config.wincap)
    _add(gamestate, CRACK_METER, progress=round(progress, 4))


def shelf_result_event(gamestate, shattered):
    _add(gamestate, SHELF_RESULT, shattered=shattered)
