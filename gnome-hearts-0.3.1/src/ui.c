/*
 *  Hearts - ui.c
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
#include <dirent.h>
#include <glib.h>
#include <glib/gi18n.h>
#include <gtk/gtk.h>
#include <glade/glade.h>
#include <string.h>
#include "background.h"
#include "cards.h"
#include "cfg.h"
#include "ui.h"

UserInterface ui;

/* Load the ui global in all it's glory */
void ui_load(void)
{
	/* Load the glade UI file */
	glade_gnome_init();
	ui.xml = glade_xml_new(PACKAGE_DATA_DIR"/gnome-hearts/gnome-hearts.glade", NULL, NULL);
	
	/* Hide the "leave fullscreen" buttons" */
	gtk_widget_hide(glade_xml_get_widget(ui.xml, "leave_fullscreen"));
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "leave_fullscreen"), FALSE);
	gtk_widget_hide(glade_xml_get_widget(ui.xml, "leave_fullscreen_button"));
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "leave_fullscreen_button"), FALSE);
	
	/* Gray out unused items */
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "undo_move1"), FALSE);
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "redo_move1"), FALSE);
	
	/* Turn off double buffering. We do that ourselves */
	gtk_widget_set_double_buffered(glade_xml_get_widget(ui.xml, "playingarea"), FALSE);
	
	/* Add a filer to the background filechooser */
	ui.filter = gtk_file_filter_new();
	gtk_file_filter_set_name(ui.filter, _("Images"));
	gtk_file_filter_add_mime_type(ui.filter, "image/png");
	gtk_file_filter_add_mime_type(ui.filter, "image/svg+xml");
	gtk_file_filter_add_mime_type(ui.filter, "image/jpeg");
	gtk_file_filter_add_mime_type(ui.filter, "image/gif");
	gtk_file_chooser_set_filter((GtkFileChooser*) glade_xml_get_widget(ui.xml, "background"), ui.filter);
	
	/* Create an array for the scores */
	ui.scores = g_ptr_array_new();
	ui.strike = pango_attr_list_new();
	pango_attr_list_insert(ui.strike, pango_attr_strikethrough_new(TRUE));
}

/* Start the user interface */
void ui_start(void)
{
	glade_xml_signal_autoconnect(ui.xml);
}

