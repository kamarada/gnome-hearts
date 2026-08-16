from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk  # noqa: E402

from .window import HeartsWindow

APPLICATION_ID = "org.gnome.Hearts"

try:
    # Generated at build time from config.py.in (see hearts/meson.build) --
    # not present in the source tree itself, only in the build directory
    # (see card_renderer.find_cards_svg() for the same fallback pattern).
    from . import config

    VERSION = config.version
except ImportError:
    VERSION = "0.0.0-dev"


class HeartsApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id=APPLICATION_ID,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self._window: HeartsWindow | None = None
        self._install_actions()

    def _install_actions(self) -> None:
        actions = [
            ("new-game", self._on_new_game, ["<primary>n"]),
            ("quit", self._on_quit, ["<primary>q"]),
            ("about", self._on_about, None),
        ]
        for name, callback, accels in actions:
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", callback)
            self.add_action(action)
            if accels:
                self.set_accels_for_action(f"app.{name}", accels)

    def do_activate(self) -> None:
        if self._window is None:
            self._window = HeartsWindow(application=self)
        self._window.present()

    def _on_new_game(self, action, param) -> None:
        if self._window is not None:
            self._window.new_game()

    def _on_quit(self, action, param) -> None:
        self.quit()

    def _on_about(self, action, param) -> None:
        about = Adw.AboutDialog(
            application_name="Hearts",
            application_icon="gnome-hearts",
            developer_name="kamarada",
            version=VERSION,
            website="https://github.com/kamarada/gnome-hearts",
            license_type=Gtk.License.GPL_3_0,
            comments="A modern rewrite of the classic four-player card game.",
        )
        about.present(self._window)
