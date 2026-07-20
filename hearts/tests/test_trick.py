import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hearts.engine.card import Card, Rank, Seat, Suit
from hearts.engine.trick import Trick


class TrickTest(unittest.TestCase):
    def test_led_suit_is_set_by_first_play(self):
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, Card(Suit.CLUBS, Rank.TWO))
        self.assertEqual(trick.led_suit, Suit.CLUBS)

    def test_led_suit_is_none_before_any_play(self):
        trick = Trick(leader=Seat.NORTH)
        self.assertIsNone(trick.led_suit)

    def test_winner_is_highest_card_of_led_suit_only(self):
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, Card(Suit.CLUBS, Rank.TWO))
        trick.play(Seat.EAST, Card(Suit.HEARTS, Rank.ACE))  # off-suit, can't win
        trick.play(Seat.SOUTH, Card(Suit.CLUBS, Rank.KING))
        trick.play(Seat.WEST, Card(Suit.CLUBS, Rank.FIVE))
        self.assertEqual(trick.winner(), Seat.SOUTH)

    def test_winner_is_none_until_trick_is_complete(self):
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, Card(Suit.CLUBS, Rank.TWO))
        self.assertIsNone(trick.winner())

    def test_next_to_play_follows_seating_order_from_leader(self):
        trick = Trick(leader=Seat.EAST)
        self.assertEqual(trick.next_to_play(), Seat.EAST)
        trick.play(Seat.EAST, Card(Suit.CLUBS, Rank.TWO))
        self.assertEqual(trick.next_to_play(), Seat.SOUTH)
        trick.play(Seat.SOUTH, Card(Suit.CLUBS, Rank.THREE))
        self.assertEqual(trick.next_to_play(), Seat.WEST)

    def test_next_to_play_is_none_once_complete(self):
        trick = Trick(leader=Seat.NORTH)
        for seat, rank in zip(
            [Seat.NORTH, Seat.EAST, Seat.SOUTH, Seat.WEST],
            [Rank.TWO, Rank.THREE, Rank.FOUR, Rank.FIVE],
        ):
            trick.play(seat, Card(Suit.CLUBS, rank))
        self.assertTrue(trick.is_complete())
        self.assertIsNone(trick.next_to_play())


if __name__ == "__main__":
    unittest.main()
