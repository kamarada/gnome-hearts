## Process this file with automake to produce Makefile.in

gnome_heartsdir = $(datadir)/gnome-hearts
gnome_hearts_DATA = gnome-hearts.glade gnome-hearts.cfg

AM_CPPFLAGS = $(GNOME_HEARTS_CFLAGS) $(PYTHON_CFLAGS)

AM_CFLAGS =\
	 -Wall\
	 -g

bin_PROGRAMS = gnome-hearts

gnome_hearts_SOURCES = \
	hearts.c\
	hearts.h\
	background.c\
	background.h\
	cards.c\
	cards.h\
	cards-image.c\
	cards-image.h\
	cfg.c\
	cfg.h\
	events.c\
	events.h\
	gettext.h\
	player-api.c\
	player-api.h\
	player.c\
	player.h\
	preimage.c\
	preimage.h\
	ui.c\
	ui.h

gnome_hearts_LDADD =  \
	$(GNOME_HEARTS_LIBS) $(PYTHON_LIBS)

EXTRA_DIST = $(gnome_hearts_DATA)
