/*
 *  Hearts - hearts.c
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
#include "background.h"

Trick 		game_trick;
gint 		game_state;
gint 		game_pass;
gint 		game_trick_winner;
gboolean 	game_hearts_broken;
CardsDeck 	*game_deck;
GList	 	*game_score_labels;

Player *player[4]; 	/* the players of the game */
gint user;			/* which playes is the user */

/* Definition of the commandline options */
static GOptionEntry option_entries[] =
{
	{"show-cards", 0, 0, G_OPTION_ARG_NONE, &cfg.show_cards, N_("Show all the card faces while playing"), NULL},
	{NULL}
};

/* Load a pixmap */
GdkPixmap* get_pixmap(const char *filename)
{
	GdkPixmap *ret;
	GdkPixbuf *im;
	
	if (filename == NULL)
		return NULL; 
	
	im = gdk_pixbuf_new_from_file (filename, NULL);
	if (im != NULL)
	{
		gdk_pixbuf_render_pixmap_and_mask_for_colormap (im, gdk_colormap_get_system(), &ret, NULL, 127);
		gdk_pixbuf_unref (im);
	}
	else
	{
		ret = NULL;
	}
	
	return ret;
}

/* start a new game */
void game_new(void)
{
	gint i;
	GList *l;
	GtkTable *score_table;
	GtkWidget *widget;
	
	/* reset the score_table. To do this, we need to remove the child widgets and then resize */
	score_table = GTK_TABLE(glade_xml_get_widget(ui.xml, "score_table"));
	for (l = game_score_labels; l; l = l->next)
	{
		GtkLabel *label;
		label = l->data;
		gtk_widget_destroy(GTK_WIDGET(label));
	}
	g_list_free(game_score_labels);
	game_score_labels = NULL;
	gtk_table_resize(score_table, 2, 4);
	
	/* set the score window title */
	gtk_window_set_title(GTK_WINDOW(glade_xml_get_widget(ui.xml, "score")), _("Scores"));
	
	/* Publish the rulesets to Python. This is done here because game_new() is called when the
	 * rules have changed, and player_new() below initializes the players for the new game.
	 */
	config_publish();

	/* refresh the AI's */
	for (i = 0; i < 4; i++)
		player_free(player[i]);
	
	widget = glade_xml_get_widget(ui.xml, "playingarea");

	gint facing = cfg.show_cards ? FACE_UP : FACE_DOWN;
	player[0] = player_new(NORTH, facing, cfg.north_ai, &game_trick, widget);
	player[1] = player_new(EAST, facing, cfg.east_ai, &game_trick, widget);
	player[2] = player_new(SOUTH, FACE_UP, NULL, &game_trick, widget);
	player[3] = player_new(WEST, facing, cfg.west_ai, &game_trick, widget);
	
	game_pass = 0;
	game_new_round();
}

/* start a new round in this game */
void game_new_round(void)
{
	gint i;
	
	/* reset the game */
	cards_deck_reset(game_deck);
	trick_reset(&game_trick);
	trick_publish(&game_trick);
	game_pass = (game_pass + 1) % 4;
	game_hearts_broken = FALSE;
	
	/* new hands for everyone */
	for (i = 0; i < 4; i++)
	{
		cards_hand_free_cards(player[i]->hand);
		cards_hand_draw(player[i]->hand, game_deck, 13);
		g_list_free(player[i]->cards_taken);
		player[i]->cards_taken = NULL;
		player[i]->score_round = 0;
	}

	game_score_publish();

	/* have the AI's select cards to pass on if we're passing cards this round */
	for (i = 0; i < 4; i++)
	{
		if (i != user && game_pass > 0)
			player_mark_selected(player[i], player_select_cards(player[i]));
	}
	
	/* set the game state */
	if (game_pass > 0)
	{
		gchar *name = player[(user + game_pass) % 4]->name;
		game_set_status(_(g_strdup_printf("Select three cards that you wish to pass to %s.", name)));
		game_state = GAME_SELECT_CARDS;
	}
	else
	{
		game_set_status(_("Click on the card you wish to play."));
		game_state = GAME_PLAY;
		game_open_round();
	}
}

