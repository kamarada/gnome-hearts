/*
 *  Hearts - cards-image.c
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
 *
 *  Some inspiration from this came from the Aisleriot game written by 
 *  Jonathan Blandford <jrb@mit.edu> and released under the GNU GPL.
 */
 
#include "cards-image.h"

/* create an empty cards imags */
CardsImage* cards_image_new(void)
{
	CardsImage *cards;
	
	cards = g_new(CardsImage, 1);
	cards->width = 0;
	cards->height = 0;
	cards->preimage = preimage_new();
	cards->pixbuf = NULL;
	
	return cards;
}

/* create a cards image from a file */
CardsImage* cards_image_from_file(const gchar *file)
{
	CardsImage *cards;
	
	cards = g_new(CardsImage, 1);
	cards->preimage = preimage_new_from_file(file);
	cards->width = cards->preimage->width / 13;
	cards->height = cards->preimage->height / 5;
	cards->ratio = (gdouble)cards->width / (gdouble)cards->height;
	cards->pixbuf = NULL;
	cards_image_set_size(cards, cards->width, cards->height);
	
	return cards;
}

/* Render card_id on target pixmap at (x, y) */
void cards_image_render_to_pixmap(CardsImage *cards, gint card_id, gboolean active, GdkPixmap *target, GdkGC *target_gc, gint x, gint y)
{
	gint sx, sy;
	
	/* check if we can render */
	if (cards->pixbuf == NULL || target == NULL)
		return;

	/* calculate card position in the image */
	sx = (card_id % 13) * cards->width;
	sy = (card_id / 13) * cards->height;

	/* render */
	if (active)
	{
		GdkPixbuf *active_card;
		guint px, py, width, height, rowstride;
		guint16 red, green, blue;
		guchar *pixels, *p;

		/* copy the active card to a new pixbuf */
		active_card = gdk_pixbuf_new(gdk_pixbuf_get_colorspace(cards->pixbuf),
			gdk_pixbuf_get_has_alpha(cards->pixbuf),
			gdk_pixbuf_get_bits_per_sample(cards->pixbuf),
			cards->width,
			cards->height);
		gdk_pixbuf_copy_area(cards->pixbuf, sx, sy, cards->width, cards->height, active_card, 0, 0);
		
		/* FIXME: We can do a color button later... if it's usable. */
		red = 0;
		green = 0;
		blue = 0xAA00 / 0xFF;

		gdk_pixbuf_saturate_and_pixelate (active_card, active_card, 0, FALSE);

		pixels = gdk_pixbuf_get_pixels (active_card);
		width = gdk_pixbuf_get_width (active_card);
		height = gdk_pixbuf_get_height (active_card);
		rowstride = gdk_pixbuf_get_rowstride (active_card);

		for (py = 0; py < cards->height; py++)
		{
			for (px = 0; px < cards->width; px++)
			{
				p = pixels + py*rowstride + px*4;
				p[0] += (0xFF - p[0]) * red   / 0xFF;
				p[1] += (0xFF - p[1]) * green / 0xFF;
				p[2] += (0xFF - p[2]) * blue  / 0xFF;
			}
		}
		
		gdk_pixbuf_render_to_drawable(active_card,
			target,
			target_gc,
			0, 0,
			x, y,
			cards->width, cards->height,
			GDK_RGB_DITHER_NONE,
			0, 0);
		
		g_object_unref(active_card);
	}
	else
	{
		gdk_pixbuf_render_to_drawable(cards->pixbuf,
			target,
			target_gc,
			sx, sy,
			x, y,
			cards->width, cards->height,
			GDK_RGB_DITHER_NONE,
			0, 0);
	}
}

/* scale the cards to (width, height) */
void cards_image_set_size(CardsImage *cards, gint width, gint height)
{
	/* check there's a preimage loaded */
	if (cards->preimage->pixbuf == NULL)
		return;
	
	/* delete the existing pixbuf */
	if (cards->pixbuf != NULL)
		g_object_unref(cards->pixbuf);
	
	/* recalculate the width and height with respect to the height/width ratio */
	if (((gdouble)width / (gdouble)height) < cards->ratio)
	{
		height = (gint)((gdouble)width / cards->ratio);
	}
	else
	{
		width = (gint)((gdouble)height * cards->ratio);
	}
	
	/* resize the cards */
	cards->pixbuf = preimage_render(cards->preimage, width * 13, height * 5);
	cards->width = width;
	cards->height = height;
}

/* Free a cards image */
void cards_image_free(CardsImage *cards)
{
	if (cards == NULL)
		return;
	
	preimage_free(cards->preimage);
	g_object_unref(cards->pixbuf);
	g_free(cards);
}
