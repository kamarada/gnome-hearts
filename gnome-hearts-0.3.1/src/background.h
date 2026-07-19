/*
 *  Hearts - background.h
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

#ifndef BACKGROUND_H
#define BACKGROUND_H

#include <glib.h>
#include <gdk/gdk.h>

typedef struct _Background
{
	GdkPixbuf *original;
	GdkPixbuf *scaled;
	GdkGC *gc;
} Background;

extern Background bg;

void background_load(gchar* file);
void background_flush(gboolean force);
void background_render(GdkPixmap *target, gint x, gint y, gint width, gint height);
void background_free(void);

#endif