/* Set configuration options from the cfg global */
void ui_set_config(void)
{
	gint i = 0;
	GList *l = NULL;
	GtkComboBox *north_ai = GTK_COMBO_BOX(glade_xml_get_widget(ui.xml, "north_ai"));
	GtkComboBox *east_ai = GTK_COMBO_BOX(glade_xml_get_widget(ui.xml, "east_ai"));
	GtkComboBox *west_ai = GTK_COMBO_BOX(glade_xml_get_widget(ui.xml, "west_ai"));
	
	/* Select the right AI's and set their names */
	for (l = ui.ai_scripts; l; l = l->next)
	{
		AIScript *ai_script = l->data;
		
		if (strcmp(cfg.north_ai, ai_script->class) == 0)
		{
			gtk_combo_box_set_active(north_ai, i);
			gtk_label_set_text(GTK_LABEL(glade_xml_get_widget(ui.xml, "north_name")), g_strdup(ai_script->name));
		}
		if (strcmp(cfg.east_ai, ai_script->class) == 0)
		{
			gtk_combo_box_set_active(east_ai, i);
			gtk_label_set_text(GTK_LABEL(glade_xml_get_widget(ui.xml, "east_name")), g_strdup(ai_script->name));
		}
		if (strcmp(cfg.west_ai, ai_script->class) == 0)
		{
			gtk_combo_box_set_active(west_ai, i);
			gtk_label_set_text(GTK_LABEL(glade_xml_get_widget(ui.xml, "west_name")), g_strdup(ai_script->name));
		}
		
		i++;
	}

	/* Set the correct names on the score table UI */
	gtk_label_set_text((GtkLabel*) glade_xml_get_widget(ui.xml, "south_name"), g_get_real_name());
	
	/* Make sure that a valid AI is selected */
	AIScript *ai_script = ui.ai_scripts->data;
	if (gtk_combo_box_get_active(north_ai) == -1)
	{
		gtk_combo_box_set_active(north_ai, 1);
		cfg.north_ai = ai_script->class;
	}
	if (gtk_combo_box_get_active(east_ai) == -1)
	{
		gtk_combo_box_set_active(east_ai, 1);
		cfg.east_ai = ai_script->class;
	}
	if (gtk_combo_box_get_active(west_ai) == -1)
	{
		gtk_combo_box_set_active(west_ai, 1);
		cfg.west_ai = ai_script->class;
	}

	/* set the game rules in the preferences dialog */
	gtk_combo_box_set_active((GtkComboBox*) glade_xml_get_widget(ui.xml, "ruleset"), cfg.ruleset);
	gtk_toggle_button_set_active((GtkToggleButton*) glade_xml_get_widget(ui.xml, "clubs_lead"), cfg.clubs_lead);
	gtk_toggle_button_set_active((GtkToggleButton*) glade_xml_get_widget(ui.xml, "hearts_break"), cfg.hearts_break);
	gtk_toggle_button_set_active((GtkToggleButton*) glade_xml_get_widget(ui.xml, "no_blood"), cfg.no_blood);
	gtk_toggle_button_set_active((GtkToggleButton*) glade_xml_get_widget(ui.xml, "queen_breaks_hearts"), cfg.queen_breaks_hearts);
	gtk_toggle_button_set_active((GtkToggleButton*) glade_xml_get_widget(ui.xml, "show_scores"), cfg.show_scores);
	gtk_widget_set_sensitive(glade_xml_get_widget(ui.xml, "queen_breaks_hearts"), cfg.hearts_break);
	
	/* Set the background image chooser */
	gtk_file_chooser_set_filename((GtkFileChooser*) glade_xml_get_widget(ui.xml, "background"), cfg.background_image);
	
	/* Set the stretch toggle */
	if (cfg.background_tiled)
		gtk_toggle_button_set_active((GtkToggleButton*) glade_xml_get_widget(ui.xml, "background_tile"), TRUE);
	else
		gtk_toggle_button_set_active((GtkToggleButton*) glade_xml_get_widget(ui.xml, "background_stretch"), TRUE);
	
	/* Find all the card styles in the gnome-hearts cards directory */
	DIR *directory = opendir(PACKAGE_DATA_DIR"/pixmaps/gnome-hearts/cards/");
	struct dirent *file;
	
	g_assert(directory != NULL);
	while ((file = readdir(directory)))
	{
		if (g_str_has_suffix(file->d_name, ".png") || g_str_has_suffix(file->d_name, ".svg"))
			ui_add_card_style(g_strdup(file->d_name), g_strconcat(PACKAGE_DATA_DIR"/pixmaps/gnome-hearts/cards/", file->d_name, NULL));
	}
	closedir(directory);
	
	/* read cards from the gnome-games card dir */
	directory = opendir(PACKAGE_DATA_DIR"/gnome-games-common/cards/");
	if (directory != NULL)
	{
		while ((file = readdir(directory)))
		{
			if (g_str_has_suffix(file->d_name, ".png") || g_str_has_suffix(file->d_name, ".svg"))
				ui_add_card_style(g_strdup(file->d_name), g_strconcat(PACKAGE_DATA_DIR"/gnome-games-common/cards/", file->d_name, NULL));
		}
		closedir(directory);
	}
	
	/* Loop over all the card styles that were added, find the one in cfg and activate it */
	i = 0;
	for (l = ui.card_styles; l; l = l->next)
	{
		CardStyle *card_style = l->data;
		
		if (strcmp(cfg.card_style, card_style->name) ==0)
		{
			gtk_combo_box_set_active(GTK_COMBO_BOX(glade_xml_get_widget(ui.xml, "card_style")), i);
			ui.cards_image = cards_image_from_file(card_style->path);
		}
		
		i++;
	}
	
	/* Make sure a card style was loaded. If the configured style wasn't found then no style has been loaded
	at this point. See Debian bugs 396043 and 395551. */
	if (!ui.cards_image)
	{
		CardStyle *card_style = ui.card_styles->data;
		ui.cards_image = cards_image_from_file(card_style->path);
	}
}

/* Add a new player AI to the UI */
void ui_add_ai_script(gchar *name, gchar *class)
{
	AIScript *ai_script = g_new(AIScript, 1);
	ai_script->name = name;
	ai_script->class = class;
	ui.ai_scripts = g_list_append(ui.ai_scripts, ai_script);
	
	gtk_combo_box_append_text(GTK_COMBO_BOX(glade_xml_get_widget(ui.xml, "north_ai")), name);
	gtk_combo_box_append_text(GTK_COMBO_BOX(glade_xml_get_widget(ui.xml, "east_ai")), name);
	gtk_combo_box_append_text(GTK_COMBO_BOX(glade_xml_get_widget(ui.xml, "west_ai")), name);
}

/* Add a new card style to the UI */
void ui_add_card_style(gchar *name, gchar *path)
{
	CardStyle *style = g_new(CardStyle, 1);
	style->name = name;
	style->path = path;
	ui.card_styles = g_list_append(ui.card_styles, style);
	
	gtk_combo_box_append_text((GtkComboBox*) glade_xml_get_widget(ui.xml, "card_style"), name);
}

