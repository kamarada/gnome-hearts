# Installs Hearts' icon (data/icons/gnome-hearts.svg, rendered to the PNG
# sizes below) into the standard hicolor icon theme directory, so it's
# resolvable by name ("gnome-hearts") through the system's icon theme --
# e.g. by Adw.AboutDialog's application_icon, same as Aisleriot's own
# "gnome-aisleriot" icon (see ../../../aisleriot/data/icons/meson.build,
# which this mirrors).
#
# Source filenames encode their install location as
# hicolor_<context>_<size>_<icon-name>, decoded below into
# <context>/<size>/<icon-name> under the hicolor theme dir.

icon_sources = [
  'hicolor_apps_16x16_gnome-hearts.png',
  'hicolor_apps_22x22_gnome-hearts.png',
  'hicolor_apps_24x24_gnome-hearts.png',
  'hicolor_apps_32x32_gnome-hearts.png',
  'hicolor_apps_40x40_gnome-hearts.png',
  'hicolor_apps_48x48_gnome-hearts.png',
  'hicolor_apps_256x256_gnome-hearts.png',
  'hicolor_apps_scalable_gnome-hearts.svg',
]

icon_renames = []
foreach icon : icon_sources
  components = icon.split('_')
  icon_renames += components[0] / components[2] / components[1] / components[3]
endforeach

icondir = get_option('datadir') / 'icons'

install_data(
  sources: icon_sources,
  rename: icon_renames,
  install_dir: icondir,
)

# Refresh the icon cache after install so the new icon is resolvable
# immediately, without waiting for the next login/cache rebuild.
meson.add_install_script(
  'meson_updateiconcache.py',
  icondir / 'hicolor',
)
