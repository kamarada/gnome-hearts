import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hearts.engine.card import Card, Rank, Suit
from hearts.engine.deck import standard_deck


class CardPointsTest(unittest.TestCase):
    def test_hearts_are_one_point(self):
        for rank in Rank:
            self.assertEqual(Card(Suit.HEARTS, rank).points(), 1)

    def test_queen_of_spades_is_thirteen_points(self):
        self.assertEqual(Card(Suit.SPADES, Rank.QUEEN).points(), 13)

    def test_other_cards_are_pointless(self):
        for suit in (Suit.CLUBS, Suit.DIAMONDS):
            for rank in Rank:
                self.assertEqual(Card(suit, rank).points(), 0)
        for rank in Rank:
            if rank != Rank.QUEEN:
                self.assertEqual(Card(Suit.SPADES, rank).points(), 0)


class CardSvgElementIdTest(unittest.TestCase):
    def test_all_52_cards_produce_a_plausible_id(self):
        expected_suit_names = {
            Suit.CLUBS: "club",
            Suit.DIAMONDS: "diamond",
            Suit.HEARTS: "heart",
            Suit.SPADES: "spade",
        }
        expected_rank_names = {
            Rank.ACE: "1",
            Rank.JACK: "jack",
            Rank.QUEEN: "queen",
            Rank.KING: "king",
        }
        for card in standard_deck():
            suit_name = expected_suit_names[card.suit]
            rank_name = expected_rank_names.get(card.rank, str(int(card.rank)))
            self.assertEqual(card.svg_element_id(), f"{suit_name}_{rank_name}")

    def test_ace_uses_id_one_not_fourteen(self):
        self.assertEqual(Card(Suit.CLUBS, Rank.ACE).svg_element_id(), "club_1")

    def test_numeric_ranks_use_plain_numbers(self):
        self.assertEqual(Card(Suit.SPADES, Rank.TEN).svg_element_id(), "spade_10")


if __name__ == "__main__":
    unittest.main()
