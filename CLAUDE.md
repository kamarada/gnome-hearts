# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository overview

This repo (`kamarada/gnome-hearts`) hosts GNOME Hearts, an old (2013) GTK2/libglade2/Python2 card
game, plus the infrastructure to keep it running on modern systems, and a git submodule of GNOME's
actively-maintained Aisleriot card game collection used as a build/architecture reference.

- `gnome-hearts-0.3.1/` — the original upstream source (autotools, C core + embedded Python2 AI
  scripts). **Do not modify anything here** — it's an unaltered vendor drop (see `docs/developer/`
  for its own architecture notes). It cannot be built directly on a modern Arch host: GTK2,
  libglade2, libgnomeui and Python 2 are no longer packaged. It builds and runs only inside a
  container — see below.
- `aisleriot/` — git submodule (`https://gitlab.gnome.org/GNOME/aisleriot.git`), GNOME's modern
  GTK3/Meson solitaire collection. Builds natively on the host (no container needed). Also the
  source of the `anglo.svg` card deck asset reused elsewhere in this repo. **Do not modify.**
- `ansible/` — one playbook per buildable component (see below).
- `docs/user/`, `docs/developer/` — archived Markdown mirrors of the original project's user and
  developer documentation from jejik.com (the upstream site), preserved verbatim including its
  original wording/typos, since jejik.com is the only remaining source for these docs.

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

### Ansible playbook conventions

Both playbooks in `ansible/` follow the same shape — match it exactly when adding a new one:
- `hosts: localhost`, `connection: local`, `become: false` at the play level; `become: true` only on
  the individual task that needs root (typically just the final install step).
- Dependency checks never auto-install: run `<tool> --version`, `register: <x>_check`,
  `failed_when: false`, `changed_when: false`, then a following `ansible.builtin.fail` task gated on
  `when: <x>_check.rc != 0` with a message naming where to get the tool. This is deliberate — this
  repo doesn't assume any particular host package manager.
- Fully-qualified module names (`ansible.builtin.command`, not `command`).
- Idempotency via `args: creates: <path>` on configure/build steps; paths are computed relative to
  `{{ playbook_dir }}/../<dir>`, never hardcoded absolute paths.
- Variable names are prefixed per component (`gnome_hearts_*`, `aisleriot_*`).
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

### Aisleriot (`aisleriot/`)

Reference architecture worth knowing when reasoning about this repo's conventions: a C/GObject
engine (rendering, board state, event dispatch, `src/`) with per-game rules written in Scheme
(`games/*.scm`, driven through a narrow primitive API in `games/api.scm`) — an engine/rules-script
split analogous to GNOME Hearts' C-engine/Python-AI split. Uses Meson+Ninja; GTK3 (not GTK4); a mix
of modern (`GSimpleAction`/`GActionEntry`) and legacy (`GtkUIManager` XML menus, GConf for most
settings aside from one real GSettings schema for window state) GNOME conventions — treat the
legacy parts as things *not* to imitate in new code, not as house style.
