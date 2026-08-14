"""The card table: a single custom-drawn Gtk.DrawingArea, matching
Aisleriot's own single-canvas Cairo approach rather than one child widget
per card (52+ widgets would be needless overhead for fanned, overlapping
hands with no benefit at this scale).

HeartsGame resolves an entire burst of plays (e.g. several AI turns in a
row) synchronously and immediately -- it has no concept of pacing. To
animate individual card plays anyway, this widget doesn't read
game.hands/game.current_trick directly when drawing. Instead it keeps its
own "display state" (what's actually on screen right now), fed by the
engine's on_round_start/on_pass_complete/on_card_played/on_trick_complete/
on_round_complete/on_game_complete callbacks, and a queue of those events
is replayed one at a time -- sliding a card into place, pausing on a
completed trick so it's actually visible, etc. -- via a GLib timer, fully
decoupled from how fast the engine itself resolved them.
"""

from __future__ import annotations

import collections

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import GLib, GObject, Gtk, Pango, PangoCairo  # noqa: E402

from .card_renderer import CARD_ASPECT_RATIO, CardRenderer
from .engine.card import Card, HUMAN_SEAT, Seat, SEATS
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
_RECEIVED_COLOR = (0.3, 0.65, 1.0)
_LABEL_COLOR = (1, 1, 1)
_LABEL_MARGIN = 12
_SELECTION_LIFT = 18  # how far a selected south card rises, in _draw_south_hand

