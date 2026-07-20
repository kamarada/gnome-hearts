"""Tag/adapter for the human-controlled seat.

HeartsGame never calls select_cards()/play_card() for the human seat --
the UI calls HeartsGame.submit_pass()/submit_play() directly instead. This
class exists so the human seat still satisfies the Player interface
uniformly (e.g. for on_trick_complete()/on_round_complete() hooks a future
UI might use to drive animations) and so game.py can tell seats apart by
type without a separate "is_human" flag.
"""

from __future__ import annotations

from ..card import Card, Seat
from ..trick import Trick
from .base import Player


class HumanPlayer(Player):
    def select_cards(self, hand: list[Card], direction_offset: int) -> list[Card]:
        raise NotImplementedError(
            "HumanPlayer selections come from the UI via HeartsGame.submit_pass()"
        )

    def play_card(
        self,
        hand: list[Card],
        trick: Trick,
        hearts_broken: bool,
        is_first_trick: bool,
        scores_so_far: dict[Seat, int],
    ) -> Card:
        raise NotImplementedError(
            "HumanPlayer plays come from the UI via HeartsGame.submit_play()"
        )
