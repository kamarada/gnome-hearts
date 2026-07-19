/*
 *  Hearts - cards.c
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

#include <Python.h>
#include "cfg.h"
#include "cards.h"
#include "player.h"

/* Return the name of a card */
gchar*	card_get_name(Card *card)
{
	gchar *name = NULL;
	
	if (card == NULL)
		return NULL;
	
	switch (card->suit)
	{
		case CARDS_CLUBS:
			switch (card->rank)
			{
				case CARD_ACE_HIGH:
				case CARD_ACE: name = _("the ace of clubs"); break;
				case CARD_TWO: name = _("the two of clubs"); break;
				case CARD_THREE: name = _("the three of clubs"); break;
				case CARD_FOUR: name = _("the four of clubs"); break;
				case CARD_FIVE: name = _("the five of clubs"); break;
				case CARD_SIX: name = _("the six of clubs"); break;
				case CARD_SEVEN: name = _("the seven of clubs"); break;
				case CARD_EIGHT: name = _("the eight of clubs"); break;
				case CARD_NINE: name = _("the nine of clubs"); break;
				case CARD_TEN: name = _("the ten of clubs"); break;
				case CARD_JACK: name = _("the jack of clubs"); break;
				case CARD_QUEEN: name = _("the queen of clubs"); break;
				case CARD_KING: name = _("the king of clubs"); break;
			}
			return name;
		case CARDS_DIAMONDS:
			switch (card->rank)
			{
				case CARD_ACE_HIGH:
				case CARD_ACE: name = _("the ace of diamonds"); break;
				case CARD_TWO: name = _("the two of diamonds"); break;
				case CARD_THREE: name = _("the three of diamonds"); break;
				case CARD_FOUR: name = _("the four of diamonds"); break;
				case CARD_FIVE: name = _("the five of diamonds"); break;
				case CARD_SIX: name = _("the six of diamonds"); break;
				case CARD_SEVEN: name = _("the seven of diamonds"); break;
				case CARD_EIGHT: name = _("the eight of diamonds"); break;
				case CARD_NINE: name = _("the nine of diamonds"); break;
				case CARD_TEN: name = _("the ten of diamonds"); break;
				case CARD_JACK: name = _("the jack of diamonds"); break;
				case CARD_QUEEN: name = _("the queen of diamonds"); break;
				case CARD_KING: name = _("the king of diamonds"); break;
			}
			return name;
		case CARDS_SPADES:
			switch (card->rank)
			{
				case CARD_ACE_HIGH:	/* Motörhead! :-) */
				case CARD_ACE: name = _("the ace of spades"); break;
				case CARD_TWO: name = _("the two of spades"); break;
				case CARD_THREE: name = _("the three of spades"); break;
				case CARD_FOUR: name = _("the four of spades"); break;
				case CARD_FIVE: name = _("the five of spades"); break;
				case CARD_SIX: name = _("the six of spades"); break;
				case CARD_SEVEN: name = _("the seven of spades"); break;
				case CARD_EIGHT: name = _("the eight of spades"); break;
				case CARD_NINE: name = _("the nine of spades"); break;
				case CARD_TEN: name = _("the ten of spades"); break;
				case CARD_JACK: name = _("the jack of spades"); break;
				case CARD_QUEEN: name = _("the queen of spades"); break;
				case CARD_KING: name = _("the king of spades"); break;
			}
			return name;
		case CARDS_HEARTS:
			switch (card->rank)
			{
				case CARD_ACE_HIGH:
				case CARD_ACE: name = _("the ace of hearts"); break;
				case CARD_TWO: name = _("the two of hearts"); break;
				case CARD_THREE: name = _("the three of hearts"); break;
				case CARD_FOUR: name = _("the four of hearts"); break;
				case CARD_FIVE: name = _("the five of hearts"); break;
				case CARD_SIX: name = _("the six of hearts"); break;
				case CARD_SEVEN: name = _("the seven of hearts"); break;
				case CARD_EIGHT: name = _("the eight of hearts"); break;
				case CARD_NINE: name = _("the nine of hearts"); break;
				case CARD_TEN: name = _("the ten of hearts"); break;
				case CARD_JACK: name = _("the jack of hearts"); break;
				case CARD_QUEEN: name = _("the queen of hearts"); break;
				case CARD_KING: name = _("the king of hearts"); break;
			}
			return name;
	}
	
	g_assert_not_reached();
}

