/*
 *  Hearts - events.c
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

#include "events.h"
#include "background.h"

/* New game menu item and button */
void on_new_event(GtkWidget *widget, gpointer data)
{
	game_new();
	ui_draw_playingarea();
}

/* Restart menu item and button */
void on_restart_event(GtkWidget *widget, gpointer data)
{
	game_restart_round();
	ui_draw_playingarea();
}

/* Show scores menu item */
void on_scores_event(GtkWidget *widget, gpointer data)
{
	GtkWidget *score = glade_xml_get_widget(ui.xml, "score");
	gtk_widget_show (score);
}

/*
 * menu/toolbar events
 */

/* Quit menu item */
void on_quit_event(GtkWidget *widget, gpointer data)
{
	gtk_main_quit();
	return;
}

/* Undo menu item and button */
void on_undo_event(GtkWidget *widget, gpointer data)
{
	return;
}

/* Redo game menu item and button */
void on_redo_event(GtkWidget *widget, gpointer data)
{
	return;
}

/* Open the help file */
void on_help(GtkWidget *widget, gpointer data)
{
	gnome_help_display("gnome-hearts.xml", NULL, NULL);
}

/* Open the preferences help file */
void on_preferences_help(GtkWidget *widget, gpointer data)
{
	gnome_help_display("gnome-hearts.xml", "hearts-prefs", NULL);
}

/* About menu item */
void on_about_event(GtkImageMenuItem *widget, gpointer data)
{
	GtkWidget *about;
	about = glade_xml_get_widget(ui.xml, "about");
	gtk_widget_show (about);

	return;
}

/* Fullscreen */
void on_fullscreen_event(GtkWidget *widget, gpointer data)
{
	GtkWidget *window = glade_xml_get_widget(ui.xml, "hearts");
	GdkWindowState state = gdk_window_get_state(window->window);
	
	if (state & GDK_WINDOW_STATE_FULLSCREEN)
	{
		gtk_widget_show(glade_xml_get_widget(ui.xml, "fullscreen"));
		gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "fullscreen"), TRUE);
		gtk_widget_hide(glade_xml_get_widget(ui.xml, "leave_fullscreen"));
		gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "leave_fullscreen"), FALSE);
		gtk_widget_hide(glade_xml_get_widget(ui.xml, "leave_fullscreen_button"));
		gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "leave_fullscreen_button"), FALSE);
		gtk_window_unfullscreen((GtkWindow*)glade_xml_get_widget(ui.xml, "hearts"));
	}
	else
	{
		gtk_widget_hide(glade_xml_get_widget(ui.xml, "fullscreen"));
		gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "fullscreen"), FALSE);
		gtk_widget_show(glade_xml_get_widget(ui.xml, "leave_fullscreen"));
		gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "leave_fullscreen"), TRUE);
		gtk_widget_show(glade_xml_get_widget(ui.xml, "leave_fullscreen_button"));
		gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "leave_fullscreen_button"), TRUE);
		gtk_window_fullscreen((GtkWindow*)glade_xml_get_widget(ui.xml, "hearts"));
	}
}

void on_leave_fullscreen_event(GtkWidget *widget, gpointer data)
{
	gtk_widget_show(glade_xml_get_widget(ui.xml, "menubar"));
	gtk_widget_show(glade_xml_get_widget(ui.xml, "fullscreen"));
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "fullscreen"), TRUE);
	gtk_widget_hide(glade_xml_get_widget(ui.xml, "leave_fullscreen"));
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "leave_fullscreen"), FALSE);
	gtk_widget_hide(glade_xml_get_widget(ui.xml, "leave_fullscreen_button"));
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "leave_fullscreen_button"), FALSE);
	gtk_window_unfullscreen((GtkWindow*)glade_xml_get_widget(ui.xml, "hearts"));
}

