BOARD_MULT_INFO = "boardMultiplierInfo"


def send_mult_info_event(gamestate, board_mult: int, mult_info: dict, base_win: float, updatedWin: float):
    multiplier_info, winInfo = {}, {}
    multiplier_info["positions"] = []
    if gamestate.config.include_padding:
        for m in range(len(mult_info)):
            multiplier_info["positions"].append(
                {"reel": mult_info[m]["reel"], "row": mult_info[m]["row"] + 1, "multiplier": mult_info[m]["value"]}
            )
    else:
        for m in range(mult_info):
            multiplier_info["positions"].append(
                {"reel": mult_info[m]["reel"], "row": mult_info[m]["row"], "multiplier": mult_info[m]["value"]}
            )

    winInfo["tumbleWin"] = int(round(min(base_win, gamestate.config.wincap) * 100))
    winInfo["boardMult"] = board_mult
    winInfo["totalWin"] = int(round(min(updatedWin, gamestate.config.wincap) * 100))

    assert round(updatedWin, 1) == round(base_win * board_mult, 1)
    event = {
        "index": len(gamestate.book.events),
        "type": BOARD_MULT_INFO,
        "multInfo": multiplier_info,
        "winInfo": winInfo,
    }
    gamestate.book.add_event(event)


MYSTERY_REVEAL = "mysteryReveal"


def send_mystery_reveal_event(gamestate, spins: int, loot_bag: int):
    """Mystery Bonus: the chest reveals the raid's free spins and starting Loot Bag."""
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": MYSTERY_REVEAL,
            "spins": spins,
            "lootBag": loot_bag,
        }
    )


MAX_BOOST = "maxBoost"


def send_max_boost_event(gamestate, spin_win: float, prize: float):
    """Max or Nothing: the spin won, so its win is lifted to the mode's max win."""
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": MAX_BOOST,
            "fromWin": int(round(spin_win * 100)),
            "toWin": int(round(prize * 100)),
        }
    )


HAUNTED_SPOTS = "hauntedSpots"


def send_haunted_spots_event(gamestate):
    """The Haunted Spots grid after a tumble's wins: per reel, per visible row (no padding),
    0 = clear, 1 = haunted, 2+ = multiplier."""
    gamestate.book.add_event(
        {
            "index": len(gamestate.book.events),
            "type": HAUNTED_SPOTS,
            "spots": [list(reel) for reel in gamestate.haunted_spots],
        }
    )
