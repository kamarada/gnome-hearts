/*
 *  Hearts - events.h
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

#ifndef EVENTS_H
#define EVENTS_H

#include "hearts.h"
#include "cards.h"

/* toolbar/menu events */
void on_new_event 		(GtkWidget *widget, gpointer data);
void on_restart_event	(GtkWidget *widget, gpointer data);
void on_scores_event 	(GtkWidget *widget, gpointer data);
void on_quit_event 		(GtkWidget *widget, gpointer data);
void on_undo_event 		(GtkWidget *widget, gpointer data);
void on_redo_event 		(GtkWidget *widget, gpointer data);
void on_online_help		(GtkWidget *widget, gpointer data);
void on_about_event 	(GtkImageMenuItem *widget, gpointer data);
void on_toolbar_toggled (GtkCheckMenuItem *widget, gpointer data);

/* playing area events */
gboolean button_press_event 	(GtkWidget *widget, GdkEventButton *event);
gboolean motion_notify_event	(GtkWidget *widget, GdkEventMotion *event);
gboolean on_expose_event 		(GtkWidget *widget, GdkEventExpose *event);
gboolean on_configure_event 	(GtkWidget *widget, gpointer data);

/* score table signals */
void on_score_ok_clicked  (GtkButton *widget, gpointer *data);
void on_score_new_clicked (GtkButton *widget, gpointer *data);
gboolean hide_score_event (GtkWidget *widget, GdkEvent *event, gpointer data);

/* preferences signals */
void on_preferences_event		(GtkWidget *widget, 	  gpointer data);
void on_ruleset_changed			(GtkComboBox *widget, 	  gpointer *data);
void on_clubs_lead_changed		(GtkToggleButton *widget, gpointer *data);
void on_hearts_break_changed	(GtkToggleButton *widget, gpointer *data);
void on_no_blood_changed		(GtkToggleButton *widget, gpointer *data);
void on_queen_breaks_hearts_changed	(GtkToggleButton *widget, gpointer *data);
void on_show_scores_changed		(GtkToggleButton *widget, gpointer *data);
void on_north_ai_changed		(GtkComboBox *widget, 	  gpointer *data);
void on_east_ai_changed			(GtkComboBox *widget, 	  gpointer *data);
void on_west_ai_changed			(GtkComboBox *widget, 	  gpointer *data);
void on_card_style_changed		(GtkComboBox *widget, 	  gpointer *data);
void on_prefs_ok_clicked		(GtkButton *widget, 	  gpointer *data);
gboolean prefs_delete_event 	(GtkWidget *widget, 	  GdkEvent *event, 	gpointer data);

/* hint signals */
void on_hint_event 		 (GtkWidget *widget, gpointer data);
void on_hide_ok_clicked  (GtkButton *widget, gpointer *data);
gboolean hide_hint_event (GtkWidget *widget, GdkEvent *event, gpointer data);

#endif