/* Add a row to the score table */
void ui_add_score_row(gint north, gint east, gint south, gint west)
{
	gint rows, i;
	
	/* Strike through the last four cells */
	if (ui.scores->len > 0)
	{
		gint i;
		for (i = ui.scores->len - 4; i < ui.scores->len; i++)
		{
			gtk_label_set_attributes(g_ptr_array_index(ui.scores, i), ui.strike);
		}
	}
	
	/* Create new score labels */
	g_ptr_array_add(ui.scores, gtk_label_new(g_strdup_printf("%d", north)));
	g_ptr_array_add(ui.scores, gtk_label_new(g_strdup_printf("%d", east)));
	g_ptr_array_add(ui.scores, gtk_label_new(g_strdup_printf("%d", south)));
	g_ptr_array_add(ui.scores, gtk_label_new(g_strdup_printf("%d", west)));
	
	/* resize the score_table widget */
	GtkTable *score_table = (GtkTable*) glade_xml_get_widget(ui.xml, "score_table");
	g_object_get(score_table, "n-rows", &rows, NULL);
	gtk_table_resize(score_table, rows + 1, 4);
	
	/* Add the labels to the table and center them */
	for (i = ui.scores->len - 4; i < ui.scores->len; i++)
	{
		gtk_label_set_justify(g_ptr_array_index(ui.scores, i), GTK_JUSTIFY_CENTER);
		gtk_table_attach((GtkTable*) glade_xml_get_widget(ui.xml, "score_table"), g_ptr_array_index(ui.scores, i), i, i + 1, rows, rows + 1, GTK_EXPAND, GTK_SHRINK, 2, 0);
	}
}

/* draw the playingarea */
void ui_draw_playingarea(void)
{
	gint x, y, width, height, n_x, n_y, n_width, n_height, i;
	GtkWidget *playingarea_widget;
	
	playingarea_widget = glade_xml_get_widget(ui.xml, "playingarea");
	
	/* Fill the buffer with the background image */
	background_render(ui.backbuffer, 0, 0, playingarea_widget->allocation.width, playingarea_widget->allocation.height);
	
	/* render the hands */
	for (i = 0; i < 4; i++)
	{
		cards_hand_get_area(player[i]->hand, playingarea_widget, ui.cards_image, &x, &y, &width, &height, TRUE);
		cards_hand_render(player[i]->hand, ui.cards_image, ui.backbuffer, ui.backbuffer_gc, x, y);
		
		/* Update the layout to display the score */
		if (cfg.show_scores)
		{
			gchar *name = g_strdup_printf("<span foreground=\"white\"><b>%s (%d/%d)</b></span>", player[i]->name, player[i]->score_round, player[i]->score_total + player[i]->score_round);
			pango_layout_set_markup(player[i]->layout, name, -1);
			g_free(name);
		}

		pango_layout_get_pixel_size(player[i]->layout, &n_width, &n_height);
		
		n_x = 0;
		n_y = 0;
		switch(i)
		{
			case NORTH:
				n_x = (playingarea_widget->allocation.width - n_width) / 2;
				n_y = y + height + 5;
				break;
			
			case EAST:
				n_x = x - n_width - 15;
				n_y = (playingarea_widget->allocation.height - n_height) / 2;
				break;
			
			case SOUTH:
				n_x = (playingarea_widget->allocation.width - n_width) / 2;
				n_y = y - n_height - 5;
				break;
			
			case WEST:
				n_x = x + width + 15;
				n_y = (playingarea_widget->allocation.height - n_height) / 2;
				break;
		}
		gdk_draw_layout(ui.backbuffer, ui.backbuffer_gc, n_x, n_y, player[i]->layout);
	}
	
	/* render the trick */
	trick_render(&game_trick, playingarea_widget, ui.cards_image, ui.backbuffer, ui.backbuffer_gc);
	
	/* update the screen */
	gtk_widget_queue_draw_area(playingarea_widget, 0, 0, playingarea_widget->allocation.width, playingarea_widget->allocation.height);
}

/* Free the UI */
void ui_free(void)
{
	GList *l;
	for (l = ui.ai_scripts; l; l = l->next)
		g_free(l->data);
	g_list_free(ui.ai_scripts);

	g_object_unref(ui.backbuffer_gc);
	g_object_unref(ui.backbuffer);
	g_object_unref(ui.filter);
	g_object_unref(ui.xml);
	
	pango_attr_list_unref(ui.strike);
}
