# Packaging

Distro packaging metadata for Hearts (`hearts/`), one directory per distro/format, mirroring how
`ansible/` holds one playbook per buildable component.

## Arch Linux (`archlinux/PKGBUILD`)

A standard `PKGBUILD`, written so it's ready to seed an AUR submission (`ssh://aur@aur.archlinux.org/hearts.git`)
once this project has an actual tagged release. It:

- Fetches the `kamarada/gnome-hearts` monorepo at a git tag (`_pkgtag`, currently `v0.4.0-beta`) and
  builds only the `hearts/` subdirectory.
- Fetches `anglo.svg` (the card art) directly from the `aisleriot` GNOME repo at the exact commit the
  `aisleriot` submodule pointer resolves to for that tag, rather than pulling in the whole submodule
  — makepkg's git source support doesn't follow submodules, and the card art is all `hearts/` actually
  needs from it. Passed to Meson via `-Dcards_svg=...` (see `hearts/meson_options.txt`).
- Uses `arch-meson` (from the `meson` package) for the standard Arch Meson build flags, builds,
  runs the engine unit tests (`meson test`), and installs via `meson install --destdir`.

**Before this can build**, a `v0.4.0-beta` git tag needs to exist on `kamarada/gnome-hearts` (and, if
the `aisleriot` submodule pointer moves before then, `_anglo_commit` in the `PKGBUILD` needs updating
to match). Update `_pkgtag`/`pkgver` together for future releases.

### Building and testing locally

```sh
cd packaging/archlinux
makepkg -si          # build and install; -s pulls in makedepends via pacman
```

Without a real tag yet, iterate on the Meson side directly instead (see `../../hearts/README.md`);
`packaging/archlinux/PKGBUILD`'s `build()`/`check()`/`package()` steps are just `arch-meson` +
`meson compile` + `meson test` + `meson install --destdir`, so anything that works there will work
here once the tag exists.

To regenerate `.SRCINFO` for an actual AUR push (not committed to this repo -- it belongs in the AUR
git repo, generated from this `PKGBUILD`):

```sh
cd packaging/archlinux
makepkg --printsrcinfo > .SRCINFO
```
