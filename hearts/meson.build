project('hearts', version: '0.4.0-beta', meson_version: '>= 0.62.0')

fs = import('fs')
python = import('python')
gnome = import('gnome')
i18n = import('i18n')

py_installation = python.find_installation('python3')

prefix = get_option('prefix')
hearts_pkgdatadir = get_option('datadir') / 'hearts'
hearts_bindir = get_option('bindir')

subdir('data')
subdir('hearts')
subdir('tests')

launcher_conf = configuration_data()
launcher_conf.set('PYTHON', py_installation.full_path())
launcher_conf.set('pythondir', py_installation.get_install_dir())
launcher = configure_file(
  input: 'hearts.in',
  output: 'hearts-launcher',
  configuration: launcher_conf,
)
install_data(
  launcher,
  install_dir: hearts_bindir,
  install_mode: 'rwxr-xr-x',
  rename: 'hearts',
)

gnome.post_install(glib_compile_schemas: true)
