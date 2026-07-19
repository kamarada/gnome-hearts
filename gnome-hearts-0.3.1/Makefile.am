## Process this file with automake to produce Makefile.in

SUBDIRS = help man pixmaps po scripts src

desktopdir = $(datadir)/applications/
desktop_in_files = gnome-hearts.desktop.in
desktop_DATA = $(desktop_in_files:.desktop.in=.desktop)
@INTLTOOL_DESKTOP_RULE@

EXTRA_DIST = \
	gnome-hearts.desktop.in \
	intltool-extract.in \
	intltool-merge.in \
	intltool-update.in \
	xmldocs.make \
	omf.make \
	COPYING-DOCS

DISTCLEANFILES = \
	gnome-hearts.desktop \
	intltool-extract \
	intltool-merge \
	intltool-update
	
