# Hearts - player.py
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

from player_api import *

class Player:
	"""Base class of a player from which AI's are derived"""
	
	def __init__(self, direction, trick, score, rules):
		self.hand = []
		self.direction = direction
		self.trick = trick
		self.score = score
		self.rules = rules
		self.name = "Base"
	
	def set_hand(self, list):
		"""Set the hand of the player"""
		self.hand = list
	
	def get_name(self):
		"""Return the player's name"""
		return self.name
	
	def f_valid(self, card):
		return is_valid(card, self.direction)

	def select_cards(self, direction):
		return None

	def receive_cards(self, cards):
		return None;
		
	def play_card(self):
		return None
		
	def trick_end(self):
		return None
		
	def round_end(self):
		return None
