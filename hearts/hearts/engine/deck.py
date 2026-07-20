"""Deck construction and dealing."""

from __future__ import annotations

import random

from .card import Card, Rank, Seat, Suit, SEATS


def standard_deck() -> list[Card]:
    """A full 52-card deck, no jokers."""
    return [Card(suit, rank) for suit in Suit for rank in Rank]


def deal(rng: random.Random | None = None) -> dict[Seat, list[Card]]:
    """Shuffle a standard deck and deal 13 cards to each of the 4 seats."""
    rng = rng or random.Random()
    deck = standard_deck()
    rng.shuffle(deck)
    hands: dict[Seat, list[Card]] = {}
    for i, seat in enumerate(SEATS):
        hands[seat] = sorted(deck[i * 13 : (i + 1) * 13])
    return hands