/* Toolbar toggle menu item */
void on_toolbar_toggled(GtkCheckMenuItem *widget, gpointer data)
{
	GtkWidget *toolbar;
	toolbar = glade_xml_get_widget(ui.xml, "toolbar");

	if (gtk_check_menu_item_get_active(widget))
		gtk_widget_show_all(toolbar);
	else
		gtk_widget_hide_all(toolbar);
	
	return;
}

/* Statusbar toggle menu item */
void on_statusbar_toggled(GtkCheckMenuItem *widget, gpointer data)
{
	GtkWidget *statusbar;
	statusbar = glade_xml_get_widget(ui.xml, "statusbar");

	if (gtk_check_menu_item_get_active(widget))
		gtk_widget_show_all(statusbar);
	else
		gtk_widget_hide_all(statusbar);
	
	return;
}

/*
 * playingarea events
 */

/* deal with mouse clicks */
gboolean button_press_event(GtkWidget *widget, GdkEventButton *event)
{
	Card *card, *active;
	gint i;
	
	if (event->button != 1)
		return TRUE;
	
	card = active = NULL;
	
	switch (game_state)
	{
		case GAME_PASS_CARDS:
			if (game_pass > 0 && game_pass_cards(widget))
			{
				game_set_status(_("Click somewhere to continue the game."));
				game_state = GAME_RECIEVE_CARDS;
				break;
			}
			/* Don't break here. You can deselect cards instead of passing them as well */
			
		case GAME_SELECT_CARDS:
			/* if there are 3 cards selected, cards can be passed */
			if (game_select_cards(widget) == 3)
			{
				gchar *name = player[(user + game_pass) % 4]->name;
				gchar *message = g_strdup_printf(_("Click on the hand of %s to pass the cards."), name);
				game_set_status(message);
				g_free(message);
				
				game_state = GAME_PASS_CARDS;
			}
			else
				game_state = GAME_SELECT_CARDS;
			break;
			
		case GAME_RECIEVE_CARDS:
			/* start the round */
			cards_deck_deselect(game_deck);
			game_set_status(_("Click on the card you wish to play."));
			game_state = GAME_PLAY;
			game_open_round();
			
			/* redraw the screen */
			ui_draw_playingarea();
			break;
			
		case GAME_PLAY:
			/* see if we're done playing this trick */
			if (game_trick.num_played == 4)
			{
				/* start the next trick in this game */
				trick_reset(&game_trick);
				
				/* is this also the end of the round or game? */
				if (game_end_test())
					return TRUE;
				
				/* play cards until it's the user's turn */
				i = game_trick_winner;
				while (i != user)
				{
					player_play_card(player[i], player_play(player[i]));
					i = (i + 1) % 4;
				}
				
				/* redraw the screen */
				game_set_status(_("Click on the card you wish to play."));
				ui_draw_playingarea();
				return TRUE;
			}
			
			/* loop through the hand to find the active card and make sure it's valid.
			 * Apparently it's sometimes possible to play an invalid card. See bug #30.
			 */
			card = cards_hand_get_active(player[user]->hand);
			if (card == NULL || !game_is_valid_card(card, player[user]->hand, &game_trick))
				return TRUE;
			
			player_play_card(player[user], card);
			
			/* play cards until the trick is over */
			i = user;
			while (game_trick.num_played < 4)
			{
				i = (i + 1) % 4;
				player_play_card(player[i], player_play(player[i]));
			}
			
			/* update the game status and score */
			if ( cfg.queen_breaks_hearts )
				game_hearts_broken = game_hearts_broken || ( trick_num_point_cards( &game_trick ) > 0 ) ;
			else
				game_hearts_broken = game_hearts_broken || trick_num_suit(&game_trick, CARDS_HEARTS);

			game_trick_winner = trick_get_winner(&game_trick);
			player_take_trick(player[game_trick_winner], &game_trick);
			
			/* show the tricks to the AI's */
			player_trick_end(player[NORTH]);
			player_trick_end(player[EAST]);
			player_trick_end(player[WEST]);
			
			/* redraw the screen */
			game_set_status(_("Click somewhere to continue the game."));
			ui_draw_playingarea();
			break;
		
		case GAME_ROUND_END:
			game_new_round();
			ui_draw_playingarea();
			break;
		
		case GAME_END:
			game_new();
			ui_draw_playingarea();
			break;
		
		default:
			g_assert_not_reached();
	}
	
	return TRUE;
}

