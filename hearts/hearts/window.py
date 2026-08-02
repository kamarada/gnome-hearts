from __future__ import annotations

import os

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk  # noqa: E402

from .board_widget import BoardWidget  # noqa: F401 (registers HeartsBoardWidget for the template)
from .engine.card import HUMAN_SEAT, Seat, SEATS
from .engine.game import HeartsGame, Phase
from .engine.players.ai import AIPlayer
from .engine.players.human import HumanPlayer
from .scores_dialog import ScoresDialog

_UI_PATH = os.path.join(os.path.dirname(__file__), "hearts.ui")

_SEAT_NAMES = {
    Seat.NORTH: "North",
    Seat.EAST: "East",
    Seat.SOUTH: "You",
    Seat.WEST: "West",
}


@Gtk.Template(filename=_UI_PATH)
class HeartsWindow(Adw.ApplicationWindow):
    __gtype_name__ = "HeartsWindow"

    toast_overlay: Adw.ToastOverlay = Gtk.Template.Child()
    board: BoardWidget = Gtk.Template.Child()
    status_label: Gtk.Label = Gtk.Template.Child()
    pass_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._game: HeartsGame | None = None

        self.board.on_change = self._refresh
        self.board.on_warning = self._on_warning
        self.board.connect("selection-changed", self._on_selection_changed)

        self._install_actions()
        self._bind_settings()

        self.new_game()

    def _install_actions(self) -> None:
        pass_action = Gio.SimpleAction.new("pass-cards", None)
        pass_action.connect("activate", lambda *_a: self.board.pass_selected_cards())
        self.add_action(pass_action)

        scores_action = Gio.SimpleAction.new("show-scores", None)
        scores_action.connect("activate", self._on_show_scores)
        self.add_action(scores_action)

    def _bind_settings(self) -> None:
        settings = Gio.Settings.new("org.gnome.Hearts")
        self._settings = settings  # keep a reference so bindings stay alive
        settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        settings.bind("window-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)

    # -- game lifecycle ---------------------------------------------------

    def new_game(self) -> None:
        players = {HUMAN_SEAT: HumanPlayer(HUMAN_SEAT)}
        for seat in SEATS:
            if seat != HUMAN_SEAT:
                players[seat] = AIPlayer(seat)

        game = HeartsGame(players)
        game.on_trick_complete.append(self._on_trick_complete)
        game.on_round_complete.append(self._on_round_complete)
        game.on_game_complete.append(self._on_game_complete)

        self._game = game
        self.board.set_game(game)
        game.start_game()
        self._refresh()

    # -- game event callbacks ----------------------------------------------

    def _on_trick_complete(self, trick, winner) -> None:
        self._toast(f"{_SEAT_NAMES[winner]} won the trick")

    def _on_round_complete(self, scores: dict) -> None:
        shooter = next((seat for seat, value in scores.items() if value < 0), None)
        if shooter is not None:
            feat = "the sun" if scores[shooter] <= -52 else "the moon"
            self._toast(f"{_SEAT_NAMES[shooter]} shot {feat}!")
        else:
            self._toast("Round over")

    def _on_game_complete(self, winner: Seat) -> None:
        self._toast(f"Game over — {_SEAT_NAMES[winner]} wins!")

    # -- UI callbacks -------------------------------------------------------

    def _on_selection_changed(self, board, count: int) -> None:
        self.pass_button.set_sensitive(count == 3)

    def _on_show_scores(self, action, param) -> None:
        if self._game is None:
            return
        ScoresDialog(self._game).present(self)

    def _on_warning(self, message: str) -> None:
        # Shown in the same status label used for turn/phase prompts (see
        # _refresh()/_status_text()) -- it's overwritten by the next real
        # game update, same as the invalid-move messages in the original
        # Windows Hearts status bar this mirrors.
        self.status_label.set_label(message)

    def _toast(self, message: str) -> None:
        self.toast_overlay.add_toast(Adw.Toast.new(message))

    # -- status ---------------------------------------------------------

    def _refresh(self) -> None:
        self.board.queue_draw()
        self.status_label.set_label(self._status_text())
        game = self._game
        self.pass_button.set_visible(game is not None and game.phase == Phase.PASSING)
        self.pass_button.set_sensitive(len(self.board.selected_cards()) == 3)

    def _status_text(self) -> str:
        game = self._game
        if game is None:
            return ""
        if game.phase == Phase.PASSING:
            if game.current_player_to_act() == HUMAN_SEAT:
                return "Choose 3 cards to pass, then click Pass"
            return "Passing cards…"
        if game.phase == Phase.PLAYING:
            if game.current_player_to_act() == HUMAN_SEAT:
                return "Your turn"
            return "Playing…"
        if game.phase == Phase.ROUND_OVER:
            return "Round over — click the table to deal the next round"
        if game.phase == Phase.GAME_OVER:
            winner = game.winner()
            return f"Game over — {_SEAT_NAMES[winner]} wins!"
        return ""