/* Get the point value of a linked list of cards */
gint cards_get_points(GList *list)
{
	GList *l;
	
	/* Figure out how many point cards are in the list */
	gint point_cards = 0;
	for (l = list; l; l = l->next)
	{
		Card* card = l->data;
		
		if (card == NULL)
			continue;

		if (card->suit == CARDS_HEARTS || (card->suit == CARDS_SPADES && card->rank == CARD_QUEEN))
			point_cards ++;
	}
	
	/* Shooting the moon: substract points for hearts and the Queen of spades */
	gint modifier = point_cards == 14 ? -1 : 1;
	
	/* Shooting the sun: substract double points for hearts and the Queen of spades */
	if (g_list_length(list) == 52)
		modifier = -2;
	
	gint score = 0;
	for (l = list; l; l = l->next)
	{
		Card* card = l->data;
		
		if (card == NULL)
			continue;

		/* Hearts add points */
		if (card->suit == CARDS_HEARTS)
		{
			if (cfg.ruleset == RULESET_SPOT_HEARTS)
				/* variant: Spot hearts - card is worth their rank */
				score += card->rank * modifier;
			else
				score += modifier;
		}
		
		/* The Queen of spades adds a big penalty */
		else if (card->suit == CARDS_SPADES && card->rank == CARD_QUEEN)
		{
			if (cfg.ruleset == RULESET_SPOT_HEARTS)
				/* variant: Spot hearts - Queen of spades is 25 points */
				score += 25 * modifier;
			else
				score += 13 * modifier;
		}
		
		/* variant: Omnibus - Jack of diamonds is -10 points */
		else if (cfg.ruleset == RULESET_OMNIBUS && card->suit == CARDS_DIAMONDS && card->rank == CARD_JACK)
			score -= 10;
		
		/* variant: Alternative Omnibus - Ten of diamonds is -10 points */
		else if (cfg.ruleset == RULESET_OMNIBUS_ALT && card->suit == CARDS_DIAMONDS && card->rank == CARD_TEN)
			score -= 10;
	}
	
	return score;
}


/* create a new deck of cards */
CardsDeck* cards_deck_new (gboolean aces_high, gboolean include_jokers)
{
	CardsDeck *deck;
	Card *card;
	Card new_card;
	gint i;
	
	/* create the array */
	if (include_jokers)
		deck = g_array_sized_new(FALSE, TRUE, sizeof(Card), 52);
	else
		deck = g_array_sized_new(FALSE, FALSE, sizeof(Card), 54);

	new_card.suit = 0;
	new_card.rank = 0;
	new_card.drawn = FALSE;
	new_card.selected = FALSE;
	new_card.active = FALSE;

	/* initialize the cards */
	for (i = 0; i < 52; i++)
	{
		g_array_append_val(deck, new_card);
		
		card = &g_array_index(deck, Card, i);
		card->suit = (i / 13);
		card->rank = (i % 13) + 1;
		
		if (aces_high && card->rank == CARD_ACE)
			card->rank = CARD_ACE_HIGH;
	}
	
	if (include_jokers)
	{
		g_array_append_val(deck, new_card);
		g_array_append_val(deck, new_card);

		card = &g_array_index(deck, Card, 52);
		card->rank = CARD_RED_JOKER;

		card = &g_array_index(deck, Card, 53);
		card->rank = CARD_BLACK_JOKER;
	}
	
	return deck;
}

/* Return a list of pointer to a random set of cards from the deck */
GList* cards_deck_draw_random (CardsDeck *deck, gint number, gboolean mark_drawn)
{
	GList *undrawn, *result;
	Card *card;
	gint i, j;
	
	undrawn = NULL;
	result = NULL;
	
	/* add all the non-drawn cards to a linked list */
	for (i = 0; i < deck->len; i++)
	{
		card = &g_array_index(deck, Card, i);
		if (card->drawn == FALSE)
			undrawn = g_list_prepend(undrawn, card);
	}

	/* are there enough cards */
	if (g_list_length(undrawn) < number)
		return NULL;
	
	for (i = 0; i < number; i++)
	{
		j = g_random_int_range(0, g_list_length(undrawn));
		card = (Card*)g_list_nth_data(undrawn, j);
		result = g_list_prepend(result, card);
		undrawn = g_list_remove(undrawn, card);

		/* mark it as drawn */
		if (mark_drawn)
			card->drawn = TRUE;
	}
	
	g_list_free(undrawn);
	
	return result;
}

