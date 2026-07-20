import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hearts.engine.card import Card, Rank, Seat, Suit, TWO_OF_CLUBS, QUEEN_OF_SPADES
from hearts.engine.rules import (
    is_hearts_broken,
    leader_of_first_trick,
    legal_plays,
    pass_offset,
    pass_target,
)
from hearts.engine.trick import Trick

C = lambda suit, rank: Card(suit, rank)  # noqa: E731


class PassOffsetTest(unittest.TestCase):
    def test_cycles_left_across_right_hold(self):
        self.assertEqual(pass_offset(1), 1)
        self.assertEqual(pass_offset(2), 2)
        self.assertEqual(pass_offset(3), 3)
        self.assertEqual(pass_offset(4), 0)
        # cycle repeats
        self.assertEqual(pass_offset(5), 1)
        self.assertEqual(pass_offset(8), 0)

    def test_pass_target_none_on_hold_round(self):
        self.assertIsNone(pass_target(Seat.NORTH, 4))

    def test_pass_target_wraps_around_seats(self):
        self.assertEqual(pass_target(Seat.WEST, 1), Seat.NORTH)  # left, wraps
        self.assertEqual(pass_target(Seat.NORTH, 3), Seat.WEST)  # right


class LeaderOfFirstTrickTest(unittest.TestCase):
    def test_holder_of_two_of_clubs_leads(self):
        hands = {
            Seat.NORTH: [C(Suit.HEARTS, Rank.ACE)],
            Seat.EAST: [TWO_OF_CLUBS],
            Seat.SOUTH: [],
            Seat.WEST: [],
        }
        self.assertEqual(leader_of_first_trick(hands), Seat.EAST)


class HeartsBrokenTest(unittest.TestCase):
    def test_false_when_no_point_cards_played(self):
        self.assertFalse(is_hearts_broken([C(Suit.CLUBS, Rank.TWO), C(Suit.DIAMONDS, Rank.KING)]))

    def test_true_once_a_heart_is_played(self):
        self.assertTrue(is_hearts_broken([C(Suit.HEARTS, Rank.TWO)]))

    def test_true_once_queen_of_spades_is_played(self):
        self.assertTrue(is_hearts_broken([QUEEN_OF_SPADES]))


class LegalPlaysLeadingTest(unittest.TestCase):
    def test_first_trick_must_lead_two_of_clubs(self):
        hand = [TWO_OF_CLUBS, C(Suit.CLUBS, Rank.KING), C(Suit.DIAMONDS, Rank.TWO)]
        self.assertEqual(legal_plays(hand, None, hearts_broken=False, is_first_trick=True), [TWO_OF_CLUBS])

    def test_cannot_lead_hearts_before_broken(self):
        hand = [C(Suit.HEARTS, Rank.TWO), C(Suit.CLUBS, Rank.KING)]
        trick = Trick(leader=Seat.NORTH)
        legal = legal_plays(hand, trick, hearts_broken=False, is_first_trick=False)
        self.assertNotIn(C(Suit.HEARTS, Rank.TWO), legal)
        self.assertIn(C(Suit.CLUBS, Rank.KING), legal)

    def test_can_lead_hearts_once_broken(self):
        hand = [C(Suit.HEARTS, Rank.TWO), C(Suit.CLUBS, Rank.KING)]
        trick = Trick(leader=Seat.NORTH)
        legal = legal_plays(hand, trick, hearts_broken=True, is_first_trick=False)
        self.assertIn(C(Suit.HEARTS, Rank.TWO), legal)

    def test_can_lead_hearts_if_hand_is_all_hearts_even_unbroken(self):
        hand = [C(Suit.HEARTS, Rank.TWO), C(Suit.HEARTS, Rank.THREE)]
        trick = Trick(leader=Seat.NORTH)
        legal = legal_plays(hand, trick, hearts_broken=False, is_first_trick=False)
        self.assertEqual(sorted(legal), sorted(hand))


class LegalPlaysFollowingTest(unittest.TestCase):
    def test_must_follow_suit_when_able(self):
        hand = [C(Suit.CLUBS, Rank.KING), C(Suit.HEARTS, Rank.TWO)]
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, C(Suit.CLUBS, Rank.THREE))
        legal = legal_plays(hand, trick, hearts_broken=True, is_first_trick=False)
        self.assertEqual(legal, [C(Suit.CLUBS, Rank.KING)])

    def test_may_play_anything_when_void_in_led_suit(self):
        hand = [C(Suit.HEARTS, Rank.TWO), C(Suit.SPADES, Rank.KING)]
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, C(Suit.CLUBS, Rank.THREE))
        legal = legal_plays(hand, trick, hearts_broken=True, is_first_trick=False)
        self.assertEqual(sorted(legal), sorted(hand))


class LegalPlaysNoBloodTest(unittest.TestCase):
    def test_first_trick_bans_point_cards_when_hand_has_alternatives(self):
        hand = [QUEEN_OF_SPADES, C(Suit.SPADES, Rank.TWO)]
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, C(Suit.SPADES, Rank.THREE))
        legal = legal_plays(hand, trick, hearts_broken=True, is_first_trick=True)
        self.assertEqual(legal, [C(Suit.SPADES, Rank.TWO)])

    def test_first_trick_allows_point_cards_when_hand_is_all_points(self):
        # Void in the led suit (clubs), so both point cards in hand are
        # candidates once follow-suit is applied; since the whole hand is
        # points, the no-blood filter must not remove them.
        hand = [QUEEN_OF_SPADES, C(Suit.HEARTS, Rank.TWO)]
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, C(Suit.CLUBS, Rank.THREE))
        legal = legal_plays(hand, trick, hearts_broken=True, is_first_trick=True)
        self.assertEqual(sorted(legal), sorted(hand))

    def test_first_trick_allows_forced_point_card_within_led_suit(self):
        # Void in every non-point suit for this led suit: only a heart of the
        # led suit... contrived but validates the "forced" fallback: hand
        # holds only spades in the led suit and one of them is the queen.
        hand = [QUEEN_OF_SPADES]
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, C(Suit.SPADES, Rank.THREE))
        legal = legal_plays(hand, trick, hearts_broken=True, is_first_trick=True)
        self.assertEqual(legal, [QUEEN_OF_SPADES])

    def test_second_trick_has_no_no_blood_restriction(self):
        hand = [QUEEN_OF_SPADES, C(Suit.SPADES, Rank.TWO)]
        trick = Trick(leader=Seat.NORTH)
        trick.play(Seat.NORTH, C(Suit.SPADES, Rank.THREE))
        legal = legal_plays(hand, trick, hearts_broken=True, is_first_trick=False)
        self.assertEqual(sorted(legal), sorted(hand))


if __name__ == "__main__":
    unittest.main()
