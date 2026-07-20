"""The Hearts state machine: deal -> pass -> play tricks -> score -> repeat.

UI-agnostic and gi-free by design. The UI subscribes to plain callback
lists (on_trick_complete, on_round_complete, on_game_complete, on_ai_turn)
and drives the human seat by calling submit_pass()/submit_play(); AI seats
are resolved synchronously and internally whenever it becomes their turn.
"""

from __future__ import annotations

import enum
import random
from typing import Callable

from .card import Card, HUMAN_SEAT, Seat, SEATS
from .deck import deal
from .players.base import Player
from .players.human import HumanPlayer
from .rules import is_hearts_broken, leader_of_first_trick, legal_plays, pass_offset, pass_target
from .scoring import score_round
from .trick import Trick

DEFAULT_TARGET_SCORE = 100


class Phase(enum.Enum):
    DEALING = enum.auto()
    PASSING = enum.auto()
    PLAYING = enum.auto()
    ROUND_OVER = enum.auto()
    GAME_OVER = enum.auto()


class HeartsGame:
    def __init__(
        self,
        players: dict[Seat, Player],
        rng: random.Random | None = None,
        target_score: int = DEFAULT_TARGET_SCORE,
    ):
        if set(players.keys()) != set(SEATS):
            raise ValueError("must supply exactly one player per seat")
        self.players = players
        self.rng = rng or random.Random()
        self.target_score = target_score

        self.phase = Phase.DEALING
        self.round_number = 0
        self.hands: dict[Seat, list[Card]] = {seat: [] for seat in SEATS}
        self.tricks_taken: dict[Seat, list[Card]] = {seat: [] for seat in SEATS}
        self.current_trick: Trick | None = None
        self.tricks_played_this_round = 0
        self.hearts_broken = False

        self._pending_passes: dict[Seat, list[Card]] = {}
        self._total_scores: dict[Seat, int] = {seat: 0 for seat in SEATS}
        self._last_round_scores: dict[Seat, int] = {seat: 0 for seat in SEATS}
        self._winner: Seat | None = None

        self.on_trick_complete: list[Callable[[Trick, Seat], None]] = []
        self.on_round_complete: list[Callable[[dict[Seat, int]], None]] = []
        self.on_game_complete: list[Callable[[Seat], None]] = []
        self.on_ai_turn: list[Callable[[Seat], None]] = []

    # -- public API -----------------------------------------------------

    def start_game(self) -> None:
        self.round_number = 0
        self._total_scores = {seat: 0 for seat in SEATS}
        self._winner = None
        self.start_round()

    def start_round(self) -> None:
        self.round_number += 1
        self.hands = deal(self.rng)
        self.tricks_taken = {seat: [] for seat in SEATS}
        self._last_round_scores = {seat: 0 for seat in SEATS}
        self.current_trick = None
        self.tricks_played_this_round = 0
        self.hearts_broken = False
        self._pending_passes = {}

        if pass_offset(self.round_number) == 0:
            self.phase = Phase.PLAYING
            self._open_first_trick()
            self._advance()
        else:
            self.phase = Phase.PASSING
            self._collect_ai_passes()

    def submit_pass(self, seat: Seat, cards: list[Card]) -> None:
        if self.phase != Phase.PASSING:
            raise ValueError("not in the passing phase")
        if seat in self._pending_passes:
            raise ValueError(f"{seat} has already submitted a pass this round")
        if len(cards) != 3 or len(set(cards)) != 3:
            raise ValueError("must pass exactly 3 distinct cards")
        if not set(cards).issubset(self.hands[seat]):
            raise ValueError("can only pass cards from your own hand")

        self._pending_passes[seat] = list(cards)
        if len(self._pending_passes) == len(SEATS):
            self._execute_pass_exchange()

    def submit_play(self, seat: Seat, card: Card) -> None:
        if self.phase != Phase.PLAYING or self.current_trick is None:
            raise ValueError("not in the playing phase")
        if seat != self.current_trick.next_to_play():
            raise ValueError(f"it is not {seat}'s turn to play")
        legal = legal_plays(
            self.hands[seat], self.current_trick, self.hearts_broken, self._is_first_trick()
        )
        if card not in legal:
            raise ValueError(f"{card} is not a legal play")

        self._apply_play(seat, card)
        self._advance()

    def current_player_to_act(self) -> Seat | None:
        """Which seat, if any, the UI should be prompting the human for."""
        if self.phase == Phase.PASSING:
            return None if HUMAN_SEAT in self._pending_passes else HUMAN_SEAT
        if self.phase == Phase.PLAYING and self.current_trick is not None:
            seat = self.current_trick.next_to_play()
            return seat if seat == HUMAN_SEAT else None
        return None

    def round_scores(self) -> dict[Seat, int]:
        return dict(self._last_round_scores)

    def total_scores(self) -> dict[Seat, int]:
        return dict(self._total_scores)

    def is_game_over(self) -> bool:
        return self.phase == Phase.GAME_OVER

    def winner(self) -> Seat | None:
        return self._winner

    # -- internals --------------------------------------------------------

    def _is_first_trick(self) -> bool:
        return self.tricks_played_this_round == 0

    def _open_first_trick(self) -> None:
        leader = leader_of_first_trick(self.hands)
        self.current_trick = Trick(leader=leader)

    def _collect_ai_passes(self) -> None:
        offset = pass_offset(self.round_number)
        for seat, player in self.players.items():
            if isinstance(player, HumanPlayer):
                continue
            cards = player.select_cards(list(self.hands[seat]), offset)
            self._pending_passes[seat] = list(cards)
        if len(self._pending_passes) == len(SEATS):
            self._execute_pass_exchange()

    def _execute_pass_exchange(self) -> None:
        new_hands = {
            seat: [c for c in self.hands[seat] if c not in self._pending_passes[seat]]
            for seat in SEATS
        }
        for seat in SEATS:
            target = pass_target(seat, self.round_number)
            assert target is not None  # PASSING phase implies a non-hold round
            new_hands[target].extend(self._pending_passes[seat])
        for seat in SEATS:
            new_hands[seat].sort()

        self.hands = new_hands
        self._pending_passes = {}
        self.phase = Phase.PLAYING
        self._open_first_trick()
        self._advance()

    def _apply_play(self, seat: Seat, card: Card) -> None:
        self.hands[seat].remove(card)
        self.current_trick.play(seat, card)

    def _advance(self) -> None:
        """Resolve trick/round completions and auto-play AI turns until the
        human seat must act, or the round/game has ended."""
        while self.phase == Phase.PLAYING:
            if self.current_trick.is_complete():
                self._finish_trick()
                continue
            next_seat = self.current_trick.next_to_play()
            if next_seat is None:
                return
            player = self.players[next_seat]
            if isinstance(player, HumanPlayer):
                return

            for callback in self.on_ai_turn:
                callback(next_seat)

            card = player.play_card(
                hand=list(self.hands[next_seat]),
                trick=self.current_trick,
                hearts_broken=self.hearts_broken,
                is_first_trick=self._is_first_trick(),
                scores_so_far=self.total_scores(),
            )
            self._apply_play(next_seat, card)

    def _finish_trick(self) -> None:
        trick = self.current_trick
        winner = trick.winner()
        self.tricks_taken[winner].extend(trick.cards())
        if is_hearts_broken(trick.cards()):
            self.hearts_broken = True

        for callback in self.on_trick_complete:
            callback(trick, winner)
        for player in self.players.values():
            player.on_trick_complete(trick, winner)

        self.tricks_played_this_round += 1
        if self.tricks_played_this_round == 13:
            self._finish_round()
        else:
            self.current_trick = Trick(leader=winner)

    def _finish_round(self) -> None:
        round_scores = score_round(self.tricks_taken)
        self._last_round_scores = round_scores
        for seat in SEATS:
            self._total_scores[seat] += round_scores[seat]

        for callback in self.on_round_complete:
            callback(round_scores)
        for player in self.players.values():
            player.on_round_complete(round_scores)

        self.current_trick = None
        if max(self._total_scores.values()) >= self.target_score:
            self.phase = Phase.GAME_OVER
            self._winner = min(self._total_scores, key=self._total_scores.get)
            for callback in self.on_game_complete:
                callback(self._winner)
        else:
            self.phase = Phase.ROUND_OVER
