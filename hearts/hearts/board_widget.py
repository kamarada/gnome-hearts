"""The card table: a single custom-drawn Gtk.DrawingArea, matching
Aisleriot's own single-canvas Cairo approach rather than one child widget
per card (52+ widgets would be needless overhead for fanned, overlapping
hands with no benefit at this scale).
"""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject, Gtk  # noqa: E402

from .card_renderer import CARD_ASPECT_RATIO, CardRenderer
from .engine.card import Card, HUMAN_SEAT, Seat
from .engine.game import HeartsGame, Phase
from .engine.rules import explain_illegal_play, legal_plays

_SEAT_LABELS = {
    Seat.NORTH: "North",
    Seat.EAST: "East",
    Seat.SOUTH: "You",
    Seat.WEST: "West",
}

_FELT_COLOR = (0.06, 0.35, 0.16)
_HIGHLIGHT_COLOR = (0.95, 0.85, 0.2)


class BoardWidget(Gtk.DrawingArea):
    __gtype_name__ = "HeartsBoardWidget"

    __gsignals__ = {
        "selection-changed": (GObject.SignalFlags.RUN_FIRST, None, (int,)),
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._renderer = CardRenderer()
        self._game: HeartsGame | None = None
        self._selected: set[Card] = set()
        self._south_hit_rects: list[tuple[Card, tuple[float, float, float, float]]] = []

        self.on_change: callable = lambda: None
        self.on_warning: callable = lambda message: None

        self.set_draw_func(self._on_draw)
        click = Gtk.GestureClick.new()
        click.connect("pressed", self._on_click)
        self.add_controller(click)

    # -- public API -------------------------------------------------------

    def set_game(self, game: HeartsGame) -> None:
        self._game = game
        self._selected.clear()
        self.queue_draw()

    def selected_cards(self) -> list[Card]:
        return list(self._selected)

    def pass_selected_cards(self) -> None:
        if self._game is None or len(self._selected) != 3:
            return
        self._game.submit_pass(HUMAN_SEAT, list(self._selected))
        self._selected.clear()
        self.emit("selection-changed", 0)
        self.queue_draw()
        self.on_change()

    # -- drawing ------------------------------------------------------------

    def _on_draw(self, area, cr, width, height):
        cr.set_source_rgb(*_FELT_COLOR)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        self._south_hit_rects = []
        if self._game is None:
            return

        game = self._game
        card_h = max(60, min(150, height * 0.24))

        self._draw_hand_back_row(cr, game, Seat.NORTH, width / 2, card_h * 0.6, card_h * 0.55, horizontal=True)
        self._draw_hand_back_row(cr, game, Seat.WEST, card_h * 0.45, height / 2, card_h * 0.55, horizontal=False)
        self._draw_hand_back_row(cr, game, Seat.EAST, width - card_h * 0.45, height / 2, card_h * 0.55, horizontal=False)

        self._draw_trick(cr, game, width / 2, height / 2, card_h * 0.85)

        self._draw_south_hand(cr, game, width / 2, height - card_h * 0.65, card_h)

    def _draw_hand_back_row(self, cr, game, seat, cx, cy, card_h, horizontal):
        count = len(game.hands.get(seat, []))
        if count == 0:
            return
        card_w = card_h * CARD_ASPECT_RATIO
        surface = self._renderer.get_back_surface(int(card_h))
        step = min(card_w * 0.35, (140 / max(count, 1)))
        total = step * (count - 1)
        for i in range(count):
            offset = -total / 2 + i * step
            if horizontal:
                x, y = cx + offset - card_w / 2, cy - card_h / 2
            else:
                x, y = cx - card_w / 2, cy + offset - card_h / 2
            cr.save()
            cr.translate(x, y)
            cr.set_source_surface(surface, 0, 0)
            cr.paint()
            cr.restore()

    def _draw_trick(self, cr, game, cx, cy, card_h):
        card_w = card_h * CARD_ASPECT_RATIO
        trick = game.current_trick
        if trick is None:
            return
        positions = {
            Seat.NORTH: (0, -card_h * 0.6),
            Seat.SOUTH: (0, card_h * 0.6),
            Seat.EAST: (card_w * 0.6, 0),
            Seat.WEST: (-card_w * 0.6, 0),
        }
        for seat, card in trick.plays:
            surface = self._renderer.get_card_surface(card, int(card_h))
            dx, dy = positions[seat]
            cr.save()
            cr.translate(cx + dx - card_w / 2, cy + dy - card_h / 2)
            cr.set_source_surface(surface, 0, 0)
            cr.paint()
            cr.restore()

    def _draw_south_hand(self, cr, game, cx, cy, card_h):
        hand = sorted(game.hands.get(HUMAN_SEAT, []))
        count = len(hand)
        if count == 0:
            return
        card_w = card_h * CARD_ASPECT_RATIO
        step = min(card_w * 0.75, 500 / max(count, 1))
        total = step * (count - 1)

        for i, card in enumerate(hand):
            offset = -total / 2 + i * step
            lift = 18 if card in self._selected else 0
            x = cx + offset - card_w / 2
            y = cy - card_h / 2 - lift
            surface = self._renderer.get_card_surface(card, int(card_h))
            cr.save()
            cr.translate(x, y)
            cr.set_source_surface(surface, 0, 0)
            cr.paint()
            cr.restore()

            if card in self._selected:
                cr.save()
                cr.set_source_rgb(*_HIGHLIGHT_COLOR)
                cr.set_line_width(3)
                cr.rectangle(x, y, card_w, card_h)
                cr.stroke()
                cr.restore()

            self._south_hit_rects.append((card, (x, y, card_w, card_h)))

    # -- interaction --------------------------------------------------------

    def _on_click(self, gesture, n_press, x, y):
        if self._game is None:
            return
        game = self._game

        if game.phase == Phase.ROUND_OVER:
            # No card to click between rounds -- any click on the table
            # deals the next round.
            game.start_round()
            self._selected.clear()
            self.queue_draw()
            self.on_change()
            return

        card = self._card_at(x, y)
        if card is None:
            return

        if game.phase == Phase.PASSING:
            self._toggle_selection(card)
        elif game.phase == Phase.PLAYING:
            self._try_play(card)

    def _card_at(self, x, y) -> Card | None:
        for card, (rx, ry, rw, rh) in reversed(self._south_hit_rects):
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return card
        return None

    def _toggle_selection(self, card: Card) -> None:
        if self._game.current_player_to_act() != HUMAN_SEAT:
            return
        if card in self._selected:
            self._selected.discard(card)
        elif len(self._selected) < 3:
            self._selected.add(card)
        else:
            self.on_warning("You can only pass 3 cards.")
            return
        self.emit("selection-changed", len(self._selected))
        self.queue_draw()

    def _try_play(self, card: Card) -> None:
        game = self._game
        if game.current_player_to_act() != HUMAN_SEAT:
            return
        hand = game.hands[HUMAN_SEAT]
        trick = game.current_trick
        hearts_broken = game.hearts_broken
        is_first_trick = game.tricks_played_this_round == 0

        legal = legal_plays(hand, trick, hearts_broken, is_first_trick)
        if card not in legal:
            reason = explain_illegal_play(hand, trick, hearts_broken, is_first_trick, card)
            self.on_warning(reason)
            return

        game.submit_play(HUMAN_SEAT, card)
        self.queue_draw()
        self.on_change()
