/*
 *  Hearts - ui.h
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

#ifndef UI_H
#define UI_H

#include <glib.h>
#include <gtk/gtk.h>
#include <glade/glade.h>

#include "cards-image.h"

/* A player AI script */
typedef struct _AIScript
{
	gchar *name;
	gchar *class;
} AIScript;

/* A card style */
typedef struct _CardStyle
{
	gchar *name;
	gchar *path;
} CardStyle;

/* The user interface global */
typedef struct _UserInterface
{
	/* The UI root */
	GladeXML *xml;

	/* The table drawing area */
	
	GdkPixmap *backbuffer;
	GdkGC * backbuffer_gc;

	/* mapping names to objects */
	GList *ai_scripts;
	GList *card_styles;

	/* Card style filter */	
	GtkFileFilter *filter;
	
	/* The score table */
	GPtrArray *scores;
	PangoAttrList *strike;
	
	/* The cards image */
	CardsImage *cards_image;
} UserInterface;

extern UserInterface ui;

void ui_load(void);
void ui_start(void);
void ui_set_config(void);
void ui_add_ai_script(gchar *name, gchar *class);
void ui_add_card_style(gchar *name, gchar *class);
void ui_add_score_row(gint north, gint east, gint south, gint west);
void ui_draw_playingarea(void);
void ui_free(void);

#endif
