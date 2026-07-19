/*
 *  Hearts - player.c
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

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "hearts.h"
#include "player.h"
	
/* create a new player */
Player* player_new(gint direction, gboolean show_faces, gchar *script, Trick *trick, GtkWidget *widget)
{
	/* create the player with default values */
	Player *player;
	player = g_new(Player, 1);
	player->direction = direction;
	player->score_round = 0;
	player->score_total = 0;
	player->trick = trick;
	player->name = NULL;
	player->cards_taken = NULL;
	
	/* assign a hand of cards */
	player->hand = cards_hand_new(direction, show_faces);
	
	/* Load the Python AI */
	PyObject *module, *dict, *player_args, *result;
	
	module = PyImport_AddModule("__main__");
	dict = PyModule_GetDict(module);
	
	/* Create a new player AI instance by calling the classname in Python */
	gchar *class = (script ? script : "StockAI");
	
	player_args = Py_BuildValue("(iOOO)",
		direction, PyDict_GetItemString(dict, "trick"),
		PyDict_GetItemString(dict, "score"),
		PyDict_GetItemString(dict, "rules")
	);

	player->ai = PyObject_Call(PyDict_GetItemString(dict, class), player_args, NULL);
	Py_DECREF(player_args);
	
	if (PyErr_Occurred())
	{
		PyErr_Print();
		g_assert_not_reached();
	}
	
	/* Assign the new player AI instance in Python */
	result = PyObject_CallFunction(PyDict_GetItemString(dict, "player_set"), "Oi", player->ai, direction);
	Py_DECREF(result);
	
	/* create a pango layout and set the player name */
	player->layout = gtk_widget_create_pango_layout(widget, NULL);

	if (script)
	{
		result = PyObject_CallMethod(player->ai, "get_name", NULL);
		player->name = strdup(PyString_AsString(result));
	}
	else
	{
		player->name = strdup(g_get_real_name());
	}
	
	gchar *name = g_strconcat("<span foreground=\"white\"><b>", player->name, "</b></span>", NULL);
	pango_layout_set_markup(player->layout, name, -1);
	g_free(name);
	
	return player;
}

/* Let a player's AI play a card on the trick */
Card* player_play(Player *player)
{
	GList *l;
	gint suit, rank;
	PyObject *result;

	/* If there's no AI loaded, quit */
	g_assert(player != NULL && player->ai != NULL);
	
	/* Publish globals to the AI */	
	game_score_publish();
	trick_publish(player->trick);
	player_publish_hand(player);
	
	/* Call play_card() */
	result = PyObject_CallMethod(player->ai, "play_card", "");
	if (PyErr_Occurred())
	{
		PyErr_Print();
		g_assert_not_reached();
	}
	PyArg_ParseTuple(result, "ii", &suit, &rank);
	Py_DECREF(result);
	
	/* Find the card in the hand */
	Card *card_result = NULL;

	for (l = player->hand->list; l; l = l->next)
	{
		Card *card = (Card*)l->data;
		if (card->suit == suit && card->rank == rank)
			card_result = card;
	}

	if (!card_result || !game_is_valid_card(card_result, player->hand, player->trick))
	{
		printf("trying to play invalid card %d,%d\n", suit, rank);
		g_assert_not_reached();
	}
	
	/* return the actual card */
	return card_result;
}

GList* player_select_cards(Player *player)
{
	gint passing_direction;
	GList *l, *cards = NULL;
	PyObject *result;
	
	/* if there's no AI loaded, quit */
	g_assert(player != NULL && player->ai != NULL);
	
	/* Publish globals to the AI */	
	game_score_publish();
	player_publish_hand(player);

	/* Call play_card() */
	passing_direction = (player->direction + game_pass ) % 4;
	result = PyObject_CallMethod(player->ai, "select_cards", "(i)", passing_direction);
	if (PyErr_Occurred())
	{
		PyErr_Print();
		g_assert_not_reached();
	}
	
	/* Find the cards in the hand and mark them as selected */
	gint i, suit, rank;
	for (i = 0; i< 3; i++)
	{
		for (l = player->hand->list; l; l = l->next)
		{
			Card *card = (Card*)l->data;
			PyObject *list_item = PyList_GetItem(result, i);
			
			if (!PyArg_ParseTuple(list_item, "ii", &suit, &rank))
			{
				PyErr_Print();
				g_assert_not_reached();
			}
			
			if (card->suit == suit && card->rank == rank)
			{
				cards = g_list_append(cards, card);
			}
		}
	}
	
	Py_DECREF(result);
	g_assert(g_list_length(cards) == 3);
	return cards;
}