/* follow the cursor around, checking for active cards */
gboolean motion_notify_event (GtkWidget *widget, GdkEventMotion *event)
{
	Card *card;
	gint cx, cy, x, y, width, height, offset_x, offset_y, y_adj;
	gboolean update = FALSE;
	
	/* hinst are used so we don't fall behind the user */
	if (event->is_hint)
		gtk_widget_get_pointer(widget, &cx, &cy);
	else
	{
		cx = event->x;
		cy = event->y;
	}
	
	/* are we in the south_hand area? */
	offset_x = ui.cards_image->width  / 4;
	offset_y = ui.cards_image->height / 4;
	
	cards_hand_get_area(player[user]->hand, widget, ui.cards_image, &x, &y, &width, &height, TRUE);	
	
	if (cx < x || cx >= x + width || cy < y || cy >= y + height)
	{
		card = cards_hand_get_active(player[user]->hand);
		if (card && card->active)
		{
			card->active = FALSE;
			update = TRUE;
		}
	}
	else
	{
		/* find the currently active card */
		Card *current_active = cards_hand_get_active(player[user]->hand);
		Card *new_active = NULL;
		GList *i = NULL;
		
		/* loop through the hand and mark the new active card */
		for (i = player[user]->hand->list; i; i = i->next)
		{
			card = (Card*)i->data;
			
			/* calculate the card's onscreen position */
			if (card->selected)
				y_adj = y;
			else
				y_adj = y + offset_y;
			
			/* is the cursor on the card? */
			if (cx >= x && cx < x + ui.cards_image->width && cy >= y_adj && cy < y_adj + ui.cards_image->height)
			{
				/* update the card */
				if (game_state != GAME_PLAY || game_is_valid_card(card, player[user]->hand, &game_trick))
				{
					card->active = TRUE;
					new_active = card;
				}
				
				/* mark previous three cards as non-active since this card covers it */
				gint count = 0; 
				GList *j = i;
				while (g_list_previous(j) != NULL && count < 3)
				{
					count++;
					j = g_list_previous(j);
					card = (Card*)j->data;
					card->active = FALSE;
				}
			}
			else
				card->active = FALSE;
			
			x += offset_x;
		}
		
		if (current_active != new_active)
			update = TRUE;
	}
	
	if (update)
	{
		x = (widget->allocation.width - width) / 2;
		cards_hand_render(player[user]->hand, ui.cards_image, ui.backbuffer, ui.backbuffer_gc, x, y);
		gtk_widget_queue_draw_area(widget, x, y, x + width, y + height);
	}
	
	return TRUE;
}

/* Called when we need to draw part of the table */
gboolean on_expose_event(GtkWidget *widget, GdkEventExpose *event) 
{
	if (ui.backbuffer == NULL)
		on_configure_event(widget, NULL);
	
	/* Draw the exposed part from the background buffer to the screen */
	gdk_draw_drawable(widget->window, widget->style->black_gc,
		ui.backbuffer, event->area.x, event->area.y,
		event->area.x, event->area.y,
		event->area.width, event->area.height);
	
	return FALSE;
}

/* Called on e.g. creation and resizes */
gboolean on_configure_event(GtkWidget *widget, gpointer data)
{
	gint width, height;
	
	width = widget->allocation.width;
	height = widget->allocation.height;
	
	/* Remove the existing background buffer */
	if (ui.backbuffer)
		g_object_unref(ui.backbuffer);
	
	if (ui.backbuffer_gc)
		g_object_unref(ui.backbuffer_gc);
	
	/* Create a new buffer and GC */
	ui.backbuffer = gdk_pixmap_new(widget->window,
		width,
		height,
		-1);
	ui.backbuffer_gc = gdk_gc_new(ui.backbuffer);
	
	/* resize the background and cards */
	background_flush(FALSE);
	cards_image_set_size(ui.cards_image, width / 8, height / 5);
	
	ui_draw_playingarea();
	return TRUE;
}

