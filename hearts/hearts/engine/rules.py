"""Pure, stateless functions encoding the Standard ruleset.

The four "gentleman's rules" toggles the original game exposed
(clubs_lead, hearts_break, no_blood, queen_breaks_hearts) are all hardcoded
to their default-on values here, matching gnome-hearts-0.3.1's shipped
defaults. A future ruleset-configuration feature would parameterize these
functions rather than replace them.
"""

from __future__ import annotations

from typing import Iterable

from .card import Card, Seat, Suit, TWO_OF_CLUBS
from .trick import Trick

# Passing direction offsets by 1-based round number, cycling every 4 rounds:
# left, across, right, hold.
_PASS_CYCLE = (1, 2, 3, 0)


def pass_offset(round_number: int) -> int:
    return _PASS_CYCLE[(round_number - 1) % 4]


def pass_target(seat: Seat, round_number: int) -> Seat | None:
    offset = pass_offset(round_number)
    if offset == 0:
        return None
    return Seat((seat + offset) % 4)


def leader_of_first_trick(hands: dict[Seat, list[Card]]) -> Seat:
    """The player holding the two of clubs leads the first trick of a round."""
    for seat, hand in hands.items():
        if TWO_OF_CLUBS in hand:
            return seat
    raise ValueError("no seat holds the two of clubs")


def is_hearts_broken(cards_played_so_far: Iterable[Card]) -> bool:
    """Hearts are broken once any point card (a heart, or the Queen of
    Spades, since queen_breaks_hearts defaults on) has been played."""
    return any(card.points() > 0 for card in cards_played_so_far)


def legal_plays(
    hand: list[Card],
    trick: Trick | None,
    hearts_broken: bool,
    is_first_trick: bool,
) -> list[Card]:
    """The subset of `hand` that may legally be played right now."""
    is_leading = trick is None or not trick.plays

    if is_leading:
        if is_first_trick and TWO_OF_CLUBS in hand:
            return [TWO_OF_CLUBS]
        candidates = list(hand)
        hand_is_all_hearts = all(c.suit == Suit.HEARTS for c in hand)
        if not hearts_broken and not hand_is_all_hearts:
            candidates = [c for c in candidates if c.suit != Suit.HEARTS]
    else:
        led_suit = trick.led_suit
        same_suit = [c for c in hand if c.suit == led_suit]
        candidates = same_suit if same_suit else list(hand)

    if is_first_trick and not all(c.points() > 0 for c in hand):
        pointless = [c for c in candidates if c.points() == 0]
        if pointless:
            candidates = pointless
        # else every remaining legal candidate is a point card (e.g. the
        # only cards left in the led suit are hearts) -- forced, allow it.

    return candidates
