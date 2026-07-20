"""Renders individual cards from the anglo.svg deck (vendored by the
aisleriot submodule, installed alongside this app) to cairo.ImageSurface
objects, cached by (element id, pixel height). BoardWidget draws directly
with cairo (Gtk.DrawingArea's draw callback), so surfaces -- not
Gdk.Textures -- are the natural currency here.
"""

from __future__ import annotations

import os

import cairo
import gi

gi.require_version("Rsvg", "2.0")
from gi.repository import Rsvg  # noqa: E402

from .engine.card import Card  # noqa: E402

# The "card" element in anglo.svg defines the canonical card outline size
# (width=201.1, height=313.6 in the document's own units) -- used here only
# to keep rendered cards at the correct aspect ratio.
CARD_ASPECT_RATIO = 201.1 / 313.6

BACK_ELEMENT_ID = "back"


def find_cards_svg() -> str:
    """Locate anglo.svg: the installed data file if this is an installed
    run, falling back to the aisleriot submodule checkout for `meson
    devenv`/uninstalled runs."""
    try:
        from . import config

        installed_path = os.path.join(config.pkgdatadir, "cards", "anglo.svg")
        if os.path.exists(installed_path):
            return installed_path
    except ImportError:
        pass

    devenv_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "aisleriot", "cards", "anglo.svg"
    )
    devenv_path = os.path.normpath(devenv_path)
    if os.path.exists(devenv_path):
        return devenv_path

    raise FileNotFoundError(
        "Could not find anglo.svg. Run 'git submodule update --init aisleriot' "
        "at the repo root, or install hearts so its data files are in place."
    )


class CardRenderer:
    def __init__(self, svg_path: str | None = None):
        self._handle = Rsvg.Handle.new_from_file(svg_path or find_cards_svg())
        self._cache: dict[tuple[str, int], cairo.ImageSurface] = {}

    def _render(self, element_id: str, height_px: int) -> cairo.ImageSurface:
        key = (element_id, height_px)
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        width_px = max(1, round(height_px * CARD_ASPECT_RATIO))
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width_px, height_px)
        cr = cairo.Context(surface)

        viewport = Rsvg.Rectangle()
        viewport.x = 0
        viewport.y = 0
        viewport.width = width_px
        viewport.height = height_px

        found = self._handle.render_element(cr, f"#{element_id}", viewport)
        if not found:
            raise ValueError(f"SVG element #{element_id} not found in the card deck")
        surface.flush()

        self._cache[key] = surface
        return surface

    def get_card_surface(self, card: Card, height_px: int) -> cairo.ImageSurface:
        return self._render(card.svg_element_id(), height_px)

    def get_back_surface(self, height_px: int) -> cairo.ImageSurface:
        return self._render(BACK_ELEMENT_ID, height_px)
