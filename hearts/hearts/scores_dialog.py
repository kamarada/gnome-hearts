"""A simple read-only view of the current round's and running scores."""

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

        grid = Gtk.Grid(column_spacing=18, row_spacing=8)
        grid.set_margin_top(18)
        grid.set_margin_bottom(18)
        grid.set_margin_start(18)
        grid.set_margin_end(18)

        for col, seat in enumerate(SEATS):
            heading = Gtk.Label(label=_SEAT_LABELS[seat.name])
            heading.add_css_class("heading")
            grid.attach(heading, col + 1, 0, 1, 1)

        round_scores = game.round_scores()
        grid.attach(Gtk.Label(label="This round", xalign=0), 0, 1, 1, 1)
        for col, seat in enumerate(SEATS):
            grid.attach(Gtk.Label(label=str(round_scores.get(seat, 0))), col + 1, 1, 1, 1)

        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        grid.attach(separator, 0, 2, len(SEATS) + 1, 1)

        totals = game.total_scores()
        total_label = Gtk.Label(label="Total", xalign=0)
        total_label.add_css_class("heading")
        grid.attach(total_label, 0, 3, 1, 1)
        for col, seat in enumerate(SEATS):
            label = Gtk.Label(label=str(totals[seat]))
            label.add_css_class("heading")
            grid.attach(label, col + 1, 3, 1, 1)

        # Adw.Dialog doesn't add a titlebar/close button on its own -- it
        # only appears if the content includes a header bar, same as an
        # Adw.ApplicationWindow. Without this, Esc was the only way to
        # close the dialog (issue #3).
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(Adw.HeaderBar())
        toolbar_view.set_content(grid)
        self.set_child(toolbar_view)
