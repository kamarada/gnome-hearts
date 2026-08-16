# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This repo (`kamarada/gnome-hearts`) hosts GNOME Hearts, an old (2013) GTK2/libglade2/Python2 card
game; `hearts/`, a from-scratch modern rewrite of it; the infrastructure to keep the original
running on modern systems; and a git submodule of GNOME's actively-maintained Aisleriot card game
collection used as a build/architecture reference for both.

- `gnome-hearts-0.3.1/` — the original upstream source (autotools, C core + embedded Python2 AI
  scripts). **Do not modify anything here** — it's an unaltered vendor drop (see `docs/developer/`
  for its own architecture notes). It cannot be built directly on a modern Arch host: GTK2,
  libglade2, libgnomeui and Python 2 are no longer packaged. It builds and runs only inside a
  container — see below.
- `hearts/` — a from-scratch rewrite of the same game in Python + GTK4 + libadwaita, built and run
  natively (no container). Implements the Standard ruleset only; see `hearts/README.md` for exact
  scope. Uses `aisleriot/` as an architecture reference (engine/rules split) and reuses its
  `anglo.svg` card art, but shares no code with either `aisleriot/` or `gnome-hearts-0.3.1/`.
- `aisleriot/` — git submodule (`https://gitlab.gnome.org/GNOME/aisleriot.git`), GNOME's modern
  GTK3/Meson solitaire collection. Builds natively on the host (no container needed). Also the
  source of the `anglo.svg` card deck asset reused by `hearts/`. **Do not modify.**
- `ansible/` — one playbook per buildable component (see below).
- `packaging/` — distro packaging metadata, one directory per distro/format; currently
  `packaging/archlinux/PKGBUILD` for `hearts/` (see below and `packaging/README.md`).
- `docs/user/`, `docs/developer/` — archived Markdown mirrors of the original project's user and
  developer documentation from jejik.com (the upstream site), preserved verbatim including its
  original wording/typos, since jejik.com is the only remaining source for these docs. These
  describe `gnome-hearts-0.3.1/`, not `hearts/`.

## Common commands

### Build & run GNOME Hearts (legacy, containerized)

GNOME Hearts requires GTK2/libglade2/libgnomeui/Python2, none of which are installable on a modern
host. It's built inside a distrobox container running openSUSE Leap 15.4, whose repos still carry
these as ordinary packages, then exported to the host as a normal desktop app.

```sh
ansible-playbook ansible/gnome-hearts.yml
```

Requires Docker (running, user in the `docker` group) and `distrobox` already installed — the
playbook checks for both and stops with install instructions rather than installing them itself.
distrobox is pinned to the Docker backend (`DBX_CONTAINER_MANAGER=docker`) because rootless Podman
doesn't map some supplementary groups (e.g. `vboxusers`, for `/dev/vboxusb`) into its user
namespace, which breaks container start on systems that need those groups.

Run manually inside the container: `distrobox enter -n gnome-hearts -- gnome-hearts`

### Build & install Aisleriot (native)

```sh
ansible-playbook ansible/aisleriot.yml
```

Builds directly on the host with Meson/Ninja — no container needed, since Aisleriot's dependencies
(GTK3, glib, cairo, guile, librsvg, libcanberra) are all present as ordinary packages on a modern
distro. Requires the submodule checked out (`git submodule update --init aisleriot`) and
Meson/Ninja installed; the playbook checks for both and fails with instructions if missing, but does
not install anything itself. Installs to `/usr/local`; run manually as `/usr/local/bin/sol`.

Manual equivalent, for iterating without Ansible:
```sh
cd aisleriot
meson setup build -Dtheme_kde=false -Dtheme_pysol=false --prefix=/usr/local
ninja -C build
sudo ninja -C build install
```
(`-Dtheme_kde=false` is required on distros not in Aisleriot's hardcoded
`{centos,debian,fedora,opensuse,rhel,ubuntu}` KDE-theme-path map — e.g. Arch — otherwise `meson setup`
fails on an unresolvable KDE theme path assertion.)

### Build & run Hearts (native)

```sh
ansible-playbook ansible/hearts.yml
```

Builds directly on the host with Meson/Ninja/PyGObject (GTK4 + libadwaita) — no container needed.
Requires the `aisleriot` submodule checked out (its `anglo.svg` deck is reused as card art),
Meson/Ninja, and PyGObject with the GTK4/libadwaita/Rsvg typelibs; the playbook checks for all of
these and fails with instructions if anything's missing, but installs nothing itself. Installs to
`/usr/local`; run manually as `/usr/local/bin/hearts`.

