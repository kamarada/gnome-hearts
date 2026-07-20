"""A heuristic AI opponent.

Conceptually modeled on gnome-hearts-0.3.1/scripts/stock_ai.py (prioritize
passing off the Queen/King/Ace of Spades, clear singleton non-heart suits,
avoid taking points when possible, duck under the trick winner otherwise)
but written fresh in idiomatic Python rather than translated line-by-line.
Not meant to be strategically deep -- just competent enough to make a
single-player game against 3 bots actually playable.
"""

from __future__ import annotations

from ..card import Card, Rank, Seat, Suit, QUEEN_OF_SPADES
from ..rules import legal_plays
from ..trick import Trick
from .base import Player

_HIGH_SPADES = (
    QUEEN_OF_SPADES,
    Card(Suit.SPADES, Rank.KING),
    Card(Suit.SPADES, Rank.ACE),
)


def _cards_of_suit(hand: list[Card], suit: Suit) -> list[Card]:
    return [c for c in hand if c.suit == suit]


def _highest_point_card(cards: list[Card]) -> Card | None:
    """Prefer dumping the Queen of Spades, then high spades, then the
    highest heart -- the cards most dangerous to be caught holding."""
    if QUEEN_OF_SPADES in cards:
        return QUEEN_OF_SPADES
    spades_desc = sorted(_cards_of_suit(cards, Suit.SPADES), key=lambda c: c.rank, reverse=True)
    for card in spades_desc:
        if card.rank in (Rank.ACE, Rank.KING):
            return card
    hearts = _cards_of_suit(cards, Suit.HEARTS)
    if hearts:
        return max(hearts, key=lambda c: c.rank)
    point_cards = [c for c in cards if c.points() > 0]
    return max(point_cards, key=lambda c: c.rank) if point_cards else None


class AIPlayer(Player):
    def select_cards(self, hand: list[Card], direction_offset: int) -> list[Card]:
        remaining = list(hand)
        chosen: list[Card] = []

        for high_spade in _HIGH_SPADES:
            if len(chosen) >= 3:
                break
            if high_spade in remaining:
                chosen.append(high_spade)
                remaining.remove(high_spade)

        while len(chosen) < 3:
            singleton = next(
                (
                    _cards_of_suit(remaining, suit)[0]
                    for suit in (Suit.CLUBS, Suit.DIAMONDS)
                    if len(_cards_of_suit(remaining, suit)) == 1
                ),
                None,
            )
            if singleton is not None:
                pick = singleton
            else:
                hearts = _cards_of_suit(remaining, Suit.HEARTS)
                pick = max(hearts, key=lambda c: c.rank) if hearts else max(remaining, key=lambda c: c.rank)
            chosen.append(pick)
            remaining.remove(pick)

        return chosen

    def play_card(
        self,
        hand: list[Card],
        trick: Trick,
        hearts_broken: bool,
        is_first_trick: bool,
        scores_so_far: dict[Seat, int],
    ) -> Card:
        legal = legal_plays(hand, trick, hearts_broken, is_first_trick)
        if len(legal) == 1:
            return legal[0]

        is_leading = trick is None or not trick.plays
        if is_leading:
            non_queen = [c for c in legal if c != QUEEN_OF_SPADES]
            candidates = non_queen if non_queen else legal
            return min(candidates, key=lambda c: c.rank)

        led_suit = trick.led_suit
        same_suit_legal = [c for c in legal if c.suit == led_suit]

        if not same_suit_legal:
            # Void in the led suit: dump the most dangerous card we can.
            dump = _highest_point_card(legal)
            return dump if dump is not None else max(legal, key=lambda c: c.rank)

        winning_rank = max(card.rank for seat, card in trick.plays if card.suit == led_suit)
        lower_cards = [c for c in same_suit_legal if c.rank < winning_rank]
        if lower_cards:
            # Duck as closely under the current winner as possible.
            return max(lower_cards, key=lambda c: c.rank)
        # Forced to win the trick: do so as cheaply as possible.
        return min(same_suit_legal, key=lambda c: c.rank)
