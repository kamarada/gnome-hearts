"""Card, Suit, Rank and Seat primitives. No gi imports allowed in this module."""

from __future__ import annotations

import dataclasses
import enum


class Suit(enum.IntEnum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3


# aisleriot/cards/anglo.svg element ids use the singular suit name.
_SUIT_SVG_NAMES = {
    Suit.CLUBS: "club",
    Suit.DIAMONDS: "diamond",
    Suit.HEARTS: "heart",
    Suit.SPADES: "spade",
}


class Rank(enum.IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14  # aces are dealt high, matching the original game's convention


_RANK_SVG_NAMES = {
    Rank.ACE: "1",
    Rank.JACK: "jack",
    Rank.QUEEN: "queen",
    Rank.KING: "king",
}

_RANK_DISPLAY_NAMES = {
    Rank.ACE: "Ace",
    Rank.JACK: "Jack",
    Rank.QUEEN: "Queen",
    Rank.KING: "King",
}


class Seat(enum.IntEnum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


HUMAN_SEAT = Seat.SOUTH

SEATS = (Seat.NORTH, Seat.EAST, Seat.SOUTH, Seat.WEST)


@dataclasses.dataclass(frozen=True, order=True)
class Card:
    suit: Suit
    rank: Rank

    def points(self) -> int:
        """Standard ruleset scoring: each heart is 1 point, the Queen of
        Spades is 13 points, everything else is worth nothing."""
        if self.suit == Suit.HEARTS:
            return 1
        if self.suit == Suit.SPADES and self.rank == Rank.QUEEN:
            return 13
        return 0

    def svg_element_id(self) -> str:
        rank_part = _RANK_SVG_NAMES.get(self.rank, str(int(self.rank)))
        return f"{_SUIT_SVG_NAMES[self.suit]}_{rank_part}"

    def __str__(self) -> str:
        rank_part = _RANK_DISPLAY_NAMES.get(self.rank, str(int(self.rank)))
        return f"{rank_part} of {self.suit.name.capitalize()}"


TWO_OF_CLUBS = Card(Suit.CLUBS, Rank.TWO)
QUEEN_OF_SPADES = Card(Suit.SPADES, Rank.QUEEN)
