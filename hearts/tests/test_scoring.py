import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hearts.engine.card import Card, Rank, Seat, Suit
from hearts.engine.deck import standard_deck
from hearts.engine.scoring import score_round


def hearts_and_queen():
    return [Card(Suit.HEARTS, rank) for rank in Rank] + [Card(Suit.SPADES, Rank.QUEEN)]


class ScoreRoundNormalTest(unittest.TestCase):
    def test_scores_points_per_seat_independently(self):
        tricks = {
            Seat.NORTH: [Card(Suit.HEARTS, Rank.TWO), Card(Suit.CLUBS, Rank.THREE)],
            Seat.EAST: [Card(Suit.SPADES, Rank.QUEEN)],
            Seat.SOUTH: [],
            Seat.WEST: [Card(Suit.HEARTS, Rank.THREE)],
        }
        scores = score_round(tricks)
        self.assertEqual(scores[Seat.NORTH], 1)
        self.assertEqual(scores[Seat.EAST], 13)
        self.assertEqual(scores[Seat.SOUTH], 0)
        self.assertEqual(scores[Seat.WEST], 1)


class ShootTheMoonTest(unittest.TestCase):
    def test_shooter_scores_negative_26_others_zero(self):
        tricks = {
            Seat.NORTH: hearts_and_queen(),
            Seat.EAST: [],
            Seat.SOUTH: [],
            Seat.WEST: [],
        }
        scores = score_round(tricks)
        self.assertEqual(scores[Seat.NORTH], -26)
        self.assertEqual(scores[Seat.EAST], 0)
        self.assertEqual(scores[Seat.SOUTH], 0)
        self.assertEqual(scores[Seat.WEST], 0)


class ShootTheSunTest(unittest.TestCase):
    def test_shooter_scores_negative_52_and_overrides_moon(self):
        deck = standard_deck()
        self.assertEqual(len(deck), 52)
        tricks = {
            Seat.EAST: deck,
            Seat.NORTH: [],
            Seat.SOUTH: [],
            Seat.WEST: [],
        }
        scores = score_round(tricks)
        self.assertEqual(scores[Seat.EAST], -52)
        self.assertEqual(scores[Seat.NORTH], 0)
        self.assertEqual(scores[Seat.SOUTH], 0)
        self.assertEqual(scores[Seat.WEST], 0)


if __name__ == "__main__":
    unittest.main()
