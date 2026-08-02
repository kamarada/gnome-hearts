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


def explain_illegal_play(
    hand: list[Card],
    trick: Trick | None,
    hearts_broken: bool,
    is_first_trick: bool,
    card: Card,
) -> str | None:
    """A human-readable reason `card` can't be played right now, or None if
    it's actually legal. Mirrors legal_plays()'s logic, in the same order,
    so the explanation always matches why the card was excluded."""
    if card in legal_plays(hand, trick, hearts_broken, is_first_trick):
        return None

    is_leading = trick is None or not trick.plays

    if is_leading:
        if is_first_trick and TWO_OF_CLUBS in hand:
            return "You must play the two of clubs."
        hand_is_all_hearts = all(c.suit == Suit.HEARTS for c in hand)
        if card.suit == Suit.HEARTS and not hearts_broken and not hand_is_all_hearts:
            return "Hearts have not been broken yet."
    else:
        led_suit = trick.led_suit
        if any(c.suit == led_suit for c in hand) and card.suit != led_suit:
            # Suit names (CLUBS, DIAMONDS, HEARTS, SPADES) are all plural;
            # drop the trailing "s" for a grammatical "play a club/heart/...".
            return f"You must follow suit. Play a {led_suit.name.lower()[:-1]}."

    if is_first_trick and card.points() > 0 and not all(c.points() > 0 for c in hand):
        return "You can't play a point card on the first trick."

    return "You can't play that card right now."
