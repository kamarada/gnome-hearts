# Hearts - luis.py
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

# This AI is named after Luis Pedro, the creator of KDE Hearts and is essentially
# a port of his AI to Python.

from definitions import *
from player import Player
from player_api import *
from random import choice

class PlayerAI_Luis(Player):
	def __init__(self, direction, trick, score, rules):
		Player.__init__(self, direction, trick, score, rules)
		self.name = "Luis"
		self.hearts_played = False
		self.queen_played = False
		self.trick_starts = [0, 0, 0, 0]
	
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

	def open_trick(self):
		"""Open a trick"""
		# If I have only hearts, play the lowest
		if len(self.hand) == len(filter(f_hearts, self.hand)):
			return	self.hand[0]
		
		# If I have the two of clubs, play it
		# FIXME: This should honor the clubs_lead = false rule
		if (clubs, two) in self.hand:
			return (clubs, two)
		
		# If I don't have the queen of spades or higher and the queen hasn't been played, open with high spades
		if have_suit(self.hand, spades) and not self.queen_played and (not (spades, queen) in self.hand) and (not (spades, king) in self.hand) and (not (spades, ace_high) in self.hand):
			spades_list = filter(f_spades, self.hand)
			spades_list.sort(s_rank, reverse=True)
			return spades_list[0]
		
		# Try playing a suit that hasn't been played much
		if have_suit(self.hand, diamonds) and self.trick_starts[diamonds] < 2:
			diamonds_list = filter(f_diamonds, self.hand)
			diamonds_list.sort(s_rank, reverse=True)
			return diamonds_list[0]
		
		if have_suit(self.hand, clubs) and self.trick_starts[clubs] < 2:
			clubs_list = filter(f_clubs, self.hand)
			clubs_list.sort(s_rank, reverse=True)
			return clubs_list[0]
		
		# A low hearts to give them trouble
		# FIXME: Should honor hearts_broken = false
		if have_suit(self.hand, hearts) and self.hearts_played:
			hearts_list = filter(f_hearts, self.hand)
			hearts_list.sort(s_rank)
			max_hearts = 2 + ((self.trick_starts[hearts] + 1) * 3)
			if hearts_list[0][1] < max_hearts:
				return hearts_list[0]
		
		# Find a good card based on scores
		suits_to_try = []
		valid_cards = filter(self.f_valid, self.hand)
		for suit in range(4):
			if have_suit(valid_cards, suit) and self.trick_starts[suit] < 4:
				suits_to_try.append(suit)
		suits_to_try.sort(s_random)
		
		best_score, best_card, list = 0, None, []
		for suit in suits_to_try:
			if suit == clubs: list = filter(f_clubs, valid_cards)
			if suit == diamonds: list = filter(f_diamonds, valid_cards)
			if suit == spades: list = filter(f_spades, valid_cards)
			if suit == hearts: list = filter(f_hearts, valid_cards)
			list.sort(s_rank)
			score = 2 + ((self.trick_starts[suit] + 1) * 3) - list[0][1]
			if score > best_score:
				best_card = list[0]
		
		if best_card != None:
			return best_card
		
		# Give up. Play random
		return choice(valid_cards)
	
	def follow_suit(self):
		"""Play a card following the trick's trump"""
		# Play spades
		if self.trick.trump == spades:
			spades_list = filter(f_spades, self.hand)
			# Uh oh, I have the queen
			if (spades, queen) in spades_list:
				# See if I can dump the queen
				if (spades, king) in self.trick.card or (spades, ace_high) in self.trick.card:
					return (spades, queen)
				# Try playing something else but the queen
				spades_list.sort(s_rank)
				if spades_list[0] == (spades, queen):
					# return the highest card. Could be the queen if that's all we have.
					# Fixes bug #24
					return spades_list.pop()
				low_list = [card for card in spades_list if card[1] < queen]
				low_list.sort(s_rank, reverse=True)
				return low_list[0]
			# I don't have the queen
			if (spades, king) in self.hand or (spades, ace_high) in self.hand:
				if self.trick.num_played == 3 and not (spades, queen) in self.trick.card:
					spades_list.sort(s_rank, reverse=True)
					return spades_list[0]
				spades_list.sort(s_rank)
				if spades_list[0][1] >= king:
					# Forced to play high spades
					return spades_list.pop()
				low_list = [card for card in spades_list if card[1] < king]
				low_list.sort(s_rank, reverse=True)
				return low_list[0]
			spades_list.sort(s_rank, reverse=True)
			return spades_list[0]
		
		# Play hearts
		if self.trick.trump == hearts:
			hearts_list = filter(f_hearts, self.hand)
			hearts_list.sort(s_rank)
			highest_card = self.trick.get_highest_card()
			if hearts_list[0][1] > highest_card[1]:
				if self.trick.num_played == 3  or (self.trick.num_played == 2 and hearts_list[0][1] > highest_card[1] + 3):
					# I'm going to get it anyway, so play the highest
					return hearts_list.pop()
				return hearts_list[0]
			# Play highest hearts that doesn't win
			low_list = [card for card in hearts_list if card[1] < highest_card[1]]
			if len(low_list):
				low_list.sort(s_rank, reverse=True)
				return low_list[0]
			# Play lowest card
			hearts_list.sort(s_rank)
			return hearts_list[0]
			
		# Play clubs or diamonds
		suit_list = []
		if self.trick.trump == clubs:
			suit_list = filter(f_clubs, self.hand)
		else:
			suit_list = filter(f_diamonds, self.hand)
		# Play high card if I don't take the queen of hearts
		if self.trick_starts[self.trick.trump] < 2 and not (spades, queen) in self.trick.card:
			suit_list.sort(s_rank, reverse=True)
			return suit_list[0]
		# If I'm the last in the trick, take with high card
		if self.trick.num_played == 3 and not (spades, queen) in self.trick.card:
			suit_list.sort(s_rank, reverse=True)
			return suit_list[0]
		# Play the highest card that doesn't win the trick
		highest_card = self.trick.get_highest_card()
		low_list = [card for card in suit_list if card[1] < highest_card[1]]
		if len(low_list):		
			low_list.sort(s_rank)
			return low_list[0]
		# Play lowest card
		suit_list.sort(s_rank)
		return suit_list[0]
	
	def dont_follow_suit(self):
		"""Play a card when I have no trump cards"""
		valid_cards = filter(self.f_valid, self.hand)
		
		if (spades, queen) in valid_cards: return (spades, queen)
		if (spades, king) in valid_cards: return (spades, king)
		if (spades, ace_high) in valid_cards: return (spades, ace_high)
		
		valid_cards.sort(s_rank, reverse=True)
		highest_card = valid_cards[0]
		
		if highest_card[1] < 8 and have_suit(valid_cards, hearts):
			hearts_list = filter(f_hearts, valid_cards)
			hearts_list.sort(s_rank, reverse=True)
			return hearts_list[0]
		
		return highest_card

	def play_card(self):
		"""Play a card"""
		if self.trick.num_played == 0:
			return self.open_trick()
		elif have_suit(self.hand, self.trick.trump):
			return self.follow_suit()
		else:
			return self.dont_follow_suit()
	
	def trick_end(self):
		"""remember the trick starts"""
		self.trick_starts[self.trick.trump] = self.trick_starts[self.trick.trump] + 1
		# Update local variables
		if have_suit(self.trick.card, hearts):
			self.hearts_broken = True
		if (spades, queen) in self.trick.card:
			self.queen_played = True
	
	def round_end(self):
		"""Reset some variables"""
		self.hearts_played = False
		self.trick_starts = [0, 0, 0, 0]
