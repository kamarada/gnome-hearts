import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hearts.engine.card import SEATS
from hearts.engine.deck import deal, standard_deck


class StandardDeckTest(unittest.TestCase):
    def test_has_52_unique_cards(self):
        deck = standard_deck()
        self.assertEqual(len(deck), 52)
        self.assertEqual(len(set(deck)), 52)


class DealTest(unittest.TestCase):
    def test_deals_13_cards_to_each_seat(self):
        hands = deal(random.Random(1))
        self.assertEqual(set(hands.keys()), set(SEATS))
        for seat in SEATS:
            self.assertEqual(len(hands[seat]), 13)

    def test_deals_all_52_cards_with_no_duplicates(self):
        hands = deal(random.Random(1))
        all_cards = [c for hand in hands.values() for c in hand]
        self.assertEqual(len(all_cards), 52)
        self.assertEqual(len(set(all_cards)), 52)

    def test_deterministic_with_seeded_rng(self):
        hands_a = deal(random.Random(42))
        hands_b = deal(random.Random(42))
        self.assertEqual(hands_a, hands_b)


if __name__ == "__main__":
    unittest.main()