Manual equivalent, for iterating without Ansible:
```sh
cd hearts
meson setup build
meson compile -C build
meson test -C build        # engine unit tests (pure Python, no display needed)
PYTHONPATH="$PWD" meson devenv -C build python3 -m hearts.main   # run uninstalled
sudo ninja -C build install
```

### Ansible playbook conventions

All three playbooks in `ansible/` follow the same shape — match it exactly when adding a new one:
- `hosts: localhost`, `connection: local`, `become: false` at the play level; `become: true` only on
  the individual task that needs root (typically just the final install step).
- Dependency checks never auto-install: run `<tool> --version`, `register: <x>_check`,
  `failed_when: false`, `changed_when: false`, then a following `ansible.builtin.fail` task gated on
  `when: <x>_check.rc != 0` with a message naming where to get the tool. This is deliberate — this
  repo doesn't assume any particular host package manager.
- Fully-qualified module names (`ansible.builtin.command`, not `command`).
- Idempotency via `args: creates: <path>` on configure/build steps; paths are computed relative to
  `{{ playbook_dir }}/../<dir>`, never hardcoded absolute paths.
- Variable names are prefixed per component (`gnome_hearts_*`, `aisleriot_*`, `hearts_*`).
- A final `ansible.builtin.debug` task named `"Done"` prints how to launch the app.
- `ansible/README.md` documents each playbook under its own `## <name>.yml` heading: what it does,
  requirements, and post-run instructions. Update it when adding or changing a playbook.

## Architecture notes

### GNOME Hearts (`gnome-hearts-0.3.1/`)

C core (GTK2 + libglade2 + libgnomeui) embeds a CPython interpreter to run AI opponent logic as
plain Python scripts, rather than implementing AI in C. `src/player-api.c` is the embedding glue;
`scripts/hearts.py` loads every `scripts/players/*.py` module and registers classes named
`PlayerAI*` as selectable opponents. Each such class implements a small contract — `select_cards()`
(pass 3 cards), `play_card()`, optional `receive_cards()`/`trick_end()`/`round_end()` — documented in
full (including the exact global helpers/filters/sorts exposed to player scripts, e.g. `f_hearts`,
`s_points`) in `docs/developer/README.md`. This scriptable-AI pattern is why the game is a fruitful
Python-embedding case study even though the rest of the engine is C.

Config lives in a keyfile at `~/.config/gnome-hearts/gnome-hearts.cfg` (ruleset choice + rule
toggles like `clubs_lead`, `hearts_break`, `no_blood`, `queen_breaks_hearts`) — see `cfg.c`/`cfg.h`
and `gnome-hearts.cfg.in` for the schema and defaults.

### Hearts (`hearts/`)

Same engine/rules-script split as GNOME Hearts and Aisleriot, but both halves are Python: a
`gi`-free `hearts/engine/` package (cards, deck, tricks, rules, scoring, and `game.py`'s
`HeartsGame` state machine — no display needed, covered by `meson test`) driven by a separate GTK4
UI layer (`application.py`, `window.py` + `hearts.ui`, `board_widget.py`, `card_renderer.py`,
`scores_dialog.py`). Rules toggles the original exposed (`clubs_lead`, `hearts_break`, `no_blood`,
`queen_breaks_hearts`) are hardcoded to their default-on values in `engine/rules.py` rather than
made configurable — that's a deliberate v1 scope cut, not an oversight.

`HeartsGame` drives AI turns synchronously and internally; the UI only calls `submit_pass()`/
`submit_play()` for the human seat (`HUMAN_SEAT` = South) and otherwise reacts to its callback
lists (`on_trick_complete`, `on_round_complete`, `on_game_complete`, `on_ai_turn`). Besides the
current-round `round_scores()`/`round_point_cards()`, `HeartsGame` also keeps `score_history()`, a
list of every completed round's scores (oldest first) — `scores_dialog.py`'s score sheet replays
this to show, per seat, the running total after each round, with superseded totals struck through.
Between rounds (`Phase.ROUND_OVER`) nothing advances automatically — `board_widget.py` treats any
click on the table as "deal the next round" (`game.start_round()`); there's no separate "Continue"
button. `window.py` auto-presents the Scores dialog as soon as a round ends, and `board_widget.py`
fans out the point cards (hearts + Queen of Spades) each seat took in that round in their now-empty
hand spot, visible on the table behind the dialog until the next round is dealt.

