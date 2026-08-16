#!/usr/bin/env bash
# Builds Hearts as an AppImage (issue #13). See ../README.md for what this
# does and doesn't bundle, and its build-host caveats (glibc compatibility
# in particular). Run from anywhere; all paths below are relative to this
# script's own location.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HEARTS_SRC="$REPO_ROOT/hearts"

BUILD_DIR="$SCRIPT_DIR/build"
APPDIR="$SCRIPT_DIR/AppDir"
TOOLS_DIR="$SCRIPT_DIR/.tools"
APP_ID="com.linuxkamarada.Hearts"

mkdir -p "$TOOLS_DIR"

# -- preflight ---------------------------------------------------------

for tool in meson ninja curl python3; do
  if ! command -v "$tool" >/dev/null; then
    echo "error: '$tool' not found -- install it and try again." >&2
    exit 1
  fi
done

# -- fetch linuxdeploy/appimagetool (cached in .tools/, gitignored) ------
#
# Both are distributed upstream only as rolling "continuous" builds (no
# stable pinned releases exist for either) -- this is the officially
# documented way to obtain them, not a shortcut on our part. Re-run with
# an empty .tools/ dir to pick up newer builds.

fetch() {
  local dest="$1" url="$2"
  if [ ! -x "$dest" ]; then
    echo "Downloading $(basename "$dest")..."
    curl -sL -o "$dest" "$url"
    chmod +x "$dest"
  fi
}

fetch "$TOOLS_DIR/linuxdeploy" \
  "https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage"
fetch "$TOOLS_DIR/linuxdeploy-plugin-gtk.sh" \
  "https://raw.githubusercontent.com/linuxdeploy/linuxdeploy-plugin-gtk/master/linuxdeploy-plugin-gtk.sh"
fetch "$TOOLS_DIR/appimagetool" \
  "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"

# Sandboxed/CI builders often lack FUSE (needed to mount an AppImage the
# normal way); this makes linuxdeploy/appimagetool extract-and-run instead,
# which works everywhere FUSE does too, just slightly slower.
export APPIMAGE_EXTRACT_AND_RUN=1

# -- build hearts/ into a clean /usr-prefixed AppDir ---------------------
#
# Not hearts/build/ (that one's prefix=/usr/local, for a normal host
# install -- see hearts/README.md) -- AppImages are conventionally laid
# out as if installed to /usr, same as packaging/archlinux/PKGBUILD.

rm -rf "$APPDIR"
meson setup "$BUILD_DIR" "$HEARTS_SRC" --prefix=/usr --wipe
meson compile -C "$BUILD_DIR"
meson install -C "$BUILD_DIR" --destdir "$APPDIR"

VERSION="$(python3 -c "
import json, subprocess
info = json.loads(subprocess.check_output(['meson', 'introspect', '$BUILD_DIR', '--projectinfo']))
print(info['version'])
")"

# -- bundle the GTK4/libadwaita/librsvg runtime --------------------------
#
# DEPLOY_GTK_VERSION=4: the gtk plugin normally auto-detects this by
# inspecting the app's main ELF executable, but hearts' is a Python script
# (usr/bin/hearts), not ELF, so auto-detection fails without this.
#
# -l .../libadwaita-1.so.0: linuxdeploy only auto-bundles a library if it's
# an ELF dependency of something already in AppDir, or reachable from
# there by scanning -- libadwaita isn't a dependency of libgtk-4.so.1
# itself (Hearts only reaches it dynamically, via gi.require_version()),
# so without this it's silently left out, and Hearts would fall back to
# (and possibly break against) whatever libadwaita the host happens to
# have, defeating the bundling entirely. Verified by checking
# /proc/<pid>/maps of a running instance -- see ../README.md.
DEPLOY_GTK_VERSION=4 "$TOOLS_DIR/linuxdeploy" \
  --appdir "$APPDIR" \
  --library "$(pkg-config --variable=libdir libadwaita-1)/libadwaita-1.so.0" \
  --desktop-file "$APPDIR/usr/share/applications/$APP_ID.desktop" \
  --icon-file "$APPDIR/usr/share/icons/hicolor/256x256/apps/gnome-hearts.png" \
  --plugin gtk

# Overwrite linuxdeploy's default AppRun (which just execs
# usr/bin/hearts directly -- see AppRun's own header comment for why that
# doesn't work here) with ours.
install -m755 "$SCRIPT_DIR/AppRun" "$APPDIR/AppRun"

# -- package --------------------------------------------------------------

OUTPUT="$SCRIPT_DIR/Hearts-${VERSION}-x86_64.AppImage"
rm -f "$OUTPUT"
ARCH=x86_64 "$TOOLS_DIR/appimagetool" "$APPDIR" "$OUTPUT"

echo
echo "Built $OUTPUT"
