import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hearts.engine.card import HUMAN_SEAT, Seat, SEATS
from hearts.engine.game import HeartsGame, Phase
from hearts.engine.players.base import Player
from hearts.engine.players.human import HumanPlayer
from hearts.engine.rules import legal_plays


class ScriptedPlayer(Player):
    """Always passes its first 3 (sorted) cards and always plays the first
    legal card -- a deterministic, rules-abiding "dumb" player used to drive
    the state machine end-to-end without any real strategy."""

    def select_cards(self, hand, direction_offset):
        return sorted(hand)[:3]

    def play_card(self, hand, trick, hearts_broken, is_first_trick, scores_so_far):
        legal = legal_plays(hand, trick, hearts_broken, is_first_trick)
        return legal[0]


def make_scripted_game(**kwargs):
    players = {seat: ScriptedPlayer(seat) for seat in SEATS}
    return HeartsGame(players, **kwargs)


class FullRoundTest(unittest.TestCase):
    def test_a_full_round_completes_with_all_cards_accounted_for(self):
        game = make_scripted_game()
        game.start_game()

        self.assertIn(game.phase, (Phase.ROUND_OVER, Phase.GAME_OVER))
        total_cards = sum(len(cards) for cards in game.tricks_taken.values())
        self.assertEqual(total_cards, 52)
        for hand in game.hands.values():
            self.assertEqual(len(hand), 0)

        round_scores = game.round_scores()
        self.assertEqual(set(round_scores.keys()), set(SEATS))
        # Either a normal round (raw points sum to 26) or a moon/sun shoot
        # (exactly one seat negative, the rest zero).
        if any(v < 0 for v in round_scores.values()):
            negatives = [v for v in round_scores.values() if v < 0]
            self.assertEqual(len(negatives), 1)
            self.assertIn(negatives[0], (-26, -52))
        else:
            self.assertEqual(sum(round_scores.values()), 26)

    def test_hold_round_skips_passing_phase(self):
        game = make_scripted_game()
        game.round_number = 3  # next start_round() call makes it round 4: a hold round
        game.start_round()
        # Should have gone straight to playing (and, since all seats are
        # scripted, all the way to round/game over) without ever exposing a
        # PASSING phase to the caller.
        self.assertIn(game.phase, (Phase.ROUND_OVER, Phase.GAME_OVER))


class FullGameTest(unittest.TestCase):
    def test_game_ends_and_declares_the_lowest_scorer_the_winner(self):
        game = make_scripted_game(target_score=15)
        game.start_game()
        while game.phase == Phase.ROUND_OVER:
            game.start_round()

        self.assertTrue(game.is_game_over())
        totals = game.total_scores()
        winner = game.winner()
        self.assertIsNotNone(winner)
        self.assertEqual(totals[winner], min(totals.values()))
        self.assertGreaterEqual(max(totals.values()), 15)


class HumanSeatBlocksAutoPlayTest(unittest.TestCase):
    def test_engine_stops_and_waits_for_the_human_seat(self):
        players = {seat: ScriptedPlayer(seat) for seat in SEATS}
        players[HUMAN_SEAT] = HumanPlayer(HUMAN_SEAT)
        game = HeartsGame(players)
        game.round_number = 3  # force a hold round so we land straight in PLAYING
        game.start_round()

        self.assertEqual(game.phase, Phase.PLAYING)
        acting = game.current_player_to_act()
        # Either it's the human's turn right away, or the engine is blocked
        # waiting on them somewhere in the trick -- either way it must not
        # have silently played on the human's behalf.
        self.assertTrue(acting is None or acting == HUMAN_SEAT)
        self.assertIn(HUMAN_SEAT, [card_owner for card_owner in game.hands if len(game.hands[card_owner]) > 0])


if __name__ == "__main__":
    unittest.main()
