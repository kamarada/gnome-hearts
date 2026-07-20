"""The narrow interface every seat-controller (human adapter or AI) implements."""

from __future__ import annotations

import abc

from ..card import Card, Seat
from ..trick import Trick


class Player(abc.ABC):
    def __init__(self, seat: Seat):
        self.seat = seat

    @abc.abstractmethod
    def select_cards(self, hand: list[Card], direction_offset: int) -> list[Card]:
        """Return exactly 3 cards from `hand` to pass this round."""

    @abc.abstractmethod
    def play_card(
        self,
        hand: list[Card],
        trick: Trick,
        hearts_broken: bool,
        is_first_trick: bool,
        scores_so_far: dict[Seat, int],
    ) -> Card:
        """Return one legal card from `hand` to play on `trick`."""

    def on_trick_complete(self, trick: Trick, winner: Seat) -> None:
        """Optional hook, called for every seat after a trick completes."""

    def on_round_complete(self, scores: dict[Seat, int]) -> None:
        """Optional hook, called for every seat after a round completes."""
