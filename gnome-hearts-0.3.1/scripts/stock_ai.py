# Hearts - stock_ai.py
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

# This is a simple stock AI used for the standard players and the "hint" feature. It's not too
# smart overall, but it works.

from definitions import *
from player import Player
from player_api import *

class StockAI(Player):
	"""This is the default AI for gnome-hearts"""
	
	def s_points_and_high_spades(self, a, b):
		"""
		Similar to the standard s_points sorting function, but this counts the King and Ace
		of Spades as point cards as well, making sure the player tries to get rid of them.
		"""
		if a == (spades, queen): return 1
		if b == (spades, queen): return -1
		if a == (spades, ace_high): return 1
		if b == (spades, ace_high): return -1
		if a == (spades, king): return 1
		if b == (spades, king): return -1
		if a[0] == hearts and b[0] != hearts: return 1
		if b[0] == hearts and a[0] != hearts: return -1
		return a[1] - b[1]

	def s_spades_priority(self, a, b):
		""" spade priority = J,10,9,8,7,6,5,4,3,2,A,K,Q followed by the other suits """
		if a[0] == spades and b[0] != spades: return 1
		if b[0] == spades and a[0] != spades: return -1
		if a[1] >= queen and b[1] < queen: return 1
		if b[1] >= queen and a[1] < queen: return -1
		return b[1] - a[1]
	
	def select_cards(self, direction):
		"""Return a list of three cards hat will be passed to an opponent"""
		result = []
		
		def select(card):
			result.append(card)
			self.hand.remove(card)
		
		# First pass on the high spades	
		if (spades, queen)    in self.hand: select((spades, queen))
		if (spades, king)     in self.hand: select((spades, king))
		if (spades, ace_high) in self.hand: select((spades, ace_high))
		
		# Pass off the other cards
		while len(result) < 3:
			clubs_list    = filter(f_clubs, self.hand)
			diamonds_list = filter(f_diamonds, self.hand)
			hearts_list   = filter(f_hearts, self.hand)
			
			# If we can clear a suit with one card then do so, else pick a hearts or a high card
			if len(clubs_list) == 1:
				select(clubs_list[0])
			elif len(diamonds_list) == 1:
				select(diamonds_list[0])
			elif len(hearts_list):
				hearts_list.sort(s_rank, reverse=True)
				select(hearts_list[0])
			else:
				self.hand.sort(s_rank, reverse=True)
				select(self.hand[0])
		return result
	
	def play_card(self):
		"""Play a card"""
		valid_cards = filter(self.f_valid, self.hand)
		
		# Open with the lowest valid card
		if self.trick.num_played == 0:
			valid_cards.sort(s_rank)
			#prevent scenario where, for example, player has QoS and KoS left - it will play QoS w/o the below check
			if valid_cards[0] == (spades, queen) and len(valid_cards) > 1:
				return valid_cards[1]
			return valid_cards[0]
		
		# Someone has already played. If the score is zero, it's not a point card
		if trick_get_score() == 0:
			# If we have a trump suit, take it with the highest card
			if have_suit(self.hand, self.trick.trump):
				valid_cards.sort(s_rank, reverse=True)

				# Spades are special because of the Queen
				if (self.trick.trump == spades):
					# Try dumping the Queen on someone else
					if (spades, king)     in self.trick.card and (spades, queen) in valid_cards: return (spades, queen)
					if (spades, ace_high) in self.trick.card and (spades, queen) in valid_cards: return (spades, queen)
					
					if self.trick.num_played == 3:
						# We're the last one playing and the queen isn't on the trick.
						# Take it with the Ace, King or anything below the Queen
						if valid_cards[0] == (spades, queen) and len(valid_cards) > 1:
							return valid_cards[1]
						return valid_cards[0]

					# Other people still have to play. Try not to play the Queen or anything above
					# because we may end up taking the points
					valid_cards.sort(self.s_spades_priority)
					return valid_cards[0]
			
				# Trump is diamonds or clubs. Play highest cards
				return valid_cards[0]
					
			# We don't have a trump. Dump a point card
			valid_cards.sort(self.s_points_and_high_spades, reverse=True)
			return valid_cards[0]
		
		# There are point cards on the trick
		if have_suit(self.hand, self.trick.trump):
			# Play the highest card that doesn't take the trick
			high_card = self.trick.get_highest_card()
			valid_cards.sort(s_rank, reverse=True)
			for card in valid_cards:
				if card[0] != high_card[0] or card[1] < high_card[1]: return card
			
			# We are forced to take the trick. Play highest card if we're the last player
			if self.trick.num_played == 3: 
				if valid_cards[0] == (spades, queen) and len(valid_cards) > 1:
					return valid_cards[1]
				else:
					return valid_cards[0]
			
			# Play low. Someone may beat us yet
			valid_cards.sort(s_rank)
			return valid_cards[0]
		else:
			# We don't have a trump. Dump a point card
			valid_cards.sort(self.s_points_and_high_spades, reverse=True)
			return valid_cards[0]
