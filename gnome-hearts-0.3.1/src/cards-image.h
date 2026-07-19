/*
 *  Hearts - cards-image.h
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
 
#ifndef CARDS_IMAGE_H
#define CARDS_IMAGE_H

#include <gdk/gdk.h>
#include "preimage.h"

/* the card types */
enum {
  CARD_ACE         = 1,
  CARD_TWO         = 2,
  CARD_THREE       = 3,
  CARD_FOUR        = 4,
  CARD_FIVE        = 5,
  CARD_SIX         = 6,
  CARD_SEVEN       = 7,
  CARD_EIGHT       = 8,
  CARD_NINE        = 9,
  CARD_TEN         = 10,
  CARD_JACK        = 11,
  CARD_QUEEN       = 12,
  CARD_KING        = 13,
  CARD_ACE_HIGH    = 14,
  CARDS_CLUBS      = 0,
  CARDS_DIAMONDS   = 1,
  CARDS_HEARTS     = 2,
  CARDS_SPADES     = 3,
  CARD_RED_JOKER   = 52,
  CARD_BLACK_JOKER = 53,
  CARD_BACK        = 54,
  CARDS_TOTAL      = 55
};

/* The card_image struct */
typedef struct _CardsImage
{
	/* The image as loaded from file */
	Preimage *preimage;
	
	/* The image resized to teh current window size */
	GdkPixbuf *pixbuf;
	
	/* width, height and ratio of a single card */
	gint 	width;
	gint 	height;
	gdouble ratio;
	
} CardsImage;

/* quick function to calculate the card ID */
#define CARD_ID(suit, rank) ((13*(suit)) + ((rank-1)%13))

/* functions for the CardsImage */
CardsImage* cards_image_new(void);
CardsImage* cards_image_from_file(const gchar *file);
void 		cards_image_render_to_pixmap(CardsImage *cards, gint card_id, gboolean active, GdkPixmap *target, GdkGC *target_gc, gint x, gint y);
void 		cards_image_set_size(CardsImage *cards, gint width, gint height);
void 		cards_image_free(CardsImage *cards);

#endif