/*
 * score table events
 */

/* next round */
void on_score_ok_clicked (GtkButton *widget, gpointer *data)
{
	GtkWidget *score;
	score = glade_xml_get_widget(ui.xml, "score");
	gtk_widget_hide_all (score);
	
	game_new_round();
	
	ui_draw_playingarea();
	return;
}

/* new game */
void on_score_new_clicked (GtkButton *widget, gpointer *data)
{
	GtkWidget *score;
	score = glade_xml_get_widget(ui.xml, "score");
	gtk_widget_hide_all(score);
	
	game_new();
	
	ui_draw_playingarea();
	return;
}

/*
 * preferences events
 */

/* Show preferences dialog */
void on_preferences_event(GtkWidget *widget, gpointer data)
{
	gtk_widget_show_all(glade_xml_get_widget(ui.xml, "preferences"));
	return;
}

/* update the ruleset */
void on_ruleset_changed	(GtkComboBox *widget, gpointer *data)
{
	gint i = gtk_combo_box_get_active(widget);
	
	if (i != -1)
		cfg.ruleset = i;
	else
		cfg.ruleset = RULESET_STANDARD;

	game_new();
}

/* update the clubs_lead radio */
void on_clubs_lead_changed (GtkToggleButton *widget, gpointer *data)
{
	cfg.clubs_lead = gtk_toggle_button_get_active(widget);
	game_new();
}

/* update the hearts_broken radio */
void on_hearts_break_changed (GtkToggleButton *widget, gpointer *data)
{
	cfg.hearts_break = gtk_toggle_button_get_active(widget);
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "queen_breaks_hearts"), cfg.hearts_break);

	// Also update queen_breaks_hearts if hearts_broken is disabled
	if (!cfg.hearts_break)
	{
		gtk_toggle_button_set_active(glade_xml_get_widget(ui.xml, "queen_breaks_hearts"), FALSE);
		cfg.queen_breaks_hearts = FALSE;
	}

	game_new();
}

/* update the no_blood radio */
void on_no_blood_changed (GtkToggleButton *widget, gpointer *data)
{
	cfg.no_blood = gtk_toggle_button_get_active(widget);
	game_new();
}

/* update the queen_breaks_hearts config value */
void on_queen_breaks_hearts_changed (GtkToggleButton *widget, gpointer *data)
{
	cfg.queen_breaks_hearts = gtk_toggle_button_get_active(widget);
	game_new();
}

void on_show_scores_changed (GtkToggleButton *widget, gpointer *data)
{
	int i;
	cfg.show_scores = gtk_toggle_button_get_active(widget);

	if (!cfg.show_scores)
	{
		for (i = 0; i < 4; i++)
		{
			gchar *name = g_strconcat("<span foreground=\"white\"><b>", player[i]->name, "</b></span>", NULL);
			pango_layout_set_markup(player[i]->layout, name, -1);
			g_free(name);
		}
	}

	ui_draw_playingarea();
}

/* load new north_ai */
void on_north_ai_changed (GtkComboBox *widget, gpointer *data)
{
	GList *l;
	gchar* text = gtk_combo_box_get_active_text(widget);
	gtk_label_set_text(GTK_LABEL(glade_xml_get_widget(ui.xml, "north_name")), text);
	
	// Find the class
	for (l = ui.ai_scripts; l; l = l->next)
	{
		AIScript *ai_script = l->data;
		if (strcmp(text, ai_script->name) == 0)
			cfg.north_ai = g_strdup(ai_script->class);
	}
	
	g_free(text);
	game_new();
}