/* reset the deck */
void cards_deck_reset (CardsDeck *deck)
{
	gint i;
	Card *card;
	
	for (i = 0; i < deck->len; i++)
	{
		card = &g_array_index(deck, Card, i);
		card->drawn = FALSE;
		card->selected = FALSE;
		card->active = FALSE;
	}
}

/* Mark all cards as unselected */
void cards_deck_deselect (CardsDeck *deck)
{
	gint i;
	Card *card;
	
	for (i = 0; i < deck->len; i++)
	{
		card = &g_array_index(deck, Card, i);
		card->selected = FALSE;
	}
}

/* Free a deck */
void cards_deck_free (CardsDeck *deck)
{
	g_array_free(deck, TRUE);
}

/* create an empty hand */
CardsHand* cards_hand_new (gint direction, gboolean show_faces)
{
	CardsHand* hand;
	
	hand = g_new(CardsHand, 1);
	hand->list = NULL;
	hand->hist = NULL;
	hand->direction = direction;
	hand->show_faces = show_faces;
	
	return hand;
}

/* draw <number> cards from <deck> */
void cards_hand_draw (CardsHand *hand, CardsDeck *deck, gint number)
{
	GList *draw;
	
	draw = cards_deck_draw_random(deck, number, TRUE);
	hand->list = g_list_concat(hand->list, draw);
	cards_hand_sort(hand);
	hand->hist = g_list_copy(hand->list);
}

GList* cards_hand_draw_selected(CardsHand *hand)
{
	GList *i, *result;
	Card *card;

	result = NULL;
	
	/* grab the result */
	i = hand->list;
	while (i != NULL)
	{
		card = (Card*)i->data;
		
		if (card->selected == TRUE)
			result = g_list_prepend(result, (gpointer)card);
		
		i = g_list_next(i);
	}
	
	/* remove the result from the original */
	i = result;
	while (i != NULL)
	{
		card = (Card*)i->data;
		hand->list = g_list_remove(hand->list, card);
		i = g_list_next(i);
	}
	
	return result;
}

void cards_hand_add(CardsHand *hand, GList *list)
{
	hand->list = g_list_concat(hand->list, g_list_copy(list));
	cards_hand_sort(hand);
}

/* callback for the sorting routine */
gint cards_hand_sort_cb(Card *one, Card *two)
{
	gint one_id, two_id;
	
	if (one->rank == CARD_RED_JOKER || one->rank == CARD_BLACK_JOKER)
		return 1;

	if (two->rank == CARD_RED_JOKER || two->rank == CARD_BLACK_JOKER)
		return -1;

	one_id = card_id(one);
	two_id = card_id(two);
	
	/* add 39 so that the order will be clubs, diamond, spades, hearts */
	if (one->suit == CARDS_HEARTS)
		one_id += 39;

	if (two->suit == CARDS_HEARTS)
		two_id += 39;

	if (one->rank % 13 == 1)
		one_id += 13;

	if (two->rank % 13 == 1)
		two_id += 13;
	
	if (one_id < two_id)
		return -1;
	
	return 1;
}

/* sort the hand */
void cards_hand_sort(CardsHand *hand)
{
	if (g_list_length(hand->list) == 0)
		return;
	
	hand->list = g_list_sort(hand->list, (GCompareFunc)cards_hand_sort_cb);
}

/* returns the x,y,width,height for a hand */
void cards_hand_get_area(CardsHand *hand, GtkWidget *widget, CardsImage *image, gint *x, gint *y, gint *width, gint *height, gboolean with_selected)
{
	gint offset_x = 0;
	gint offset_y = 0;
	
	if (hand->direction == NORTH || hand->direction == SOUTH)
	{
		offset_x = image->width / 4;
		
		if (with_selected)
			offset_y = image->height / 4;

		*width = (g_list_length(hand->list) * offset_x) + (image->width - offset_x);
		*height = image->height + offset_y;
		*x = (widget->allocation.width - *width) / 2;
		
		if (hand->direction == NORTH)
			*y = 10;
		else
			*y = widget->allocation.height - *height - 10;
	}
	else
	{
		offset_y = image->height / 4;
		
		if (with_selected)
			offset_x = image->width / 4;
			
		*height = (g_list_length(hand->list) * offset_y) + (image->height - offset_y);
		*width = image->width + offset_x;
		*y = (widget->allocation.height - *height) / 2;
		
		if (hand->direction == WEST)
			*x = 10;
		else
		{
			*x = widget->allocation.width - *width - 10;
		}    
	}
}

