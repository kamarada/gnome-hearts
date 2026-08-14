# Hearts

A from-scratch rewrite of GNOME Hearts (`gnome-hearts-0.3.1/` at the repo
root) in Python, GTK4 and libadwaita — a modern, natively-buildable
replacement for the original GTK2/libglade2/embedded-Python2 game, which
today only runs via a distrobox workaround (see `ansible/gnome-hearts.yml`).

Uses [Aisleriot](https://gitlab.gnome.org/GNOME/aisleriot) (vendored as
the `aisleriot` submodule at the repo root) as an architectural reference,
not a code source: its engine/rules-script split is mirrored here as a
`gi`-free `hearts/engine/` package (cards, deck, tricks, rules, scoring,
the game state machine) driven by a separate GTK4 UI layer, and its
`anglo.svg` card deck is reused directly rather than bundling new art.

## Scope

v1 implements the **Standard ruleset only**, fully playable against 3 AI
opponents: dealing, passing (left/across/right/hold, cycling every 4
rounds), trick play (follow suit, 2♣ leads, "no blood" on the first trick,
hearts must be broken before leading), scoring (hearts = 1 point, Queen of
Spades = 13, shoot the moon/sun), and running score to 100 points. At the
end of each round the point cards each player took are shown on the table,
and a Scores dialog (running total per round, oldest to newest) opens
automatically.

Deliberately deferred: other rulesets (Omnibus, Omnibus Alternative, Spot
Hearts), card-theme customization, multiple AI personalities, sound,
translations, undo/redo, hints.

## Building and running

```sh
meson setup build
meson compile -C build
meson test -C build      # engine unit tests
sudo ninja -C build install
hearts
```

Or via the repo's [Ansible playbook](../ansible/hearts.yml):

```sh
ansible-playbook ../ansible/hearts.yml
```

Requires the `aisleriot` submodule checked out (`git submodule update
--init aisleriot` from the repo root) for its card art, plus Meson, Ninja,
Python 3, and PyGObject with GTK4/libadwaita/Rsvg — see
`../ansible/README.md` for exact package names per distribution.

To run without installing, from this directory (the `PYTHONPATH` makes the
source-tree package importable; `meson devenv` alone doesn't add it):

```sh
PYTHONPATH="$PWD" meson devenv -C build python3 -m hearts.main
```

## Layout

- `hearts/engine/` — pure Python game logic (no `gi` imports), fully unit
  tested independently of the UI: `card.py`, `deck.py`, `trick.py`,
  `rules.py`, `scoring.py`, `game.py` (the state machine), and
  `engine/players/` (the AI opponent and the human-seat adapter).
- `hearts/` (the rest) — the GTK4/libadwaita UI: `application.py`,
  `window.py` (+ `hearts.ui`), `board_widget.py` (the card table, drawn
  directly with Cairo rather than one widget per card), `card_renderer.py`
  (renders individual cards from `anglo.svg`), `scores_dialog.py`.
- `data/` — desktop file, AppStream metainfo, GSettings schema, app icon.
- `tests/` — engine unit tests, run via `meson test`.
