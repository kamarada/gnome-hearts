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

## AppImage (`appimage/build-appimage.sh`)

A self-contained `.AppImage` build. Unlike the Arch package above, `build-appimage.sh` works from
this working tree directly (no git tag needed) and needs nothing installed beyond `meson`, `ninja`,
`curl`, and `python3`:

```sh
packaging/appimage/build-appimage.sh
```

Produces `packaging/appimage/Hearts-<version>-x86_64.AppImage` (gitignored, along with the
intermediate `AppDir/`, `build/`, and `.tools/` the script creates alongside it).

### Scope: what's bundled, what isn't

It bundles GTK4, libadwaita, librsvg and their own runtime data (icon theme, GSettings schemas,
gdk-pixbuf loaders, typelibs) via [linuxdeploy](https://github.com/linuxdeploy/linuxdeploy) and its
`gtk` plugin -- but **not** Python or PyGObject (the `gi` module) themselves. The AppImage's own
`AppRun` execs the *host's* `python3 -m hearts.main`, with `PYTHONPATH` pointing at the bundled
`hearts` package.

This was a deliberate tradeoff, not an oversight: fully bundling a relocatable CPython plus a
PyGObject rebuilt against the bundled GTK/glib is a much bigger, more fragile undertaking (compiled
extension-module ABI compatibility across host distros, no realistic way to test that from a single
dev machine) for comparatively little benefit, since python3-gi is close to a given on any GTK-based
Linux desktop already. If that tradeoff ever needs revisiting, start from `AppRun`'s own comments.

### Two non-obvious things `build-appimage.sh` does, and why

- `DEPLOY_GTK_VERSION=4` -- the `gtk` plugin normally auto-detects the GTK version by inspecting the
  app's main ELF executable, but `usr/bin/hearts` is a Python script, not ELF, so auto-detection
  fails without this.
- `--library .../libadwaita-1.so.0` -- linuxdeploy only auto-bundles a library that's an ELF
  dependency of something already in `AppDir`, or otherwise reachable by its own scanning. libadwaita
  isn't a dependency of `libgtk-4.so.1` itself -- Hearts only reaches it dynamically, through
  `gi.require_version("Adw", "1")` -- so without this flag it's silently left out, and the app falls
  back to (and depending on the host, breaks against) whatever libadwaita the host happens to have,
  defeating the bundling. Caught by checking a running instance's `/proc/<pid>/maps` for which copy
  of `libadwaita-1.so.0`/`libgtk-4.so.1` actually got mapped in -- worth re-checking the same way
  after any change here, since this class of gap (a library only ever `dlopen()`d by name, never
  linked) is exactly what auto-detection tends to miss silently.

### Build-host caveat

AppImages are conventionally built on an old baseline distro (e.g. Ubuntu 20.04/22.04) specifically
to maximize glibc-compatibility with older target systems -- building on a bleeding-edge host instead
produces an AppImage that only *runs* on systems with an equally new (or newer) glibc, which mostly
defeats the point for a general-purpose release artifact. This script doesn't enforce that itself;
for an actual release build, run it inside a suitably old container (`ansible/gnome-hearts.yml`'s
distrobox/openSUSE setup is this repo's existing precedent for that kind of thing, though AppImage
recipes upstream more commonly use Ubuntu).

## Flatpak (`flatpak/com.linuxkamarada.Hearts.json`)

A Flatpak manifest, built with [Flatter](https://github.com/andyholmes/flatter) and published to a
self-hosted Flatpak repo on GitHub Pages via `.github/workflows/flatpak.yml`. The workflow only
runs on `v*` tags (or manual `workflow_dispatch`) -- same release cadence as the Arch package -- and
the published repo is unsigned, served over plain HTTPS.

Like the Arch `PKGBUILD`, the manifest fetches the monorepo via a pinned git `tag` (kept in step
with `_pkgtag` above) and builds only the `hearts/` subdirectory (via the module's `subdir` key).
Unlike makepkg, `flatpak-builder` *does* follow git submodules by default, so the `aisleriot`
submodule (and its `anglo.svg` card art) comes along with the git source automatically -- no
separate `anglo.svg` fetch or `-Dcards_svg=...` override needed, unlike the Arch package.

Flatpak only exports an icon whose filename matches the app's icon theme name, but Hearts' desktop
file uses `Icon=gnome-hearts` with icon files named `gnome-hearts.*` (see `hearts/data/`) rather
than the app-id -- so the manifest's `post-install` step copies each hicolor PNG icon to a
`com.linuxkamarada.Hearts.png`-named copy and rewrites the installed desktop file's `Icon=` line to
match, Flatpak-side only (the shared `hearts/data/` build used by Arch/AppImage is untouched). The
scalable SVG is deliberately *not* copied/exported this way: `flatpak build-export`'s icon validator
fails on any SVG (not just this one) on at least one tested host, due to its sandbox not exposing a
working fontconfig to the SVG rasterizer -- a host/Flatpak-level bug, not a defect in this icon.
PNG-only (up to 256x256) is exported instead, which covers normal desktop/icon-theme lookups fine.

The `ghcr.io/andyholmes/flatter/gnome` container image only pre-installs the GNOME *nightly*
runtime/SDK (branch `master`), not a numbered stable version -- so `.github/workflows/flatpak.yml`
has an explicit `flatpak install ... org.gnome.Sdk//50 org.gnome.Platform//50` step (from the
`flathub` remote, already configured in that image) before invoking Flatter, matching the
`runtime-version` pinned in the manifest. Bump both together if the manifest's `runtime-version`
ever changes.

### Building and testing locally

Requires `flatpak`, `flatpak-builder`, and the `org.gnome.Platform`/`org.gnome.Sdk` runtime+SDK
installed locally (matching `runtime-version` in the manifest):

```sh
flatpak-builder --force-clean --user --install build-dir packaging/flatpak/com.linuxkamarada.Hearts.json
flatpak run com.linuxkamarada.Hearts
```

### Installing from the published repo

See the top-level `README.md` for end-user install instructions once the repo has been published
via the GitHub Actions workflow (which also requires GitHub Pages to be enabled for this repository,
with its source set to "GitHub Actions", in the repo's Settings).
