/*
 *  Hearts - background.c
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

#include <glib.h>
#include <gtk/gtk.h>
#include <glade/glade.h>
#include "background.h"
#include "cfg.h"
#include "ui.h"

Background bg;

/* Load background from path */
void background_load(gchar* file)
{
	GError *error = NULL;
	
	bg.original = gdk_pixbuf_new_from_file(file, &error);
	
	if (bg.original == NULL)
	{
		printf("**Error**: %s", error->message);
		g_assert_not_reached();
	}
	
	background_flush(TRUE);
}

/* Flush the background, applying stretch/tile and size settings */
void background_flush(gboolean force)
{
	/* Force new background creation */
	if (force)
	{
		if (bg.gc)
		{
			g_object_unref(bg.gc);
			bg.gc = NULL;
		}
		
		if (bg.scaled)
		{
			g_object_unref(bg.scaled);
			bg.scaled = NULL;
		}
	}
	
	/* Create a gc to paint a tiled background */
	if (cfg.background_tiled)
	{
		if (bg.gc)
			return;
		
		if (bg.scaled)
		{
			g_object_unref(bg.scaled);
			bg.scaled = NULL;
		}
		
		GdkPixmap *tile;
		GtkWidget *playingarea_widget = glade_xml_get_widget (ui.xml, "playingarea");
		
		gdk_pixbuf_render_pixmap_and_mask_for_colormap (bg.original, gdk_colormap_get_system(), &tile, NULL, 127);
		bg.gc = gdk_gc_new(playingarea_widget->window);
		gdk_gc_set_tile(bg.gc, tile);
		gdk_gc_set_fill(bg.gc, GDK_TILED);
		g_object_unref(tile);
		return;
	}
	
	/* Draw a scaled background */
	if (bg.gc)
	{
		g_object_unref(bg.gc);
		bg.gc = NULL;
	}
	
	/* rescale the background if necessary */
	GtkWidget *widget = glade_xml_get_widget(ui.xml, "playingarea");
	if (bg.scaled == NULL || widget->allocation.width != gdk_pixbuf_get_width(bg.scaled) || widget->allocation.height != gdk_pixbuf_get_height(bg.scaled))
	{
		if (bg.scaled)
			g_object_unref(bg.scaled);
		
		bg.scaled = gdk_pixbuf_scale_simple(bg.original, widget->allocation.width, widget->allocation.height, GDK_INTERP_BILINEAR);
	}
}

/* Render part of the background to a GdkPixmap */
void background_render(GdkPixmap *target, gint x, gint y, gint width, gint height)
{
	if (bg.scaled)
	{
		gdk_draw_pixbuf(target, bg.gc, bg.scaled,
			x, y,
			x, y,
			width, height,
			GDK_RGB_DITHER_NONE,
			0, 0);
		return;
	}

	gdk_draw_rectangle(target, bg.gc, TRUE, x, y, width, height);
}

/* free the background */
void background_free(void)
{
	if (bg.original) g_object_unref(bg.original);
	if (bg.scaled) g_object_unref(bg.scaled);
	if (bg.gc) g_object_unref(bg.gc);
}