void player_receive_cards (Player *player, GList *list)
{
	/* Add the cards to the hand */
	cards_hand_add(player->hand, list);
	player_publish_hand(player);
	
	/* call receive_cards() on the player */
	GList *l;
	PyObject *result;
	PyObject *cards = PyList_New(0);
	
	for (l = list; l; l = l->next)
	{
		Card *card = (Card*)l->data;
		PyList_Append(cards, Py_BuildValue("(ii)", card->suit, card->rank));
	} 
	
	result = PyObject_CallMethod(player->ai, "receive_cards", "O", cards);
	if (PyErr_Occurred())
	{
		PyErr_Print();
		g_assert_not_reached();
	}
	Py_DECREF(cards);
	Py_DECREF(result);
}

/* show the trick to the AI */
void player_trick_end(Player *player)
{
	/* Don't assert here. This is called for human players too */
	if (player->ai == NULL)
		return;
	
	/* Publish globals to the AI */	
	trick_publish(player->trick);
	game_score_publish();
	player_publish_hand(player);
	
	/* Call trick_end() */
	PyObject *result = PyObject_CallMethod(player->ai, "trick_end", NULL);
	if (PyErr_Occurred())
	{
		PyErr_Print();
		g_assert_not_reached();
	}
	Py_DECREF(result);
}

/* Call an AI's round_end function */
void player_round_end(Player *player)
{
	/* Don't assert here. This is called for human players too */
	if (player->ai == NULL)
		return;
	
	/* Publish globals to the AI */	
	game_score_publish();
	
	/* Call round_end() */
	PyObject *result = PyObject_CallMethod(player->ai, "round_end", NULL);
	if (PyErr_Occurred())
	{
		PyErr_Print();
		g_assert_not_reached();
	}
	Py_DECREF(result);
}

/* play player's card on trick */
void player_play_card(Player *player, Card *card)
{
	GList *list_item;
	
	if (card == NULL)
		return;
	
	player->trick->card[player->hand->direction] = card;
	player->trick->num_played++;
	
	/* if this is the first card played, save the suit and the one who played it */
	if (player->trick->first_played == -1)
		player->trick->first_played = player->hand->direction;
	if (player->trick->trump == -1)
		player->trick->trump = card->suit;
	
	g_assert(player->trick->first_played >= 0 && player->trick->first_played < 4);

	/* move the card from the hand to the history stack */
	list_item = g_list_find(player->hand->list, card);
	player->hand->list = g_list_delete_link(player->hand->list, list_item);
}

/* Mark a list of cards as selected */
void player_mark_selected(Player *player, GList *list)
{
	GList *l;
	
	for (l = list; l; l = l->next)
	{
		Card *card = (Card*)l->data;
		card->selected = TRUE;
	}
}

/* Add the cards from the trick to the player's list of taken card */
void player_take_trick(Player *player, Trick *trick)
{
	/* You can only take a trick when it's fully played */
	if (trick->num_played != 4)
		return;
		
	int i;
	for (i = 0; i < 4; i++)
	{
		player->cards_taken = g_list_append(player->cards_taken, trick->card[i]);
	}

	/* Update the score for this round */
	player->score_round = cards_get_points(player->cards_taken);
}

/* Show the hand to the player */
void player_publish_hand (Player *player)
{
	GList *l;
	PyObject *result;
	
	PyObject *hand = PyList_New(0);
	for (l = player->hand->list; l; l = l->next)
	{
		Card *card = (Card*)l->data;
		PyList_Append(hand, Py_BuildValue("(ii)", card->suit, card->rank));
	} 
	
	result = PyObject_CallMethod(player->ai, "set_hand", "O", hand);
	if (PyErr_Occurred())
	{
		PyErr_Print();
		g_assert_not_reached();
	}
	Py_DECREF(hand);
	Py_DECREF(result);
}

/* free a player */
void player_free(Player *player)
{
	if (player == NULL)
		return;
	
	if (player->hand != NULL)
		cards_hand_free(player->hand);
	
	if (player->ai != NULL)
	{
		Py_DECREF(player->ai);
	}
	
	if (player->layout != NULL)
		g_object_unref(player->layout);
	
	g_list_free(player->cards_taken);
	
	g_free(player);
}
