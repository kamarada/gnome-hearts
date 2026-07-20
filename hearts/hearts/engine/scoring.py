"""Round scoring, including shoot-the-moon and shoot-the-sun."""

from __future__ import annotations

from .card import Card, Seat, SEATS

MOON_POINTS = 26  # all 13 hearts (13) + the Queen of Spades (13)
SUN_CARD_COUNT = 52  # every card in the deck, i.e. every trick of the round


def score_round(tricks_taken: dict[Seat, list[Card]]) -> dict[Seat, int]:
    """Per-seat score delta for a completed round."""
    raw_points = {seat: sum(c.points() for c in tricks_taken.get(seat, [])) for seat in SEATS}
    card_counts = {seat: len(tricks_taken.get(seat, [])) for seat in SEATS}

    sun_shooter = next((seat for seat in SEATS if card_counts[seat] == SUN_CARD_COUNT), None)
    if sun_shooter is not None:
        return {seat: (-2 * MOON_POINTS if seat == sun_shooter else 0) for seat in SEATS}

    moon_shooter = next((seat for seat in SEATS if raw_points[seat] == MOON_POINTS), None)
    if moon_shooter is not None:
        return {seat: (-MOON_POINTS if seat == moon_shooter else 0) for seat in SEATS}

    return raw_points
