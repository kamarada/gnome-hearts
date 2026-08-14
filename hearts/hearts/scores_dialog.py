"""A simple read-only view of the accumulated scores for each round."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gtk  # noqa: E402

from .engine.card import SEATS
from .engine.game import HeartsGame

_SEAT_LABELS = {
    "NORTH": "North",
    "EAST": "East",
    "SOUTH": "You",
    "WEST": "West",
}


class ScoresDialog(Adw.Dialog):
    __gtype_name__ = "HeartsScoresDialog"

    def __init__(self, game: HeartsGame, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Scores")
        self.set_content_width(360)

        grid = Gtk.Grid(column_spacing=18, row_spacing=8, halign=Gtk.Align.CENTER)
        grid.set_margin_top(18)
        grid.set_margin_bottom(18)
        grid.set_margin_start(18)
        grid.set_margin_end(18)

        for col, seat in enumerate(SEATS):
            heading = Gtk.Label(label=_SEAT_LABELS[seat.name])
            heading.add_css_class("heading")
            grid.attach(heading, col, 0, 1, 1)

        # One row per round, each cell showing the *running* total at that
        # point. Superseded (non-final) totals are struck through, so the
        # only plain number in each column is the current total -- the same
        # tally-style scorecard the Windows 98 and original GNOME Hearts
        # dialogs used (issue #7).
        history = game.score_history()
        totals = {seat: 0 for seat in SEATS}
        for round_number, round_scores in enumerate(history, start=1):
            for seat in SEATS:
                totals[seat] += round_scores.get(seat, 0)
            is_last_round = round_number == len(history)
            for col, seat in enumerate(SEATS):
                text = str(totals[seat])
                label = Gtk.Label(label=text if is_last_round else f"<s>{text}</s>")
                if not is_last_round:
                    label.set_use_markup(True)
                grid.attach(label, col, round_number, 1, 1)

        # Adw.Dialog doesn't add a titlebar/close button on its own -- it
        # only appears if the content includes a header bar, same as an
        # Adw.ApplicationWindow. Without this, Esc was the only way to
        # close the dialog (issue #3).
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(Adw.HeaderBar())
        toolbar_view.set_content(grid)
        self.set_child(toolbar_view)
