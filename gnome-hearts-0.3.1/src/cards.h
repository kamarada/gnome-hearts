/*
 *  Hearts - cards.h
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
 
#ifndef CARDS_H
#define CARDS_H

#include <glib.h>
#include <glib/gi18n.h>
#include <gtk/gtk.h>

#include "cards-image.h"

enum 
{
	NORTH 		= 0,
	EAST 		= 1,
	SOUTH		= 2,
	WEST		= 3,
	FACE_DOWN 	= FALSE,
	FACE_UP 	= TRUE
};

enum
{
	RULESET_OMNIBUS		= 0,
	RULESET_OMNIBUS_ALT	= 1,
	RULESET_SPOT_HEARTS	= 2,
	RULESET_STANDARD	= 3
};

/* A single card */
typedef struct _Card
{
	gint suit;
	gint rank;
	
	/* deck variables */
	gboolean drawn;
	
	/* hand variables */
	gboolean selected;
	gboolean active;
} Card;

/* A hand of cards */
typedef struct _CardsHand
{
	GList *list;			/* the current cards */
	GList *hist;			/* copy of the original list of 13 cards (for reset purposes) */
	gint direction;
	gboolean show_faces;
} CardsHand;

/* A full deck of cards */
typedef GArray CardsDeck;

/* The trick currently being played */
typedef struct _Trick
{
	gint trump;			/* suit of the first card that was played */
	gint num_played;	/* number of cards played */
	gint first_played;	/* first card to be played */
	Card *card[4];		/* the cards played */
} Trick;

/* functions for cards */
gchar* card_get_name(Card *card);
gint cards_get_points(GList *list);

/* functions for the card deck */
CardsDeck* 	cards_deck_new (gboolean aces_high, gboolean include_jokers);
GList* 	cards_deck_draw_random (CardsDeck *deck, gint number, gboolean mark_drawn);
void 	cards_deck_reset (CardsDeck *deck);
void 	cards_deck_deselect (CardsDeck *deck);
void 	cards_deck_free (CardsDeck *deck);

/* functions for a hand of cards */
CardsHand* 	cards_hand_new (gint direction, gboolean show_faces);
void 	cards_hand_draw (CardsHand *hand, CardsDeck *deck, gint number);
GList* 	cards_hand_draw_selected (CardsHand *hand);
void 	cards_hand_add (CardsHand *hand, GList *list);
gint 	cards_hand_sort_cb (Card *one, Card *two);
void 	cards_hand_sort (CardsHand *hand);
void 	cards_hand_get_area (CardsHand* hand, GtkWidget *widget, CardsImage *image, gint *x, gint *y, gint *width, gint *height, gboolean with_selected);
void 	cards_hand_render (CardsHand *hand, CardsImage *cards, GdkPixmap *target, GdkGC *target_gc, gint x, gint y);
gint 	cards_hand_length (CardsHand *hand);
Card* 	cards_hand_get (CardsHand *hand, gint n);
Card* 	cards_hand_get_active (CardsHand *hand);
void 	cards_hand_toggle_select (CardsHand *hand, gint n);
gint 	cards_hand_num_suit (CardsHand *hand, gint suit);
gint	cards_hand_num_selected(CardsHand *hand);
void 	cards_hand_reset (CardsHand *hand);
void 	cards_hand_free_cards (CardsHand *hand);
void 	cards_hand_free (CardsHand *hand);

/* functions for a trick of cards */
gint trick_get_winner (Trick *trick);
gint trick_get_score (Trick *trick);
gint trick_num_suit (Trick *trick, gint suit);
gint trick_num_point_cards (Trick *trick);
void trick_render (Trick *trick, GtkWidget *widget, CardsImage *image, GdkPixmap *target, GdkGC *target_gc);
void trick_reset (Trick *trick);
void trick_publish (Trick *trick);

gint card_id (Card *card);

#endif
