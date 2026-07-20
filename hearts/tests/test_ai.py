import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hearts.engine.card import Seat
from hearts.engine.deck import deal
from hearts.engine.players.ai import AIPlayer
from hearts.engine.rules import is_hearts_broken, leader_of_first_trick, legal_plays, pass_offset
from hearts.engine.trick import Trick


class AISelectCardsTest(unittest.TestCase):
    def test_always_returns_three_distinct_cards_from_hand(self):
        ai = AIPlayer(Seat.NORTH)
        rng = random.Random(0)
        for round_number in range(1, 20):
            hands = deal(rng)
            for seat, hand in hands.items():
                offset = pass_offset(round_number)
                if offset == 0:
                    continue
                chosen = ai.select_cards(list(hand), offset)
                self.assertEqual(len(chosen), 3)
                self.assertEqual(len(set(chosen)), 3)
                self.assertTrue(set(chosen).issubset(hand))


class AIPlayCardTest(unittest.TestCase):
    def test_always_returns_a_legal_play_across_many_random_hands(self):
        ai = AIPlayer(Seat.NORTH)
        rng = random.Random(1)
        for _ in range(200):
            hands = deal(rng)
            leader = leader_of_first_trick(hands)
            trick = Trick(leader=leader)
            hearts_broken = False
            is_first_trick = rng.choice([True, False])

            # Simulate 0-3 prior plays on this trick from other seats using
            # cards not held by `leader`, so the trick stays internally
            # consistent for the legality check.
            other_seats = [s for s in hands if s != leader]
            rng.shuffle(other_seats)
            for seat in other_seats[: rng.randint(0, 2)]:
                card = rng.choice(hands[seat])
                trick.play(seat, card)
                hands[seat].remove(card)
                if is_hearts_broken([card]):
                    hearts_broken = True

            acting_seat = trick.next_to_play()
            hand = hands[acting_seat]
            if not hand:
                continue

            legal = legal_plays(hand, trick, hearts_broken, is_first_trick)
            play = ai.play_card(
                hand=hand,
                trick=trick,
                hearts_broken=hearts_broken,
                is_first_trick=is_first_trick,
                scores_so_far={s: 0 for s in hands},
            )
            self.assertIn(play, legal)


if __name__ == "__main__":
    unittest.main()
