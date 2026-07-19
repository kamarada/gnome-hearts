/*
 *  Hearts - cfg.h
 *  Copyright 2006 Sander Marechal
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 */
 
#ifndef CFG_H
#define CFG_H

#include <glib.h>

/* The Config object holds all of the game's configuration settings */
typedef struct _Config
{
	/* General configuration options. */
	gchar *config_path;
	gchar *config_file;
	gint ruleset;
	gboolean clubs_lead;
	gboolean hearts_break;
	gboolean no_blood;
	gboolean queen_breaks_hearts;
	gboolean show_scores;
	gchar *north_ai;
	gchar *east_ai;
	gchar *west_ai;
	gchar *card_style;
	gchar *background_image;
	gboolean background_tiled;

	/* These options are only accessible from the commandline. */
	gboolean show_cards;
} Config;

extern Config cfg;

void config_load(void);
void config_save(void);
void config_publish(void);
void config_free(void);

#endif
