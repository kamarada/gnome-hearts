# Build playbooks

Two playbooks, one per game in this repo. Both just need:

```sh
ansible-playbook <playbook>.yml
```

## gnome-hearts.yml

Builds and installs GNOME Hearts 0.3.1 from the `gnome-hearts-0.3.1/`
source tree in this repo, targeting a modern Linux desktop that no
longer ships GTK2/libglade2/Python 2 as installable packages.

It works around that by creating an [openSUSE Leap 15.4](https://get.opensuse.org/leap/)
[distrobox](https://distrobox.it/) container (openSUSE Leap 15.4 still
carries `gtk2-devel`, `libglade2-devel`, `libgnomeui-devel` and
`python-devel` 2.7 as ordinary packages), compiling the game inside it,
and exporting it as a regular application on the host desktop.

Requirements:

- [Docker](https://docs.docker.com/engine/install/), running, with your
  user in the `docker` group
- [distrobox](https://distrobox.it/#installation)

The playbook checks for Docker and distrobox and stops with instructions
if either is missing — it does not install them itself, since the right
way to do so depends on your distribution.

Once it finishes, look for **"Hearts (on gnome-hearts)"** in your
application launcher, or run:

```sh
distrobox enter -n gnome-hearts -- gnome-hearts
```

## aisleriot.yml

Builds and installs [Aisleriot](https://gitlab.gnome.org/GNOME/aisleriot),
the `aisleriot` git submodule at the repo root. Unlike GNOME Hearts, it's
an actively maintained GTK3/Meson project with no legacy toolkit
dependencies, so it's built directly on the host — no container needed.

Requirements:

- The `aisleriot` submodule checked out (`git submodule update --init
  aisleriot` from the repo root)
- [Meson](https://mesonbuild.com/Getting-meson.html) and
  [Ninja](https://ninja-build.org/)
- A C/C++ compiler, `pkg-config`, `guile` (3.0/2.2/2.0), and the
  development files for `glib-2.0`, `gio-2.0`, `cairo`, `gtk+-3.0`,
  `librsvg-2.0` and `libcanberra-gtk3`, plus the `itstool`, `xmllint` and
  `gzip` programs

The playbook checks for Meson, Ninja and the submodule and stops with
instructions if any are missing. The rest of the dependencies above are
validated by `meson setup` itself — if a library is missing, its error
will name which one; install the matching package for your distribution
and re-run the playbook. It does not install any of these itself, since
package names and installation vary by distribution.

Once it finishes, look for **"AisleRiot Solitaire"** in your application
launcher, or run:

```sh
/usr/local/bin/sol
```
