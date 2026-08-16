# GNOME Hearts

This repo hosts [GNOME Hearts](https://www.jejik.com/gnome-hearts/), an old
(2013) GTK2/libglade2/Python2 Hearts card game; `hearts/`, a from-scratch
modern rewrite of it; the infrastructure to keep the original running on
modern systems; and a git submodule of GNOME's actively-maintained
[Aisleriot](https://gitlab.gnome.org/GNOME/aisleriot) card game collection,
used as a build/architecture reference for both.

- `gnome-hearts-0.3.1/` — the original upstream source (autotools, C core +
  embedded Python2 AI scripts). See `docs/user/` and `docs/developer/` for
  its archived documentation.
- `hearts/` — a from-scratch rewrite of the same game in Python, GTK4 and
  libadwaita, built and run natively (no container). Implements the
  Standard ruleset only — see `hearts/README.md` for exact scope.
- `aisleriot/` — git submodule, GNOME's modern GTK3/Meson solitaire
  collection, used as an architecture reference and as the source of the
  `anglo.svg` card art reused by `hearts/`.
- `ansible/` — one playbook per buildable component.
- `packaging/` — distro packaging metadata, one directory per distro/format (currently just an Arch
  Linux `PKGBUILD` for `hearts/`).

## Building and running

### Hearts (native, recommended)

The modern rewrite, playable against 3 AI opponents.

```sh
ansible-playbook ansible/hearts.yml
```

or manually:

```sh
cd hearts
meson setup build
meson compile -C build
meson test -C build        # engine unit tests (pure Python, no display needed)
sudo ninja -C build install
hearts
```

To run without installing:

```sh
cd hearts
PYTHONPATH="$PWD" meson devenv -C build python3 -m hearts.main
```

Requires the `aisleriot` submodule checked out (`git submodule update
--init aisleriot`) for its card art, plus Meson, Ninja, Python 3, and
PyGObject with the GTK4/libadwaita/Rsvg typelibs. See `hearts/README.md`
and `ansible/README.md` for details and exact package names per
distribution.

### GNOME Hearts (legacy, containerized)

The original game. Requires GTK2/libglade2/libgnomeui/Python2, none of
which are installable on a modern host, so it's built inside a distrobox
container and exported to the host as a normal desktop app.

```sh
ansible-playbook ansible/gnome-hearts.yml
```

Requires Docker (running, user in the `docker` group) and `distrobox`
already installed. Run manually inside the container:

```sh
distrobox enter -n gnome-hearts -- gnome-hearts
```

### Aisleriot

```sh
ansible-playbook ansible/aisleriot.yml
```

or manually:

```sh
cd aisleriot
meson setup build -Dtheme_kde=false -Dtheme_pysol=false --prefix=/usr/local
ninja -C build
sudo ninja -C build install
sol
```

Requires the `aisleriot` submodule checked out and Meson/Ninja installed.

See `ansible/README.md` for full requirements and options for all three
playbooks.

### Hearts (Arch Linux package)

```sh
cd packaging/archlinux
makepkg -si
```

See `packaging/README.md`.

### Hearts (AppImage)

```sh
packaging/appimage/build-appimage.sh
```

Produces `packaging/appimage/Hearts-<version>-x86_64.AppImage` -- a self-contained build (bundles
GTK4/libadwaita/librsvg; still needs the host's Python 3 + PyGObject). See `packaging/README.md`.