/* render the hand */
void cards_hand_render(CardsHand *hand, CardsImage *cards, GdkPixmap *target, GdkGC *target_gc, gint x, gint y)
{
	GList *i;
	gint id, offset_x, offset_y;
	Card *card;
	
	if (target == NULL || target_gc == NULL)
		return;
	
	offset_x = 0;
	offset_y = 0;
	
	switch (hand->direction)
	{
		case NORTH:	offset_y = cards->height /  4; break;
		case EAST:	offset_x = cards->width  / -4; x -= offset_x; break;
		case SOUTH:	offset_y = cards->height / -4; y -= offset_y; break;
		case WEST:	offset_x = cards->width  /  4; break;
	}

	/* step through the list */	
	i = hand->list;
	while (i != NULL)
	{
		card = (Card*)i->data;
		
		/* get the image ID */
		if (hand->show_faces == FACE_UP)
			id = card_id(card);
		else
			id = CARD_BACK;
		
		/* selected cards are pushed up */
		if (card->selected == TRUE)
			cards_image_render_to_pixmap(cards, id, card->active, target, target_gc, x + offset_x, y + offset_y);
		else
			cards_image_render_to_pixmap(cards, id, card->active, target, target_gc, x, y);
		
		/* position of the next card */
		if (hand->direction == NORTH || hand->direction == SOUTH)
			x += (cards->width / 4);
		else
			y += (cards->height / 4);

		i = g_list_next(i);
	}
}

/* the number of cards in the hand */
gint cards_hand_length(CardsHand *hand)
{
	return g_list_length(hand->list);
}

/* get the nth card from the hand */
Card* cards_hand_get(CardsHand *hand, gint n)
{
	Card *card = NULL;
	
	if (n >= 0 && n < g_list_length(hand->list))
		card = g_list_nth_data(hand->list, n);
	
	return card;
}

/* return the active card */
Card* cards_hand_get_active(CardsHand *hand)
{
	GList *i;
	Card *card = NULL, *active = NULL;

	for (i = hand->list; i; i = i->next)
	{
		card = (Card*)i->data;

		if (card->active)
			active = card;
	}
	
	return active;
}

void cards_hand_toggle_select(CardsHand* hand, gint n)
{
	Card *card = cards_hand_get(hand, n);
	
	if (card != NULL)
		card->selected = !card->selected;
}

/* count how many cards of a certain suit we have */
gint cards_hand_num_suit(CardsHand *hand, gint suit)
{
	GList *i;
	Card *card;
	gint result = 0;
	
	i = hand->list;
	while (i != NULL)
	{
		card = (Card*)i->data;
		if (card->suit == suit)
			result++;
		i = g_list_next(i);
	}
	
	return result;
}

/* return the number of selected cards in this hand */
gint cards_hand_num_selected(CardsHand *hand)
{
	GList *l;
	Card *card;
	gint num_selected = 0;
	
	for (l = hand->list; l; l = l->next)
	{
		card = (Card*)l->data;
		if (card->selected)
			num_selected++;
	}
	
	return num_selected;
}

/* reset the hand to the initial state */
void cards_hand_reset(CardsHand *hand)
{
	g_list_free(hand->list);
	hand->list = g_list_copy(hand->hist);
	
	g_assert(g_list_length(hand->list) == 13);
}

/* Free the cards in a hand */
void cards_hand_free_cards(CardsHand *hand)
{
	if (hand->list != NULL)
		g_list_free(hand->list);

	if (hand->hist != NULL)
		g_list_free(hand->hist);

	hand->list = NULL;
	hand->hist = NULL;
}

/* Free a hand */
void cards_hand_free(CardsHand *hand)
{
	cards_hand_free_cards(hand);
	g_free(hand);
}

