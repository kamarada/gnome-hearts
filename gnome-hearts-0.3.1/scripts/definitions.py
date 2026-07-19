# Hearts - definitions.py
# Copyright 2006 Sander Marechal
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

from random import random

# The cards, suits and directions
clubs, diamonds, hearts, spades = 0, 1, 2, 3
ace, two, three, four, five, six, seven, eight, nine, ten, jack, queen, king, ace_high = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14
north, east, south, west = 0, 1, 2, 3

# Some usefull functions
def have_suit(list, suit):
	"""Test if the list contains any cards of the suit"""
	for card in list:
		if card[0] == suit:
			return True
	return False

# The functions below can be used for filters. Call them like result = filter(function, list)
def f_clubs(card):    return type(card) == tuple and card[0] == clubs
def f_diamonds(card): return type(card) == tuple and card[0] == diamonds
def f_hearts(card):   return type(card) == tuple and card[0] == hearts
def f_spades(card):   return type(card) == tuple and card[0] == spades

def f_pointless_cards(card): return type(card) == tuple and card[0] != hearts and card != (spades, queen) # FIXME: Doesn't take into account any rules
def f_point_cards(card): return type(card) == tuple and (card[0] == hearts or card == (spades, queen)) # FIXME: Doesn't take into account any rules

# The functions below can be used for sorting. Call them like list.sort(function) or list.sort(function, reverse=True)
def s_rank(a, b): return (a[1] * 10 + a[0]) - (b[1] * 10 + b[0])
def s_suit(a, b): return (a[0] * 13 + a[1]) - (b[0] * 13 + b[1])

def s_points(a, b):
	if a == (spades, queen): return 1
	if b == (spades, queen): return -1
	if a[0] == hearts and b[0] != hearts: return 1
	if b[0] == hearts and a[0] != hearts: return -1
	return a[1] - b[1]

def s_random(a, b):
	if random() > 0.5:
		return 1
	return -1