/* load new east_ai */
void on_east_ai_changed (GtkComboBox *widget, gpointer *data)
{
	GList *l;
	gchar* text = gtk_combo_box_get_active_text(widget);
	gtk_label_set_text(GTK_LABEL(glade_xml_get_widget(ui.xml, "east_name")), text);
	
	// Find the class
	for (l = ui.ai_scripts; l; l = l->next)
	{
		AIScript *ai_script = l->data;
		if (strcmp(text, ai_script->name) == 0)
			cfg.east_ai = g_strdup(ai_script->class);
	}
	
	g_free(text);
	game_new();
}

/* load new west_ai */
void on_west_ai_changed (GtkComboBox *widget, gpointer *data)
{
	GList *l;
	gchar* text = gtk_combo_box_get_active_text(widget);
	gtk_label_set_text(GTK_LABEL(glade_xml_get_widget(ui.xml, "west_name")), text);
	
	// Find the class
	for (l = ui.ai_scripts; l; l = l->next)
	{
		AIScript *ai_script = l->data;
		if (strcmp(text, ai_script->name) == 0)
			cfg.west_ai = g_strdup(ai_script->class);
	}
	
	g_free(text);
	game_new();
}

/* load a new background image */
void on_background_changed (GtkFileChooser *widget, gpointer *data)
{
	if (widget == NULL)
		return;
	
	gchar *path = gtk_file_chooser_get_filename(widget);
	
	if (path == NULL)
		return;
	
	background_load(path);
	
	GtkWidget *playingarea_widget = glade_xml_get_widget(ui.xml, "playingarea");
	on_configure_event(playingarea_widget, NULL);
	
	cfg.background_image = g_strdup(path);
	g_free(path);
}

void on_background_tile_toggled (GtkToggleButton *widget, gpointer *data)
{
	cfg.background_tiled = gtk_toggle_button_get_active(widget);
	
	GtkWidget *playingarea_widget = glade_xml_get_widget(ui.xml, "playingarea");
	on_configure_event(playingarea_widget, NULL);
}

/* load a new cards_image */
void on_card_style_changed (GtkComboBox *widget, gpointer *data)
{
	gchar *path = NULL;
	gchar *card = gtk_combo_box_get_active_text(widget);
	GList *l = NULL;
	
	for (l = ui.card_styles; l; l = l->next)
	{
		CardStyle *card_style = l->data;
		if (strcmp(card_style->name, card) == 0)
		{
			path = g_strdup(card_style->path);
			break;
		}
	}
	
	cards_image_free(ui.cards_image);
	ui.cards_image = cards_image_from_file(path);
	
	GtkWidget *playingarea_widget = glade_xml_get_widget(ui.xml, "playingarea");
	on_configure_event(playingarea_widget, NULL);

	cfg.card_style = g_strdup(card);
	g_free(card);
}

/* hide the preferences */
void on_prefs_ok_clicked (GtkButton *widget, gpointer *data)
{
	config_save();
	
	/* hide the preferences dialog */
	gtk_widget_hide_all(glade_xml_get_widget(ui.xml, "preferences"));

	/* display the new game started by changed prefs */
	ui_draw_playingarea();
}

/* hide the preferences */
gboolean prefs_delete_event (GtkWidget *widget, GdkEvent *event, gpointer data)
{
	on_prefs_ok_clicked(NULL, NULL);
	return TRUE;
}

/**
 * hint events
 */

/* Hint menu item and button */
void on_hint_event(GtkWidget *widget, gpointer data)
{
	gchar *hint = game_get_hint();
	GtkLabel *hint_text = (GtkLabel*)glade_xml_get_widget(ui.xml, "hint_text");
	gtk_label_set_text(hint_text, hint);
	gtk_widget_show_all(glade_xml_get_widget(ui.xml, "hint"));
	
	g_free(hint);
		
	return;
}

void on_hide_ok_clicked (GtkButton *widget, gpointer *data)
{
	gtk_widget_hide_all(glade_xml_get_widget(ui.xml, "hint"));
	return;
}

/* hide the hint dialog */
gboolean hide_hint_event (GtkWidget *widget, GdkEvent *event, gpointer data)
{
	gtk_widget_hide_all(glade_xml_get_widget(ui.xml, "hint"));
	return TRUE;
}