/* return the winning card in this trick */
gint trick_get_winner(Trick *trick)
{
	gint i, val = 0, result = -1;
	
	for (i = 0; i < 4; i++)
	{
		/* return an error if not all cards have been played */
		g_assert(trick->card[i] != NULL);
		
		/* determine the value of the card */
		if (trick->card[i]->suit == trick->trump && trick->card[i]->rank > val)
		{
			val = trick->card[i]->rank;
			result = i;
		}
	}

	// Quit if a winner can't be determined	
	g_assert(result >= 0 || result < 4);

	return result;
}

/* get the score of a trick */
gint trick_get_score(Trick *trick)
{
	gint i, score = 0;
	GList *list = NULL;
	
	/* cards_get_score wants a linked list, so build it */
	for (i = 0; i < 4; i++)
	{
		list = g_list_append(list, trick->card[i]);
	}
	
	score = cards_get_points(list);
	g_list_free(list);
	
	return score;
}

/* return the number of suit cards in the trick */
gint trick_num_suit(Trick *trick, gint suit)
{
	gint i, result = 0;
	
	for (i = 0; i < 4; i++)
	{
		if (trick->card[i] != NULL && trick->card[i]->suit == suit)
			result++;
	}
	
	return result;
}

/* return the number of point cards in the trick (sans bonus cards) */
gint trick_num_point_cards (Trick *trick)
{
	gint i, result = 0;
	
	for (i = 0; i < 4; i++)
	{
		if (trick->card[i] != NULL)
		{
			if (trick->card[i]->suit == CARDS_HEARTS)
				result++;
			else if (trick->card[i]->suit == CARDS_SPADES && trick->card[i]->rank == CARD_QUEEN)
				result++;
		}
	}
	
	return result;
}

/* render the trick */
void trick_render(Trick *trick, GtkWidget *widget, CardsImage *image, GdkPixmap *target, GdkGC *target_gc)
{
	gint x, y, width, height, cx, cy, offset, i, player;
	Card *card;

	// Nothing played yet, so return
	if (trick->first_played == -1)
		return;

	offset = image->height / 4;
	width = image->width * 2;
	height = (image->height * 2) - (offset * 2);
	x = (widget->allocation.width - width) / 2;
	y = (widget->allocation.height - height) / 2;
	cx = cy = 0;
	
	for (i = 0; i < 4; i++)
	{
		player = (trick->first_played + i) % 4;

		switch (player)
		{
			case NORTH: cx = x + (image->width / 2); cy = y; break;
			case EAST: cx = x + image->width; cy = y + offset; break;
			case SOUTH: cx = x + (image->width / 2); cy = y + (offset * 2); break;
			case WEST: cx = x; cy = y + offset; break;
		}
		
		card = trick->card[player];
		
		if (card == NULL)
			return;

		cards_image_render_to_pixmap(image, card_id(card), FALSE, target, target_gc, cx, cy);
	}
}

/* reset the trick */
void trick_reset(Trick *trick)
{
	gint i;
	
	trick->trump = -1;
	trick->num_played = 0;
	trick->first_played = -1;
	
	for (i = 0; i < 4; i++)
		trick->card[i] = NULL;  
	
}

/* Set the trick global in Python */
void trick_publish(Trick *trick)
{
	PyObject *module, *dict, *object, *result, *card[4];
	int i;
	
	/* Get a reference to trick.set() */
	module = PyImport_AddModule("__main__");
	dict = PyModule_GetDict(module);
	object = PyDict_GetItemString(dict, "trick");
	
	/* Create a tuple of cards */
	for (i = 0; i < 4; i++)
	{
		if (trick->card[i] == NULL)
			card[i] = Py_BuildValue("");
		else
			card[i] = Py_BuildValue("(ii)", trick->card[i]->suit, trick->card[i]->rank);
	}
	
	result = PyObject_CallMethod(object, "set", "(OOOO)iii", card[NORTH], card[EAST], card[SOUTH], card[WEST], trick->trump, trick->num_played, trick->first_played);
	
	Py_DECREF(result);
	for (i = 0; i < 4; i++)
		Py_DECREF(card[i]);
}

/* return the ID for a card */
gint card_id(Card *card)
{
	/* jokers */
	if (card->rank > 51)
		return card->rank;
	
	/* a regular card */
	return CARD_ID(card->suit, card->rank);
}