/* restart the current round */
void game_restart_round(void)
{
	gint i;
	
	/* reset the game */
	trick_reset(&game_trick);
	trick_publish(&game_trick);
	game_hearts_broken = FALSE;
	
	/* reset the hands for everyone */
	for (i = 0; i < 4; i++)
	{
		cards_hand_reset(player[i]->hand);
		g_list_free(player[i]->cards_taken);
		player[i]->cards_taken = NULL;
		player[i]->score_round = 0;
	}
	
	game_score_publish();

	/* have the AI's select cards to pass on if we're passing cards this round */
	for (i = 0; i < 4; i++)
	{
		if (i != user && game_pass > 0)
			player_mark_selected(player[i], player_select_cards(player[i]));
	}
	
	/* set the game state */
	if (game_pass > 0)
	{
		game_set_status(_("Select three cards that you wish to pass on."));
		game_state = GAME_SELECT_CARDS;
	}
	else
	{
		game_set_status(_("Click on the card you wish to play."));
		game_state = GAME_PLAY;
		game_open_round();
	}
}

/* start the round and play untill the player is due */
void game_open_round (void)
{
	gint i, starter = user;
	Card *two_of_clubs;
	
	/* figure out which playes has to start */
	if (cfg.clubs_lead)
	{
		two_of_clubs = &g_array_index(game_deck, Card, CARD_ID(CARDS_CLUBS, CARD_TWO));
		for (i = 0; i < 4; i++)
		{
			if (g_list_find(player[i]->hand->list, two_of_clubs))
				starter = i;
		}
	}
	else
	{
		starter = (game_pass + 1) % 4;
	}
	
	/* play */
	i = starter;
	while (i != user)
	{
		player_play_card(player[i], player_play(player[i]));
		i = (i + 1) % 4;
	}
}

/* test for the end of the round and show this game's score */
gboolean game_end_test(void)
{
	gint rows, i, score_value = 0;
	GtkWidget *label, *score;
	GtkTable *score_table;
	gchar *label_text;
	GList *l;
	
	/* end of round test */
	if (g_list_length(player[user]->hand->list) == 0)
	{
		/* Signal the players that the round is over */
		player_round_end(player[NORTH]);
		player_round_end(player[EAST]);
		player_round_end(player[WEST]);
		
		/* strike out the previous row */
		i = 0;
		l = game_score_labels;
		while (l != NULL && i < 4)
		{
			GtkLabel *label = l->data;
			gchar *text = g_strdup_printf("<s>%s</s>", gtk_label_get_label(label));
			gtk_label_set_markup(label, text);
			g_free(text);
			
			l = l->next;
			i++;
		}
		
		/* resize the score_table widget */
		score_table = (GtkTable*)glade_xml_get_widget(ui.xml, "score_table");
		g_object_get(score_table, "n-rows", &rows, NULL);
		gtk_table_resize(score_table, rows + 1, 4);
		
		/* fill the new row */
		for (i = 0; i < 4; i++)
		{
			/* update the scores */
			player[i]->score_total += player[i]->score_round;
			player[i]->score_round = 0;
			
			label_text = g_strdup_printf("%d", player[i]->score_total);
			label = gtk_label_new(label_text);
			game_score_labels = g_list_prepend(game_score_labels, label);
			g_free(label_text);
				
			gtk_label_set_justify((GtkLabel*)label, GTK_JUSTIFY_CENTER);
			gtk_table_attach(score_table, label, i, i + 1, rows, rows + 1,
					 GTK_EXPAND, GTK_SHRINK, 2, 0);
		}
		
		/* grab the score widget */		
		score = glade_xml_get_widget(ui.xml, "score");
		
		/* end of game test */
		for (i = 0; i < 4; i++)
			score_value = MAX(score_value, player[i]->score_total);
		
		if (score_value >= (cfg.ruleset == RULESET_SPOT_HEARTS ? 500 : 100))
		{
			game_state = GAME_END;
			
			gint winner = NORTH;
			for (i = 0; i < 4; i++)
			{
				if (player[i]->score_total < score_value)
				{
					score_value = player[i]->score_total;
					winner = i;
				}
			}

			// If user is tied for win, make him win
			if (player[user]->score_total == score_value) {
				winner = user;
			}
			
			if (winner == user)
				gtk_window_set_title((GtkWindow*)score, _("Game over - You have won!"));
			else
			{
				gchar *name = player[winner]->name;
				gtk_window_set_title((GtkWindow*)score,
				g_strdup_printf(_("Game over - %s has won!"), name));
			}
			game_set_status(_("Click somewhere to start a new game."));
		}
		else
		{
			game_set_status(_("Click somewhere to continue the game."));
			game_state = GAME_ROUND_END;
		}
		
		/* show the score */
		gtk_widget_show_all(score);
		
		return TRUE;
	}
	
	return FALSE;
}

