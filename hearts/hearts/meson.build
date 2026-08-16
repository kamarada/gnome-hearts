hearts_sources = files(
  '__init__.py',
  'application.py',
  'board_widget.py',
  'card_renderer.py',
  'main.py',
  'scores_dialog.py',
  'window.py',
)

py_installation.install_sources(hearts_sources, subdir: 'hearts')

install_data('hearts.ui', install_dir: py_installation.get_install_dir() / 'hearts')

conf = configuration_data()
conf.set('pkgdatadir', prefix / hearts_pkgdatadir)
conf.set('version', meson.project_version())
configure_file(
  input: 'config.py.in',
  output: 'config.py',
  configuration: conf,
  install: true,
  install_dir: py_installation.get_install_dir() / 'hearts',
)

subdir('engine')