_TICK_INTERVAL_MS = 16  # ~60fps
_PLAY_ANIM_MS = 220  # how long a card takes to slide from hand to table
_TRICK_PAUSE_MS = 800  # how long a completed trick stays visible before clearing
_COLLECT_ANIM_MS = 260  # how long the completed trick takes to slide to its winner


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

        # Display state: what's actually drawn, kept in sync with the
        # engine via callbacks and animation playback rather than read
        # live from game.hands/game.current_trick (see module docstring).
        self._display_south_hand: list[Card] = []
        self._display_counts: dict[Seat, int] = {s: 0 for s in SEATS if s != HUMAN_SEAT}
        self._display_trick: dict[Seat, Card] = {}

        # Set right after a pass exchange, listing the 3 cards just
        # received; stays set (blocking the animation queue below, and
        # highlighted in the hand) until the player clicks to acknowledge.
        self._received_pause: list[Card] | None = None
        self._received_highlight: set[Card] = set()

        self._pending_events: collections.deque = collections.deque()
        self._tick_active = False
        self._pause_until: float | None = None
        self._pending_collect: tuple[object, Seat] | None = None
        self._collecting_cards: list[tuple[Seat, Card, tuple, tuple]] = []
        self._collecting_start_time: float | None = None
        self._collecting_card_h: float = 0
        self._animating_seat: Seat | None = None
        self._animating_card: Card | None = None
        self._animation_start: tuple[float, float] | None = None
        self._animation_end: tuple[float, float] | None = None
        self._animation_start_time: float | None = None
        self._animation_card_h: float = 0

        self.on_change: callable = lambda: None
        self.on_warning: callable = lambda message: None
        self.on_trick_shown: callable = lambda trick, winner: None
        self.on_round_shown: callable = lambda scores: None
        self.on_game_shown: callable = lambda winner: None

        self.set_draw_func(self._on_draw)
        click = Gtk.GestureClick.new()
        click.connect("pressed", self._on_click)
        self.add_controller(click)

    # -- public API -------------------------------------------------------

    def set_game(self, game: HeartsGame) -> None:
        self._game = game
        self._selected.clear()
        self._reset_animation_state()
        self._display_south_hand = []
        self._display_counts = {s: 0 for s in SEATS if s != HUMAN_SEAT}
        self._display_trick = {}
        self.queue_draw()

    def selected_cards(self) -> list[Card]:
        return list(self._selected)

    def pending_received_cards(self) -> list[Card] | None:
        """The 3 cards just received, while the player hasn't yet
        acknowledged them (see handle_pass_complete()); None otherwise."""
        return self._received_pause

    def is_busy(self) -> bool:
        """Whether an animation/pause is in progress or queued -- the UI
        should hold off on the "your turn"-style status text and ignore
        clicks until this clears, or the player could act ahead of what's
        still animating in."""
        return (
            bool(self._pending_events)
            or self._animating_seat is not None
            or self._pause_until is not None
            or self._collecting_start_time is not None
            or self._received_pause is not None
        )

    def _reset_animation_state(self) -> None:
        self._pending_events.clear()
        self._pause_until = None
        self._pending_collect = None
        self._collecting_cards = []
        self._collecting_start_time = None
        self._animating_seat = None
        self._animating_card = None
        self._received_pause = None
        self._received_highlight = set()

    def pass_selected_cards(self) -> None:
        if self._game is None or len(self._selected) != 3:
            return
        self._game.submit_pass(HUMAN_SEAT, list(self._selected))
        self._selected.clear()
        self.emit("selection-changed", 0)
        self.queue_draw()
        self.on_change()

    # -- engine event handlers (wired up by window.py) ---------------------

    def handle_round_start(self) -> None:
        """Fired by the engine right after dealing. Not itself animated
        (only plays are) -- just resets display state to the fresh hands."""
        game = self._game
        self._reset_animation_state()
        self._selected.clear()
        self._display_south_hand = sorted(game.hands[HUMAN_SEAT])
        self._display_counts = {s: len(game.hands[s]) for s in SEATS if s != HUMAN_SEAT}
        self._display_trick = {}
        self.queue_draw()

    def handle_pass_complete(self) -> None:
        """Fired right after the 4-way card exchange applies. Hand *size*
        is unaffected (still 13 each) so only south's actual displayed
        cards need resyncing -- opponents are shown as backs either way.

        Diffs against the pre-exchange display hand (still untouched at
        this point) to find which 3 cards were just received, then pauses
        -- blocking the animation queue below, even though any resulting
        trick-opening AI plays are likely already queued right behind this
        by the time it returns -- until the player clicks to acknowledge,
        the same "click to continue" beat both the original GNOME Hearts
        and the Windows Hearts Network used here.
        """
        game = self._game
        if game is None:
            return
        previously_held = set(self._display_south_hand)
        self._display_south_hand = sorted(game.hands[HUMAN_SEAT])
        received = sorted(set(self._display_south_hand) - previously_held)

        self._received_pause = received
        self._received_highlight = set(received)
        self.queue_draw()

    def handle_card_played(self, seat: Seat, card: Card) -> None:
        self._pending_events.append(("play", seat, card))
        self._ensure_ticking()

    def handle_trick_complete(self, trick, winner: Seat) -> None:
        self._pending_events.append(("trick_done", trick, winner))
        self._ensure_ticking()

    def handle_round_complete(self, scores: dict[Seat, int]) -> None:
        self._pending_events.append(("round_done", scores))
        self._ensure_ticking()

    def handle_game_complete(self, winner: Seat) -> None:
        self._pending_events.append(("game_done", winner))
        self._ensure_ticking()

    # -- animation playback -------------------------------------------------

    def _ensure_ticking(self) -> None:
        if not self._tick_active:
            self._tick_active = True
            GLib.timeout_add(_TICK_INTERVAL_MS, self._tick)

    def _tick(self) -> bool:
        if self._received_pause is not None:
            # Waiting on the player to click and acknowledge the cards
            # they received -- nothing to animate meanwhile, so stop
            # ticking entirely rather than idle-polling; _on_click()
            # restarts it once dismissed.
            self._tick_active = False
            return False

        now = GLib.get_monotonic_time() / 1000.0

        if self._pause_until is not None:
            if now < self._pause_until:
                return True
            self._pause_until = None
            self._start_trick_collect(now)
            self.queue_draw()

        if self._collecting_start_time is not None:
            elapsed = now - self._collecting_start_time
            if elapsed < _COLLECT_ANIM_MS:
                self.queue_draw()
                return True
            self._display_trick = {}
            self._collecting_cards = []
            self._collecting_start_time = None
            self.queue_draw()

        if self._animating_seat is not None:
            elapsed = now - self._animation_start_time
            if elapsed < _PLAY_ANIM_MS:
                self.queue_draw()
                return True
            self._display_trick[self._animating_seat] = self._animating_card
            if self._animating_seat == HUMAN_SEAT:
                if self._animating_card in self._display_south_hand:
                    self._display_south_hand.remove(self._animating_card)
            else:
                current = self._display_counts.get(self._animating_seat, 0)
                self._display_counts[self._animating_seat] = max(0, current - 1)
            self._animating_seat = None
            self._animating_card = None
            self.queue_draw()

        if not self._pending_events:
            self._tick_active = False
            self.on_change()
            return False

        event = self._pending_events.popleft()
        kind = event[0]
        if kind == "play":
            _, seat, card = event
            self._start_card_animation(seat, card, now)
        elif kind == "trick_done":
            _, trick, winner = event
            self._pending_collect = (trick, winner)
            self._pause_until = now + _TRICK_PAUSE_MS
            self.on_trick_shown(trick, winner)
        elif kind == "round_done":
            _, scores = event
            self.on_round_shown(scores)
        elif kind == "game_done":
            _, winner = event
            self.on_game_shown(winner)

        return True

    def _start_trick_collect(self, now: float) -> None:
        """Slide the completed trick's cards from the table to whoever won
        it, instead of just vanishing -- makes the winner obvious and gives
        the pause on the completed trick a natural resolution."""
        if self._pending_collect is None:
            self._display_trick = {}
            return
        trick, winner = self._pending_collect
        self._pending_collect = None

        width, height = self.get_width(), self.get_height()
        card_h = self._card_h(height)
        end = self._hand_center(winner, width, height, card_h)

        self._collecting_cards = [
            (seat, card, self._trick_slot_point(seat, width, height, card_h), end)
            for seat, card in self._display_trick.items()
        ]
        self._collecting_card_h = card_h * 0.85
        self._collecting_start_time = now

    def _start_card_animation(self, seat: Seat, card: Card, now: float) -> None:
        width, height = self.get_width(), self.get_height()
        card_h = self._card_h(height)

        start = None
        if seat == HUMAN_SEAT:
            for c, rect in self._south_hit_rects:
                if c == card:
                    rx, ry, rw, rh = rect
                    start = (rx + rw / 2, ry + rh / 2)
                    break
        if start is None:
            start = self._hand_center(seat, width, height, card_h)

        self._animating_seat = seat
        self._animating_card = card
        self._animation_start = start
        self._animation_end = self._trick_slot_point(seat, width, height, card_h)
        self._animation_start_time = now
        self._animation_card_h = card_h * 0.85
        self.queue_draw()

    # -- layout helpers, shared between drawing and animation ---------------

    def _card_h(self, height: float) -> float:
        return max(60, min(150, height * 0.24))

    def _hand_center(self, seat: Seat, width: float, height: float, card_h: float) -> tuple[float, float]:
        if seat == Seat.NORTH:
            return width / 2, card_h * 0.6
        if seat == Seat.WEST:
            return card_h * 0.45, height / 2
        if seat == Seat.EAST:
            return width - card_h * 0.45, height / 2
        return width / 2, height - card_h * 0.65  # SOUTH

    def _trick_slot_point(self, seat: Seat, width: float, height: float, card_h: float) -> tuple[float, float]:
        cx, cy = width / 2, height / 2
        trick_card_h = card_h * 0.85
        trick_card_w = trick_card_h * CARD_ASPECT_RATIO
        offsets = {
            Seat.NORTH: (0, -trick_card_h * 0.6),
            Seat.SOUTH: (0, trick_card_h * 0.6),
            Seat.EAST: (trick_card_w * 0.6, 0),
            Seat.WEST: (-trick_card_w * 0.6, 0),
        }
        dx, dy = offsets[seat]
        return cx + dx, cy + dy

    # -- drawing ------------------------------------------------------------

    def _on_draw(self, area, cr, width, height):
        cr.set_source_rgb(*_FELT_COLOR)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        self._south_hit_rects = []
        if self._game is None:
            return

        card_h = self._card_h(height)
        back_card_h = card_h * 0.55
        back_card_w = back_card_h * CARD_ASPECT_RATIO

        self._draw_hand_back_row(cr, Seat.NORTH, width / 2, card_h * 0.6, back_card_h, horizontal=True)
        self._draw_hand_back_row(cr, Seat.WEST, card_h * 0.45, height / 2, back_card_h, horizontal=False)
        self._draw_hand_back_row(cr, Seat.EAST, width - card_h * 0.45, height / 2, back_card_h, horizontal=False)

        self._draw_trick(cr, width, height, card_h)

        self._draw_south_hand(cr, width / 2, height - card_h * 0.65, card_h)

        # Player names, positioned on the side of each hand that faces the
        # table (matching Aisleriot-era Hearts implementations, e.g. the
        # Windows 98 and original GNOME Hearts clients).
        self._draw_seat_label(
            cr, _SEAT_LABELS[Seat.NORTH],
            width / 2, card_h * 0.6 + back_card_h / 2 + _LABEL_MARGIN, "center",
        )
        self._draw_seat_label(
            cr, _SEAT_LABELS[Seat.WEST],
            card_h * 0.45 + back_card_w / 2 + _LABEL_MARGIN, height / 2, "left",
        )
        self._draw_seat_label(
            cr, _SEAT_LABELS[Seat.EAST],
            width - card_h * 0.45 - back_card_w / 2 - _LABEL_MARGIN, height / 2, "right",
        )
        self._draw_seat_label(
            cr, _SEAT_LABELS[Seat.SOUTH],
            width / 2,
            height - card_h * 0.65 - card_h / 2 - _SELECTION_LIFT - _LABEL_MARGIN,
            "center",
        )

        self._draw_animating_card(cr)
        self._draw_collecting_cards(cr, width, height)

    def _draw_seat_label(self, cr, text, x, y, halign):
        layout = PangoCairo.create_layout(cr)
        layout.set_text(text, -1)
        font_desc = Pango.FontDescription()
        font_desc.set_family("Sans")
        font_desc.set_weight(Pango.Weight.BOLD)
        font_desc.set_size(13 * Pango.SCALE)
        layout.set_font_description(font_desc)

        _ink, logical = layout.get_pixel_extents()
        if halign == "center":
            draw_x = x - logical.width / 2
        elif halign == "right":
            draw_x = x - logical.width
        else:
            draw_x = x

        cr.save()
        cr.set_source_rgb(*_LABEL_COLOR)
        cr.move_to(draw_x, y - logical.height / 2)
        PangoCairo.show_layout(cr, layout)
        cr.restore()

    def _draw_hand_back_row(self, cr, seat, cx, cy, card_h, horizontal):
        count = self._display_counts.get(seat, 0)
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

    def _draw_trick(self, cr, width, height, card_h):
        if self._collecting_start_time is not None:
            # Cards are being drawn mid-flight to the winner by
            # _draw_collecting_cards() instead of sitting statically here.
            return
        trick_card_h = card_h * 0.85
        trick_card_w = trick_card_h * CARD_ASPECT_RATIO
        for seat, card in self._display_trick.items():
            surface = self._renderer.get_card_surface(card, int(trick_card_h))
            x, y = self._trick_slot_point(seat, width, height, card_h)
            cr.save()
            cr.translate(x - trick_card_w / 2, y - trick_card_h / 2)
            cr.set_source_surface(surface, 0, 0)
            cr.paint()
            cr.restore()

    def _draw_south_hand(self, cr, cx, cy, card_h):
        hand = self._display_south_hand
        count = len(hand)
        if count == 0:
            return
        card_w = card_h * CARD_ASPECT_RATIO
        step = min(card_w * 0.75, 500 / max(count, 1))
        total = step * (count - 1)

        for i, card in enumerate(hand):
            offset = -total / 2 + i * step
            lift = _SELECTION_LIFT if (card in self._selected or card in self._received_highlight) else 0
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
            elif card in self._received_highlight:
                cr.save()
                cr.set_source_rgb(*_RECEIVED_COLOR)
                cr.set_line_width(3)
                cr.rectangle(x, y, card_w, card_h)
                cr.stroke()
                cr.restore()

            self._south_hit_rects.append((card, (x, y, card_w, card_h)))

    def _draw_animating_card(self, cr):
        if self._animating_seat is None:
            return
        now = GLib.get_monotonic_time() / 1000.0
        t = min(1.0, (now - self._animation_start_time) / _PLAY_ANIM_MS)
        t = 1 - (1 - t) ** 2  # ease-out

        sx, sy = self._animation_start
        ex, ey = self._animation_end
        x = sx + (ex - sx) * t
        y = sy + (ey - sy) * t

        card_h = self._animation_card_h
        card_w = card_h * CARD_ASPECT_RATIO
        surface = self._renderer.get_card_surface(self._animating_card, int(card_h))
        cr.save()
        cr.translate(x - card_w / 2, y - card_h / 2)
        cr.set_source_surface(surface, 0, 0)
        cr.paint()
        cr.restore()

    def _draw_collecting_cards(self, cr, width, height):
        if self._collecting_start_time is None:
            return
        now = GLib.get_monotonic_time() / 1000.0
        t = min(1.0, (now - self._collecting_start_time) / _COLLECT_ANIM_MS)
        t = 1 - (1 - t) ** 2  # ease-out

        card_h = self._collecting_card_h
        card_w = card_h * CARD_ASPECT_RATIO
        for _seat, card, start, end in self._collecting_cards:
            sx, sy = start
            ex, ey = end
            x = sx + (ex - sx) * t
            y = sy + (ey - sy) * t
            surface = self._renderer.get_card_surface(card, int(card_h))
            cr.save()
            cr.translate(x - card_w / 2, y - card_h / 2)
            cr.set_source_surface(surface, 0, 0)
            cr.paint()
            cr.restore()

    # -- interaction --------------------------------------------------------

    def _on_click(self, gesture, n_press, x, y):
        if self._game is None:
            return

        if self._received_pause is not None:
            self._received_pause = None
            self._received_highlight = set()
            self.queue_draw()
            self.on_change()
            self._ensure_ticking()
            return

        if self.is_busy():
            return
        game = self._game

        if game.phase == Phase.ROUND_OVER:
            # No card to click between rounds -- any click on the table
            # deals the next round.
            game.start_round()
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