/* pass cards to the next player */
gboolean game_pass_cards(GtkWidget *widget)
{
	gint x, y, width, height, mouse_x, mouse_y, p;
	GList *temp[4];
	
	/* get the area we're supposed to click on */
	gtk_widget_get_pointer(widget, &mouse_x, &mouse_y);
	cards_hand_get_area(player[(user + game_pass) % 4]->hand, widget, ui.cards_image, &x, &y, &width, &height, TRUE);
	
	if (mouse_x >= x && mouse_x < x + width && mouse_y >= y && mouse_y < y + height)
	{
		/* pass the cards and make a copy in the history for trick reset support */
		for (p = 0; p < 4; p++)
			temp[p] = cards_hand_draw_selected(player[p]->hand);
		
		for (p = 0; p < 4; p++)
		{
			player_receive_cards(player[(p + game_pass) % 4], temp[p]);
			g_list_free(temp[p]);
		}
		
		/* redraw */
		ui_draw_playingarea();
		return TRUE;
	}
	
	return FALSE;
}

/* (de)select cards in the passing round */
gint game_select_cards(GtkWidget *widget)
{
	GList *i;
	Card *card, *active;
	gint x, y, width, height, num_selected = 0;
	
	i = player[user]->hand->list;
	active = NULL;
	
	/* loop through the hand to find the active cards and the number of selected cards */			
	do
	{
		card = (Card*)i->data;
		
		if (card->active)
			active = card;
		
		if (card->selected)
			num_selected++;
							
		i = g_list_next(i);
	} while (i != NULL);
	
	/* You cannot select the active card if there are already 3 selected cards */				
	if (active != NULL && (num_selected < 3 || active->selected == TRUE))
	{
		active->selected = !active->selected;
		
		/* adjust the number of selected cards */
		if (active->selected)
			num_selected++;
		else
			num_selected--;
	}
	
	/* redraw the screen */
	cards_hand_get_area(player[user]->hand, widget, ui.cards_image, &x, &y, &width, &height, TRUE);
	background_render(ui.backbuffer, x, y, width, height);
	cards_hand_render(player[user]->hand, ui.cards_image, ui.backbuffer, ui.backbuffer_gc, x, y);
	gtk_widget_queue_draw_area(widget, x, y, width, height);
	
	return num_selected;
}

/* Publish the game's score to Python */
void game_score_publish()
{
	PyObject *module, *dict, *object, *result;
	
	/* Get a reference to score.set() */
	module = PyImport_AddModule("__main__");
	dict = PyModule_GetDict(module);
	object = PyDict_GetItemString(dict, "score");
	
	PyObject *score_list_round = Py_BuildValue("[iiii]",
		player[NORTH]->score_round,
		player[EAST]->score_round,
		player[SOUTH]->score_round,
		player[WEST]->score_round);
	
	PyObject *score_list_game = Py_BuildValue("[iiii]",
		player[NORTH]->score_total + player[NORTH]->score_round,
		player[EAST]->score_total + player[EAST]->score_round,
		player[SOUTH]->score_total + player[SOUTH]->score_round,
		player[WEST]->score_total + player[WEST]->score_round);

	result = PyObject_CallMethod(object, "set", "OO", score_list_round, score_list_game);

	Py_DECREF(score_list_round);
	Py_DECREF(score_list_game);
	Py_DECREF(result);
}

