"""A single trick (one card played by each of the 4 seats)."""

from __future__ import annotations

import dataclasses

from .card import Card, Seat, Suit, SEATS


@dataclasses.dataclass
class Trick:
    leader: Seat
    plays: list[tuple[Seat, Card]] = dataclasses.field(default_factory=list)

    @property
    def led_suit(self) -> Suit | None:
        if not self.plays:
            return None
        return self.plays[0][1].suit

    def is_complete(self) -> bool:
        return len(self.plays) == 4

    def cards(self) -> list[Card]:
        return [card for _, card in self.plays]

    def seats_played(self) -> set[Seat]:
        return {seat for seat, _ in self.plays}

    def play(self, seat: Seat, card: Card) -> None:
        self.plays.append((seat, card))

    def next_to_play(self) -> Seat | None:
        if self.is_complete():
            return None
        played = self.seats_played()
        # Turn order is fixed seating order starting from the leader.
        start = SEATS.index(self.leader)
        for offset in range(4):
            seat = SEATS[(start + offset) % 4]
            if seat not in played:
                return seat
        return None

    def winner(self) -> Seat | None:
        if not self.is_complete():
            return None
        led = self.led_suit
        winning_seat, winning_card = self.plays[0]
        for seat, card in self.plays[1:]:
            if card.suit == led and card.rank > winning_card.rank:
                winning_seat, winning_card = seat, card
        return winning_seat
