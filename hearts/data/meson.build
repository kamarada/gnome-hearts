desktop_file = configure_file(
  input: 'org.gnome.Hearts.desktop.in',
  output: 'org.gnome.Hearts.desktop',
  copy: true,
)
install_data(desktop_file, install_dir: get_option('datadir') / 'applications')

metainfo_file = configure_file(
  input: 'org.gnome.Hearts.metainfo.xml.in',
  output: 'org.gnome.Hearts.metainfo.xml',
  copy: true,
)
install_data(metainfo_file, install_dir: get_option('datadir') / 'metainfo')

install_data(
  'org.gnome.Hearts.gschema.xml',
  install_dir: get_option('datadir') / 'glib-2.0' / 'schemas',
)

# Also compile the schema into the build directory itself (not just at
# install time) and register it with `meson devenv`, so the app can be run
# straight from the build tree without installing first.
gnome.compile_schemas(
  build_by_default: true,
  depend_files: files('org.gnome.Hearts.gschema.xml'),
)

subdir('icons')

# Card art: reuse the SVG deck already vendored by the aisleriot submodule
# rather than bundling our own art. Not committed to git under hearts/.
cards_svg = get_option('cards_svg')
if cards_svg == ''
  cards_svg = meson.project_source_root() / '..' / 'aisleriot' / 'cards' / 'anglo.svg'
endif
if not fs.exists(cards_svg)
  error(
    'Card SVG not found at @0@. Run `git submodule update --init aisleriot` at the repo root, or pass -Dcards_svg=<path>.'.format(
      cards_svg,
    ),
  )
endif
install_data(cards_svg, install_dir: hearts_pkgdatadir / 'cards', rename: 'anglo.svg')
