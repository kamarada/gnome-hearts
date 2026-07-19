/*
 *  Hearts - preimage.c
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

#include "preimage.h"

/* Create a new primage */
Preimage* preimage_new(void)
{
	Preimage *preimage;
	
	preimage = g_new(Preimage, 1);
	
	preimage->width = 0;
	preimage->height = 0;
	preimage->pixbuf = NULL;
	
	return preimage;
}

/* Create a new preimage from a file, using a loader */
Preimage* preimage_new_from_file(const gchar *file)
{
	Preimage *preimage;
	GError	 *error = NULL;
	
	if (file == NULL)
		return NULL;
	
	preimage = preimage_new();
	preimage->pixbuf = gdk_pixbuf_new_from_file(file, &error);

	if (preimage->pixbuf == NULL)
	{
		printf("**Error**: %s", error->message);
		g_assert_not_reached();
	}
	
	preimage->width = gdk_pixbuf_get_width(preimage->pixbuf);
	preimage->height = gdk_pixbuf_get_height(preimage->pixbuf);
	
	return preimage;
}

/* Render the preimage at the requested width and height */
GdkPixbuf* preimage_render(Preimage *preimage, gint width, gint height)
{
	GdkPixbuf *pixbuf;

	g_return_val_if_fail (width > 0 && height > 0, NULL);
	g_return_val_if_fail (preimage != NULL, NULL);
	
	pixbuf = gdk_pixbuf_scale_simple (preimage->pixbuf,
		width, height,
		GDK_INTERP_BILINEAR);
	
	return pixbuf;
}

/* Free the preimage */
void preimage_free(Preimage *preimage)
{
	g_object_unref(preimage->pixbuf);
	g_free(preimage);
}
