/*
 *  Hearts - hearts.h
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
 
#ifndef HEARTS_H
#define HEARTS_H

/* Must be inlcuded first */
#include <Python.h>

/* headers */
#include <glib/gi18n.h>
#include <dirent.h>
#include <gnome.h>
#include <glade/glade.h>
#include "cards.h"
#include "cfg.h"
#include "player.h"
#include "player-api.h"
#include "ui.h"

/* the game states */
enum
{
	GAME_SELECT_CARDS	= 0,
	GAME_PASS_CARDS		= 1,
	GAME_RECIEVE_CARDS	= 2,
	GAME_PLAY			= 3,
	GAME_ROUND_END		= 4,
	GAME_END			= 5
};

/* the game's globals */
extern Trick 	 	game_trick;
extern gint 	 	game_state;
extern gint 	 	game_pass;
extern gint 	 	game_trick_winner;
extern gboolean  	game_hearts_broken;
extern CardsDeck 	*game_deck;
extern GList	 	*game_score_labels;

/* the players */
extern Player 	*player[4];
extern gint 	user;

/* forward declarations */
GdkPixmap* get_pixmap (const char *filename);

void	 game_new (void);
void	 game_new_round (void);
void	 game_restart_round (void);
void 	 game_open_round (void);
gboolean game_end_test (void);
gboolean game_pass_cards (GtkWidget *widget);
gint 	 game_select_cards (GtkWidget *widget);
void 	 game_score_publish(void);
gboolean game_is_valid_card (Card *card, CardsHand *hand, Trick *trick);
gchar*	 game_get_hint(void);
void	 game_set_status(gchar *message);

int  main (int argc, char *argv[]);

#endif