`board_widget.py` is a single `Gtk.DrawingArea` (raw Cairo draw callback + `Gtk.GestureClick`), not
one widget per card — matching Aisleriot's own single-canvas approach, since GTK4's snapshot/
`Gdk.Texture` machinery isn't the natural fit for a plain `DrawingArea`. `card_renderer.py` caches
rendered cards as `cairo.ImageSurface` (not `Gdk.Texture`, for the same reason) keyed by
`(svg_element_id, pixel_height)`, rendered via `Rsvg.Handle.render_element()` against
`anglo.svg`'s per-card element ids (`<suit>_<rank>`, e.g. `heart_queen`, ace = `1`). It also draws
each seat's player name and, when a play is attempted outside `rules.legal_plays()`,
`rules.explain_illegal_play()` supplies the human-readable reason surfaced via `on_warning` into
`window.py`'s status label rather than the move just silently failing.

`Adw.Dialog` (used by `scores_dialog.py`, and any future dialog) has no titlebar/close button by
default — one only appears if the dialog's content includes a header bar, same as
`Adw.ApplicationWindow`. Without an `Adw.ToolbarView` wrapping an `Adw.HeaderBar` around the
content, Esc is the only way to close it.

The card SVG and the `pkgdatadir` it's installed under are resolved at build time in
`data/meson.build`/`hearts/meson.build` (a generated `hearts/config.py` — gitignored, never
committed — carries the installed `pkgdatadir` path); `card_renderer.find_cards_svg()` falls back
to a path relative to its own source location (the `aisleriot` submodule checkout) when `config.py`
doesn't exist, which is what makes `meson devenv`/uninstalled runs work without installing first.

The version lives in exactly one place, `project('hearts', version: ...)` in `hearts/meson.build`;
everything else reads it rather than repeating the string (that duplication is exactly how the
app-id/`gnome-hearts` icon-name drift from issue #9 happened — the About dialog and `.desktop` file
each hardcoded the icon name separately, and only one of them got updated). `config.py.in` carries
the version into `application.py` (`config.version`, same generated-file/fallback pattern as
`pkgdatadir` above) for the About dialog, and `data/meson.build` substitutes it into
`com.linuxkamarada.Hearts.metainfo.xml.in`'s `<release version="@version@">` — bump it in
`meson.build` only, and update the `pkgver`/`_pkgtag` pair in `packaging/archlinux/PKGBUILD` to match
for the next release.

The application ID is `com.linuxkamarada.Hearts` (`application.py`'s `APPLICATION_ID`, matching the
`.desktop`/`.gschema.xml`/`.metainfo.xml.in` filenames and each file's own `id`/`path`/`launchable`
fields) rather than `org.gnome.Hearts` — deliberately not under the `org.gnome.*` namespace, since
that's reserved for apps GNOME itself has accepted (e.g. into GNOME Circle), which this hasn't been
submitted for yet.

### Packaging (`packaging/`)

`packaging/archlinux/PKGBUILD` builds only the `hearts/` subdirectory of this monorepo (fetched via
a pinned git tag), not `gnome-hearts-0.3.1/` or `aisleriot/`. Since makepkg's git source doesn't
follow submodules, `anglo.svg` is fetched separately, straight from the `aisleriot` GNOME repo at
the exact commit the submodule pointer resolves to, and handed to Meson via `-Dcards_svg=...`
(`hearts/meson_options.txt`) instead of needing the submodule at all. See `packaging/README.md`.

### Aisleriot (`aisleriot/`)

Reference architecture worth knowing when reasoning about this repo's conventions: a C/GObject
engine (rendering, board state, event dispatch, `src/`) with per-game rules written in Scheme
(`games/*.scm`, driven through a narrow primitive API in `games/api.scm`) — an engine/rules-script
split analogous to GNOME Hearts' C-engine/Python-AI split. Uses Meson+Ninja; GTK3 (not GTK4); a mix
of modern (`GSimpleAction`/`GActionEntry`) and legacy (`GtkUIManager` XML menus, GConf for most
settings aside from one real GSettings schema for window state) GNOME conventions — treat the
legacy parts as things *not* to imitate in new code, not as house style.
