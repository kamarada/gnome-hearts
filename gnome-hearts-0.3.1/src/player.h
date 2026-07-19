/*
 *  Hearts - player.h
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

#ifndef GAME_H
#define GAME_H

#include "cards.h"
#include "player-api.h"

/* the players */
typedef struct _Player
{
	gint		direction;
	gint 	  	score_round;
	gint 	  	score_total;
	gchar		*name;
	CardsHand 	*hand;
	GList		*cards_taken;
	PangoLayout *layout;
	PyObject	*ai;
	Trick 		*trick;
} Player;

/* functions for the player */
Player* player_new (gint direction, gboolean show_faces, gchar *script, Trick *trick, GtkWidget *widget);
Card* 	player_play (Player *player);
GList* 	player_select_cards (Player *player);
void	player_receive_cards (Player *player, GList *list);
void	player_trick_end(Player *player);
void	player_round_end(Player *player);
void 	player_play_card (Player *player, Card *card);
void	player_mark_selected(Player *player, GList *list);
void	player_take_trick(Player *player, Trick *trick);
void	player_publish_hand (Player *player);
void 	player_free (Player *player);

#endif