/* returns wether a card is valid to play from this hand on the stack */
gboolean game_is_valid_card(Card *card, CardsHand *hand, Trick *trick)
{
	/* special case: opening with a two of clubs (variant) */
	if (cfg.clubs_lead && g_list_length(hand->list) == 13 && trick->num_played == 0)
	{
		if (card->suit == CARDS_CLUBS && card->rank == CARD_TWO)
			return TRUE;
		else
			return FALSE;
	}
	
	/* special case, no blood in the first round, unless we have to */
	if (cfg.no_blood
		&& (card->suit == CARDS_HEARTS || (card->suit == CARDS_SPADES && card->rank == CARD_QUEEN))
		&& g_list_length(hand->list) == 13)
	{
		GList *l;
		gint num_pointcards = 0;
		for (l = hand->list; l; l = l->next)
		{
			Card *lcard = l->data;
			if (lcard->suit == CARDS_HEARTS || (lcard->suit == CARDS_SPADES && lcard->rank == CARD_QUEEN))
				num_pointcards++;
		}
		
		if (num_pointcards < 13)
			return FALSE;
	}
	
	/* special case: hearts must have been "broken" to be played as trump (variant).
	If a player has all hearts, then one must be played anyway */
	if (cfg.hearts_break 
		&& trick->num_played == 0
		&& game_hearts_broken == FALSE
		&& card->suit == CARDS_HEARTS
		&& cards_hand_num_suit(hand, CARDS_HEARTS) != cards_hand_length(hand)
	)
		return FALSE;
	
	/* follow the trump if possible */
	if (trick->trump > -1 && card->suit != trick->trump && cards_hand_num_suit(hand, trick->trump) > 0)
		return FALSE;
	
	/* no more reason to disallow a card */
	return TRUE;
}

/* get a hint string */
gchar* game_get_hint(void)
{
	if (game_state == GAME_PLAY)
	{
		if (game_trick.num_played == 4)
			return g_strdup(_("Click somewhere to continue the game."));
		
		Card *card = player_play(player[user]);
		/* Hint: %s is the name of the card the player should play */
		return g_strdup_printf(_("Play %s."), card_get_name(card));
	}
	else if (game_state == GAME_PASS_CARDS)
	{
		gchar *name = player[(user + game_pass) % 4]->name;
		return g_strdup_printf(_("Click on the hand of %s to pass the cards."), name);
	}
	else if (game_state == GAME_SELECT_CARDS)
	{
		GList *l, *cards = player_select_cards(player[user]);
		
		for (l = cards; l; l = l->next)
		{
			Card *card = l->data;
			
			if (!card->selected)
				/* Hint: %s is the name of the card the player should pass on */
				return g_strdup_printf(_("Pass %s."), card_get_name(card));
		}
	}
	
	return g_strdup(_("Sorry, I can't help you."));
}

/* Set the text of the status bar */
void game_set_status(gchar *message)
{
	GtkStatusbar *statusbar = GTK_STATUSBAR(glade_xml_get_widget(ui.xml, "statusbar"));
	gint context_id = gtk_statusbar_get_context_id(statusbar, "hearts user feedback");
	gtk_statusbar_pop(statusbar, context_id);
	gtk_statusbar_push(statusbar, context_id, message);
}

int main(int argc, char *argv[])
{
	#ifdef ENABLE_NLS
		bindtextdomain(GETTEXT_PACKAGE, PACKAGE_LOCALE_DIR);
		textdomain(PACKAGE);
		setlocale(LC_ALL, "");
	#endif

	/* Initialize GNOME */
	GOptionContext *option_context = g_option_context_new(_("- Play a game of hearts"));
	g_option_context_add_main_entries(option_context, option_entries, GETTEXT_PACKAGE);

	gnome_program_init(PACKAGE, VERSION, LIBGNOMEUI_MODULE,
			argc, argv,
			GNOME_PARAM_GOPTION_CONTEXT, option_context,
			GNOME_PARAM_APP_DATADIR, PACKAGE_DATA_DIR,
			GNOME_PARAM_NONE);
	
	/* init the game's global variables */
	game_score_labels = NULL;
	game_state = GAME_SELECT_CARDS;
	game_pass = 0;
	game_hearts_broken = FALSE;
	game_deck = cards_deck_new(TRUE, FALSE);
	trick_reset(&game_trick);
	user = SOUTH;
	
	/* Start the Glade UI - must be done before starting Python because Python loads AI's in the UI combo boxes */ 
	ui_load();
	
	/* Start the Python interpreter and load the hearts base module and list of AI's */
	python_start();
	
	/* Load the configuration */
	config_load();
	
	/* Apply the loaded configuration settings */
	ui_set_config();
	
	/* Load the background */
	background_load(cfg.background_image);
	
	/* Start the game */
	ui_start();
	game_new();
	gtk_main();
	
	/* Free the global structures */
	background_free();
	config_free();
	python_stop();
	ui_free();

	return 0;
}
