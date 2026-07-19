# Hearts - peter.py Version 1.0
# Copyright 2008 Charles A. Crayne
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

from definitions import *
from player import Player
from player_api import *
from random import choice

# Global Definitions
left, across, right, keep = 0, 1, 2, 3	# pass directions

def f_low(card):    return type(card) == tuple and card[1] < six
def f_high(card):   return type(card) == tuple and card[1] > ten
def f_mid(card):    return type(card) == tuple and five < card[1] < jack
def f_below_queen(card): return type(card) == tuple and card[1] < queen
def f_top_two(card):	return type(card) == tuple and card[1] > queen
def f_top_three(card):	return type(card) == tuple and card[1] > jack
def f_not_spade(card):    return type(card) == tuple and card[0] != spades
def f_minor(card): return type(card) == tuple and card[0] < hearts
def deal():
	list =[]	
	for suit in range(clubs, spades+1):
	    for rank in range(two, ace_high+1):
	       list.append( (suit, rank) )
	return list

def list_suit(list, suit):
	"""
	Return a list of all cards in the given list
	which are of the given suit
	"""
	suit_list = []
	for card in list:
		if card != None and card[0] == suit:
			suit_list.append(card)
	return suit_list
def diff(list1, list2):
	"""Return a list of those cards in list1 which are not in list1"""
	diff_list = []
	for card in list2:
		if card not in list1:
			diff_list.append(card)
	return diff_list

# Class Definitions
class PlayerAI_Peter(Player):
	def __init__(self, direction, trick, score, rules):
		Player.__init__(self, direction, trick, score, rules)
		self.name = "Peter"
		self.hearts_played = False
		self.queen_played = False
                self.shooting = False
                self.hearts_split = False
		self.can_shoot = True
                self.pass_dir = left
		self.deck = []
                self.out_spades = []
                self.out_hearts = []
                self.out_diamonds = []
                self.out_clubs = []
                self.suit_counts = []
		self.void_counts = []
                self.pass_cards = []
		self.received_cards = []
		self.trick_num = 1
		self.bonus_card = [None]

	
	def entry(self, suit_list):
		"""
		Returns true if suit_list contains
		  Highest unplayed card in the suit
		  or the second highest unplayed card
        	  and at least one lower card
		  or the third highest unplayed card
        	  and at least two lower cards . . .
		"""
        	if len(suit_list):
			suit_list.sort(s_rank, reverse=True)
			if self.num_above(suit_list[0]) < len(suit_list):
				return True
		return False

	def num_out(self, suit):
		"""
		Returns the number of cards in the suit
		which are still in the deck
		"""
		deck_list = list_suit(self.deck, suit)
		return len(deck_list)

	def num_below(self, card):
		"""
		Returns number of outstanding cards
		in this suit which can duck this card
		"""
		count = 0
		deck_list = list_suit(self.deck, card[0])
		if not len(deck_list): return 0
		deck_list.sort(s_rank)
		for dcard in deck_list:
			if card[1] > dcard[1]:
				count = count + 1
		return count

	def num_above(self, card):
		"""
		Returns number of outstanding cards
		in this suit which can beat this card
		"""
		count = 0
		deck_list = list_suit(self.deck, card[0])
		if not len(deck_list): return 0
		deck_list.sort(s_rank)
		for dcard in deck_list:
			if card[1] < dcard[1]:
				count = count + 1
		return count

	def is_runnable(self, suit):
		"""
		Returns true if, for each high card in decending sequence,
		and assuming that the highest outstanding card will fall on each trick,
		and that the outstanding cards are not all in the same hand, unless
		there is evidence to the contrary, every card in the suit will take a trick,
		and the suit is long enough to produce a reasonable number of discards
		"""
		suit_list = list_suit(self.hand, suit)
		suit_length = len(suit_list)
		if not suit_length: return False
		if not self.num_discards(suit): return False
		deck_list = list_suit(self.deck, suit)
		deck_length = len(deck_list)
		if not deck_length: return True
		deck_list.sort(s_rank, reverse=True)
		suit_list.sort(s_rank, reverse=True)
		for index in range(suit_length):
			if index >= deck_length: return True
			if suit_list[index][1] < deck_list[index][1]: return False
			if self.num_players_have(suit): deck_length = deck_length -1
		return True

	def is_duckable(self, suit):
		"""
		Returns true if, for each high card in decending sequence,
		and assuming that the other players will try to duck the trick,
		there is a reasonable chance that every card in the suit will take a trick.
		"""
		deck_list = list_suit(self.deck, suit)
		deck_length = len(deck_list)
		if not deck_length: return True
		suit_list = list_suit(self.hand, suit)
		suit_length = len(suit_list)
		if not suit_length: return False
		suit_list.sort(s_rank, reverse=True)
		deck_list.sort(s_rank, reverse=True)
		num_played = self.num_players_have(suit)
		deck_index = 0
		for card in suit_list:
			if deck_index >= deck_length: return False
			while card[1] < deck_list[deck_index][1]:
				deck_index = deck_index + 1
				if deck_index >= deck_length: return False
			if deck_length - deck_index < 5: return False
			deck_index = deck_index + num_played
			if deck_index > deck_length: return False
		return True

	def players_void(self, suit):
		"""Return a list of players who are void in the given suit"""
		list = []
		for entry in self.void_counts:
			if entry[0] == suit and entry[1] != self.direction:
				list.append(entry[1])
		return list

	def num_players_have(self, suit):
		"""Return the number of players who are not void in the given suit"""
		return 3 - len(self.players_void(suit))

	def num_discards(self, suit):
		"""
		Returns the minimum number of discards the suit will draw if run.
		"""
		suit_length = len(list_suit(self.hand, suit))
		deck_length = len(list_suit(self.deck, suit))
		follow = min(self.num_players_have(suit) * suit_length, deck_length)
		return suit_length * 3 - follow

	def list_safe(self,suit):
		"""
		Returns a list of all cards in the given suit which
		are lower then the corresponding card of that suit in the deck
		"""
		safe_list = []
		deck_list = list_suit(self.deck, suit)
		if not len(deck_list): return safe_list
		deck_list.sort(s_rank)
		hand_list = list_suit(self.hand, suit)
		hand_list.sort(s_rank)
		index = 0
       		for card in hand_list:
			if card[1] < deck_list[index][1]:
				safe_list.append(card)
       		        index = index +1
			if index >= len(deck_list): break
		return safe_list

	def num_top_two_spades(self, list):
		"""
		Returns number of spades above queen in list
		"""
		spades_list = filter(f_spades, list)
		top_list = filter(f_top_two, spades_list)
		return len(top_list)

	def num_top_three_spades(self, list):
		"""
		Returns number of spades above jack in list
		"""
		spades_list = filter(f_spades, list)
		top_list = filter(f_top_three, spades_list)
		return len(top_list)

# Select Cards Definitions
	def select_cards(self, direction):
		"""
		Return a list of three cards that will be passed
		to the opponent specified by direction
		"""
		def select(card):
			self.pass_cards.append(card)
			self.hand.remove(card)

		def pass_to_shoot():
			"""
			Returns true if the hand contains
			  Above average high card points
			  Entries in all non-void suits
			"""
			points = 0
			for card in self.hand:
				if card[1] == ace: points = points + 4
				if card[1] == king: points = points + 3
				if card[1] == queen: points = points + 2
				if card[1] == jack: points = points + 1
			if points < 13: return False
                	if not self.entry(clubs_list): return False
                	if not self.entry(diamonds_list): return False
                	if not self.entry(hearts_list): return False
                        if not self.entry(spades_list): return False
                	return True

		def safe_spades():
			"""
			Returns true if the hand contains
			  At least five spades
                          At least three spades below the queen
			"""
			if len(spades_list) > 4: return True
			list = filter(f_below_queen, spades_list)
                        if len(list) > 2: return True
                        return False

# Select Cards Code
		# Remember pass direction
                self.pass_dir = (direction - self.direction + 3) % 4
		# Set bonus card for Omnibus ruleset
		if self.rules.ruleset == 'omnibus': self.bonus_card = (diamonds, jack)
		elif self.rules.ruleset == 'omnibus_alt': self.bonus_card = (diamonds, ten)
		else: self.bonus_card = None
		# Create deck of unseen cards      		
		self.deck = deal()
		for card in self.hand:
			self.deck.remove(card)
		self.pass_cards = []
                goal = 0	# no goal set
                # Analyze hand 
		clubs_list    = filter(f_clubs, self.hand)
                low_clubs     = filter(f_low, clubs_list)
                mid_clubs     = filter(f_mid, clubs_list)
                high_clubs    = filter(f_high, clubs_list)
		diamonds_list = filter(f_diamonds, self.hand)
                low_diamonds     = filter(f_low, diamonds_list)
                mid_diamonds     = filter(f_mid, diamonds_list)
                high_diamonds    = filter(f_high, diamonds_list)
		hearts_list   = filter(f_hearts, self.hand)
                low_hearts     = filter(f_low, hearts_list)
                mid_hearts     = filter(f_mid, hearts_list)
                high_hearts    = filter(f_high, hearts_list)
                spades_list = filter(f_spades, self.hand)
                low_spades     = filter(f_low, spades_list)
                mid_spades     = filter(f_mid, spades_list)
                high_spades    = filter(f_high, spades_list)
                low_count      = [len(low_clubs), len(low_diamonds), len(low_hearts), len(low_spades)]
                mid_count      = [len(mid_clubs), len(mid_diamonds), len(mid_hearts), len(mid_spades)]
                high_count      = [len(high_clubs), len(high_diamonds), len(high_hearts), len(high_spades)]

		if pass_to_shoot():
			while len(self.pass_cards) < 3:
				clubs_list    = filter(f_clubs, self.hand)
				diamonds_list = filter(f_diamonds, self.hand)
				spades_list   = filter(f_spades, self.hand)
				hearts_list   = filter(f_hearts, self.hand)
				# Pass unduckable hearts
				hearts_list.sort(s_rank)
				if not self.is_duckable(hearts): select(hearts_list[0])
				# Pass spades below the Queen
				if len(spades_list) and spades_list[0][1] < queen: select(spades_list[0])
				# Pass deuce of clubs (if must be led)
				elif (clubs, two) in self.hand and len(clubs_list) < 5 \
				   and self.rules.clubs_lead: select((clubs, two))
				# Pass lowest cards in hand
				else:
					self.hand.sort(s_rank)
					select(self.hand[0])
			return self.pass_cards
			

		# Only pass spades as a last resort
                if not safe_spades():
			if (spades, queen) in self.hand:
				select((spades, queen))
				if (spades, ace_high) in self.hand: select((spades, ace_high))
				if (spades, king)     in self.hand: select((spades, king))
				
			else:
                        	if len(clubs_list) < 4:
                                   for i in range(len(clubs_list)): select(clubs_list[i])
                        	elif len(diamonds_list) <  4:
                                   for i in range(len(diamonds_list)): select(diamonds_list[i])
                        	else:
					if (spades, ace_high) in self.hand: select((spades, ace_high))
					if (spades, king)     in self.hand: select((spades, king))
                                     
		
		# Pass off the other cards
		while len(self.pass_cards) < 3:
			clubs_list    = filter(f_clubs, self.hand)
			diamonds_list = filter(f_diamonds, self.hand)
			hearts_list   = filter(f_hearts, self.hand)
			hearts_list.sort(s_rank, reverse=True)
			safe_hearts = self.list_safe(hearts)
			# If we can clear a minor suit do so,
			# unless Omnibus ruleset and we have the bonus card
                        # else pick an unsafe heart or the highest minor
			# If spots ruleset, pass unsafe hearts first
			if self.rules.ruleset == 'spot_hearts':
				if len(hearts_list) and hearts_list[0] not in safe_hearts \
				  and hearts_list[0][1] > 6:
                                	select(hearts_list[0])
					continue
			if len(clubs_list) and len(clubs_list) <= 3 - len(self.pass_cards):
				clubs_list.sort(s_rank, reverse=True)
				select(clubs_list[0])
			elif len(diamonds_list) and len(diamonds_list) <= 3 - len(self.pass_cards) \
			   and (self.bonus_card == None or self.bonus_card not in self.hand):
				diamonds_list.sort(s_rank, reverse=True)
				select(diamonds_list[0])
			elif len(hearts_list) and hearts_list[0] not in safe_hearts \
			   and hearts_list[0][1] > 6:
                                select(hearts_list[0])
			else:
				list = filter(f_minor, self.hand)
                                list.sort(s_rank, reverse=True)
                                if len(list): select(list[0])
                                else:
					self.hand.sort(s_rank, reverse=True)
					select(self.hand[0])
		return self.pass_cards

# Receive Cards Code
	def receive_cards(self, cards):
		"""
		Receives a list of cards passed
		"""
		self.received_cards = cards

# Play Card Definitions	
	def play_card(self):
		"""Play a card"""

		def deck_is_risky():
			"""
			Return true if more than half of the total points
			are still in the deck.
			"""
			if self.rules.ruleset == 'spot_hearts': risk = 65
			else: risk = 13
			if list_cost(self.deck) >= risk: return True
			return False

		def list_1below(list):
			"""
			Returns list of cards which only one
			outstanding card can duck
			"""
			below_list = []
			for card in list:
				if self.num_below(card) == 1 and self.num_above(card):
					below_list.append(card)
			return below_list

		def is_winner(card):
			""" Returns true if card will win trick """
			deck_list = list_suit(self.deck, card[0])
			if not len(deck_list): return True
			deck_list.sort(s_rank, reverse=True)
			if card[1] > deck_list[0][1]: return True
			return False

		def is_exit(card):
			""" Returns true if card will lose trick """
			deck_list = list_suit(self.deck, card[0])
			if not len(deck_list): return False
			deck_list.sort(s_rank)
			if card[1] < deck_list[0][1]: return True
			return False
	
		def list_exit(suit):
			"""
			Returns a list of all cards in the given suit which
			are lower then the lowest card of that suit in the deck
			"""
			exit_list = []
			deck_list = list_suit(self.deck, suit)
			if not len(deck_list): return exit_list
			deck_list.sort(s_rank)
			hand_list = list_suit(self.hand, suit)
			hand_list.sort(s_rank)
        		for card in hand_list:
				if card[1] < deck_list[0][1]:
					exit_list.append(card)
			return exit_list

		def suits_void(player):
			"""Return a list of suits in which a given player is void"""
			list = []
			for entry in self.void_counts:
				if entry[1] == player:
					list.append(entry[0])
			return list

		def yet_to_play():
			"""Return a list of players who have not played to the trick"""
			list = []
			for player in range(4):
				if self.trick.card[player] == None and player != self.direction:
					list.append(player)
			return list

		def list_high(suit):
			"""
			Return list of cards in the hand which are higher than
			two-thirds of the cards of the given suit in the deck
			"""
			hand_list = list_suit(self.hand, suit)
			if not len(hand_list): return hand_list
			deck_list = list_suit(self.deck, suit)
			if not len(deck_list): return hand_list
			deck_list.sort(s_rank, reverse = True)
			if len(deck_list) > 2: index = len(deck_list)/3
			else: index = len(deck_list) - 1
			limit = deck_list[index][1]
			return_list = []
			for card in hand_list:
				if card[1] > limit:
					return_list.append(card)
			return return_list


		def list_low(suit):
			"""
			Return list of cards in the hand which are lower than
			two-thirds of the cards of the given suit in the deck
			"""
			return_list = []
			hand_list = list_suit(self.hand, suit)
			if not len(hand_list): return return_list
			deck_list = list_suit(self.deck, suit)
			if not len(deck_list): return return_list
			deck_list.sort(s_rank)
			if len(deck_list) > 2: index = len(deck_list)/3
			else: index = len(deck_list) - 1
			limit = deck_list[index][1]
			for card in hand_list:
				if card[1] < limit:
					return_list.append(card)
			return return_list

		def sole_shooter():
			"""
			If only one player has taken points,
			and that player is not ouself, return
			a one element list with the player
			number, and the number of points taken.
			"""
			score_list = []
			for index in range(4):
				if self.score.round[index]:
					score_list.append((index, self.score.round[index]))
			if len(score_list) == 1 and score_list[0][0] != self.direction:
				return score_list
			return []

		def trick_leader():
			"""
			Return the direction of the opponent who
			played the highest card in the current trick
			"""
			for index in range(4):
				if self.trick.card[index] == self.trick.get_highest_card():
					return index
			return None

		def can_shooter_win():
			"""
			Return true if sole shooter is the trick leader,
			or has not played and and there are outstanding cards
			above the current highest card.
			"""
			shooter = sole_shooter()
			if not len(shooter): return False
			if shooter[0][0] == trick_leader(): return True
			if has_played(shooter[0][0]): return False
			if self.num_above(self.trick.get_highest_card()): return True
			return False

		def has_played(player):
			"""
			Returns true if player has already played
			to the current trick.
			"""
			return self.trick.card[player] != None

		def last_to_play():
			"""
			Returns true if in 4th position,
			or all remaining players have are known
			to be void in the suit led.
			"""
			if self.trick.num_played == 3: return True
			yet_list = yet_to_play()
			play_list = self.players_void(self.trick.trump)
			for player in yet_list:
				if player not in play_list:
					return False
			return True
				
		def list_cost(list):
			"""
			Returns the total point value of cards
			in the specified list
			"""
			cost = 0
			for card in list:
				if card != None:
					if self.rules.ruleset == 'spot_hearts':
						if card == (spades, queen): cost = cost + 25
						if card[0] == hearts: cost = cost + card[1]
					else:
						if card == (spades, queen): cost = cost + 13
						if card[0] == hearts: cost = cost + 1
			return cost
					
		def suit_score(suit):
			"""
			Returns a score indicating the risk that
			the highest card in the given suit will
        		be forced to take an unwanted trick.
			"""
			suit_score = 0
			if have_suit(self.hand, suit) and have_suit(self.deck, suit):
				suit_list = list_suit(self.hand, suit)
				suit_list.sort(s_rank, reverse=True)
				suit_score = self.num_below(suit_list[0]) \
				  - 2 * len(suit_list) + 1
			return suit_score

		def try_to_shoot():
			"""
			Returns a non-zero indicating the reason why it is
			reasonable to try to shoot, else returns zero
			Have already taken half of the total points (2)
			Have the unprotected Queen and no short minor suits (3)
			If in the lead, and have an exit problem (7)
			Have a hand with all of the following: (4,5,6)
			  Duckable hearts, or none at all
                	  At least one runnable suit
                          If not in the lead, entries in non-void minor suits
			"""
			clubs_list = list_suit(self.hand, clubs)
			diamonds_list = list_suit(self.hand, diamonds)
			hearts_list = list_suit(self.hand, hearts)
			spades_list = list_suit(self.hand, spades)
			runnable_suits = 0
			discards = 0
			for suit in range(4):
				if self.is_runnable(suit): runnable_suits = runnable_suits + 1
				discards = discards + self.num_discards(suit)
			if not runnable_suits: return 0
			if self.rules.ruleset != 'spot_hearts' and self.score.round[self.direction] >= 13:
				return 2
			if self.rules.ruleset == 'spot_hearts' and self.score.round[self.direction] >= 64:
				return 2
			if (spades, queen) in spades_list and len(spades_list) < 4 \
			  and len(clubs_list) > 2 and len(diamonds_list) > 2: return 3
			if not self.trick.num_played and exit_problem(): return 7
			if len(hearts_list):
        	                if not self.is_duckable(hearts) and not self.is_runnable(hearts): return 0
			if self.trick.num_played:
        	                if len(clubs_list) and not self.entry(clubs_list): return 0
        	                if len (diamonds_list) and not self.entry(diamonds_list): return 0
                	return 4

		def open_trick():
			"""Open a trick"""
        	        # Special rule for breaking hearts by leading hearts
			# If I have only hearts, and it is still possible to shoot,
			# and I have the top heart, then play it. Otherwise, play
			# the lowest heart.
			if len(self.hand) == len(filter(f_hearts, self.hand)):
				self.hand.sort(s_rank, reverse=True)
				card = self.hand[0]
				if is_winner(card) and self.can_shoot and self.is_runnable(hearts):
					return	self.hand[0]
				self.hand.sort(s_rank)
				return self.hand[0]

			# Special rule for leading the queen of spades
			if (spades, queen) in self.hand and len(self.out_spades):
				deck_list = filter(f_spades, self.deck)
				if len(deck_list) == self.num_above((spades,queen)):
					return (spades, queen)

			# Special rule for leading the bonus card
			if self.bonus_card != None and self.bonus_card in self.hand \
			   and not self.num_above(self.bonus_card):
				return self.bonus_card

			# If queen of spades is still in the deck, try to flush it
			if have_suit(self.hand, spades) and (spades, queen) in self.deck:
				spades_list = filter(f_spades, self.hand)
                                flush_list = filter(f_below_queen, spades_list)
				if len(flush_list):
                                	high_list = filter(f_top_two, spades_list)
					player_num =  self.num_players_have(spades)
					out_num	= len(self.out_spades)
					if not len(high_list) or out_num == 1 \
				   	   or (len(flush_list) >= (out_num/player_num) \
                                             and len(flush_list) > 1):
						flush_list.sort(s_rank, reverse=True)
						return flush_list[0]
				# look for safe lead in a minor suit in which the holder of the
                                # queen might be void.

			# Establish safe spades
			if self.queen_played:
				if have_suit(self.hand, spades) and have_suit(self.deck, spades):
					spades_list = list_high(spades)
					spades_list.sort(s_rank, reverse=True)
					if len(spades_list):
						return spades_list[0]

			# Establish safe minor suits
			risky_suit = None			
			club_score = suit_score(clubs)
			diamond_score = suit_score(diamonds)
			if club_score > 0 and club_score > diamond_score: risky_suit = clubs
			elif diamond_score > 0: risky_suit = diamonds
			if risky_suit != None:
				risky_list = list_suit(self.hand, risky_suit)
				risky_list.sort(s_rank, reverse=True)
				# If the deck is not risky,
				# and I do not have an exit problem,
				# lead most unprotected minor card
				if not deck_is_risky() \
				  or (not spade_problem and self.num_out(risky_suit) > 4 \
                                      and self.num_players_have(risky_suit) == 3):
					return risky_list[0]

			# Spread some hearts around
			if self.hearts_played and have_suit(self.hand, hearts) and len(self.out_hearts):
				hearts_list = filter(f_hearts, self.hand)
				hearts_list.sort(s_rank)
				if hearts_list[0] < self.out_hearts[0]:
				   return hearts_list[0]

			# Get out of lead without too much risk
			# See if there are any exit cards
			exit_suits = []
			for suit in range(4):
                        	list = list_exit(suit)
				if len(list):
					if suit == hearts and not self.hearts_played: continue
					if suit == spades and not safe_spade_lead(): continue
					exit_suits.append(suit)

			# See if there are any "one below" cards
			below_suits = []
			below_list = list_1below(self.hand)
			for suit in range(4):
                        	list = list_suit(below_list, suit)
				if len(list):
					if suit == hearts and not self.hearts_played: continue
					if suit == spades and not safe_spade_lead(): continue
					below_suits.append(suit)


			# See if there are any safe cards
			safe_suits = []
			for suit in range(4):
                        	list = self.list_safe(suit)
				if len(list):
					if suit == hearts and not self.hearts_played: continue
					if suit == spades and not safe_spade_lead(): continue
					safe_suits.append(suit)

			if (spades, queen) in self.deck:
				if len(exit_suits):
        	        		# Play an exit card
					exit_suits.sort(s_random)
					for suit in exit_suits:
						if suit == spades and not safe_spade_lead(): continue
						list = list_suit(self.hand, suit)
						return list[0]
				if len(below_suits):
        	        		# Play a below card
					below_suits.sort(s_random)
					for suit in below_suits:
						if suit == spades and not safe_spade_lead(): continue
						list = list_suit(self.hand, suit)
						return list[0]
				if len(safe_suits):
        	        		# Play a safe card
					safe_suits.sort(s_random)
					for suit in safe_suits:
						if suit == spades and not safe_spade_lead(): continue
						list = list_suit(self.hand, suit)
						return list[0]
				# Play the card which can be beat by the most
				# cards in the deck
				most_above = 0
				best_card = None
				for suit in range(4):
                        		list = list_suit(self.hand, suit)
					if len(list):
						if suit == hearts and not self.hearts_played: continue
						if suit == spades and not safe_spade_lead(): continue
						card = list[0]
						if self.bonus_card != None and self.bonus_card in list \
						   and len(list) > 1: list.remove(self.bonus_card)
						above = self.num_above(card) 
						if above > most_above:
							most_above = above
							best_card = card
				if best_card != None: return best_card

			# The queen is not in the deck, so lead a relatively high card 
			# Play the highest card which can be beat by at least
			# four cards in the deck
			high_rank = 0
			best_card = None
			for suit in range(4):
                       		list = list_suit(self.hand, suit)
				if self.bonus_card != None and self.bonus_card in list \
				   and len(list) > 1: list.remove(self.bonus_card)
				if len(list):
					if suit == hearts and not self.hearts_played: continue
					low_list = list_low(suit)
					for card in list:
						if card in low_list: continue
						above = self.num_above(card) 
						if above > 3 and card[1] > high_rank:
							high_rank = card[1]
							best_card = card
			if best_card != None: return best_card

       	        	# Play a card which can be beat
			if have_suit(self.hand, diamonds) and len(self.out_diamonds):
				diamonds_list = filter(f_diamonds, self.hand)
				if self.bonus_card != None and self.bonus_card in list \
				   and len(list) > 1: list.remove(self.bonus_card)
				diamonds_list.sort(s_rank)
				if diamonds_list[0] < self.out_diamonds[-1]:
       	                	   return diamonds_list[0]
			if have_suit(self.hand, clubs) and len(self.out_clubs):
				clubs_list = filter(f_clubs, self.hand)
				clubs_list.sort(s_rank,)
				if clubs_list[0] < self.out_clubs[-1]:
				   return clubs_list[0]
			if self.hearts_played and have_suit(self.hand, hearts) and len(self.out_hearts):
				hearts_list = filter(f_hearts, self.hand)
				hearts_list.sort(s_rank)
				if hearts_list[0] < self.out_hearts[-1]:
				   return hearts_list[0]
			if have_suit(self.hand, spades) and len(self.out_spades):
				spades_list = filter(f_spades, self.hand)
				spades_list.sort(s_rank)
				card = spades_list[0]
				if card < self.out_spades[-1] and card != (spades, queen) \
                                         and card != (spades, king):
				   return spades_list[0]
			if have_suit(self.hand, hearts):
				minor_list = filter(f_minor, self.hand)
				if len(minor_list):
					return minor_list[0]
				if (spades, queen) in self.hand:
					spades_list = filter(f_spades, self.hand)
					spades_list.remove((spades, queen))
					if len(spades_list):
						return spades_list[0]
			# Abandon hope
			valid_cards = filter(self.f_valid, self.hand)
			return choice(valid_cards)


		def follow_suit():
		# If we get this far, then suit_list will have at least two entries
			"""Play a card following the trick's trump"""
			suit_list = list_suit(self.hand, self.trick.trump)
			suit_list.sort(s_rank)
			highest_card = self.trick.get_highest_card()
			trick_list = list_suit(self.trick.card, self.trick.trump)
			deck_list = list_suit(self.deck, self.trick.trump)
			deck_list.sort(s_rank)
			# If I must win this trick, do so with highest card,
			# with the following exceptions:
			# Queen of Spades - play next lowest (all rulesets)
			# Take with bonus card (Omnibus rulesets)
			# Take with lowest heart (Spot ruleset)
			if suit_list[0][1] > deck_list[-1][1] \
			  or (last_to_play() and suit_list[0][1] > highest_card[1]):
				if (spades, queen) in suit_list: suit_list.remove((spades, queen))
				if self.bonus_card != None and self.bonus_card in suit_list:
					return self.bonus_card
				if self.rules.ruleset == 'spot_hearts' and self.trick.trump == hearts:
					return suit_list[0]
				return suit_list[-1]

			
			# Play spades
			if self.trick.trump == spades:
				spades_list = filter(f_spades, self.hand)
				# I have the queen
				if (spades, queen) in spades_list:
					# See if I can dump the queen
					if (spades, king) in self.trick.card \
                                           or (spades, ace_high) in self.trick.card:
						return (spades, queen)
					# Try playing something else but the queen
					spades_list.sort(s_rank)
					if spades_list[0] == (spades, queen):
						# return the highest card.
                                                # Could be the queen if that's all we have.
						return spades_list.pop()
					low_list = [card for card in spades_list if card[1] < queen]
					low_list.sort(s_rank, reverse=True)
					return low_list[0]
				# Queen has been played
				if not (spades, queen) in self.deck:
					spades_list.sort(s_rank, reverse=True)
					return spades_list[0]
				# I don't have the queen
				if (spades, king) in self.hand or (spades, ace_high) in self.hand:
					spades_list.sort(s_rank, reverse=True)
					if self.trick.num_played == 3 and not (spades, queen) in self.trick.card:
						return spades_list[0]
					if already_played():
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
					if self.trick.num_played == 3  \
					   or not self.num_above(hearts_list[0]):
						# I'm going to get it anyway, so play the highest
						return hearts_list[-1]
					return hearts_list[0]
				# If someone is trying to shoot, put a spoke in their wheels
				shooter = sole_shooter()
				if len(shooter) and trick_leader() == shooter[0][0]:
					if self.rules.ruleset == 'spot_hearts' and shooter[0][1] > 64 \
					   or self.rules.ruleset != 'spot_hearts' and shooter[0][1] > 13: 
						if hearts_list[-1][1] > highest_card[1]:
							return hearts_list[-1]
						return hearts_list[-2]
				# Play highest heart that doesn't win
				card = duck_high(highest_card)
				if card != None:
					return card
				# Play lowest card
				hearts_list.sort(s_rank)
				return hearts_list[0]
			
			# Play clubs or diamonds

			# Special rule for 1st trick - always safe to take
			if self.trick_num == 1 and have_suit(self.hand, self.trick.trump) \
			   and self.rules.no_blood:
				suit_list.sort(s_rank, reverse=True)
				return suit_list[0]

			# Special rule for Omnibus ruleset
			if self.bonus_card != None and self.bonus_card in suit_list \
			   and not self.num_above(self.bonus_card): return self.bonus_card

			# If I can duck this suit forever, do so
			if len(trick_list) == len(deck_list) \
                           or len(self.list_safe(self.trick.trump)) == len(suit_list):
				low_list = [card for card in suit_list if card[1] < highest_card[1]]
				if len(low_list):		
					low_list.sort(s_rank, reverse=True)
					return low_list[0]

			# If I'm the last in the trick, take with high card,
			# or with bonus card if playing Omnibus ruleset
			if self.trick.num_played == 3 and not list_cost(self.trick.card) > 10:
				suit_list.sort(s_rank, reverse=True)
				if self.bonus_card != None and self.bonus_card in suit_list:
					if self.bonus_card[1] > highest_card[1]:
						return self.bonus_card
					elif len(suit_list) > 1: suit_list.remove(self.bonus_card)
				return suit_list[0]

			# Play high card if queen of spades not in deck
			# But don't play bonus card if Omnibus ruleset,
			# unless it will win the trick
			if self.suit_counts[self.trick.trump] > 4 \
			   and (not (spades, queen) in self.deck or already_played()):
				suit_list.sort(s_rank, reverse=True)
				if self.bonus_card != None and self.bonus_card in suit_list:
					if not self.num_above(self.bonus_card):
						return self.bonus_card
					elif len(suit_list) > 1: suit_list.remove(self.bonus_card)
				return suit_list[0]

			# Play the highest card that doesn't win the trick
			card = duck_high(highest_card)
			if card != None:
				return card

			# Play lowest card
			if self.bonus_card != None and self.bonus_card in suit_list \
			   and len(suit_list) > 1: suit_list.remove(self.bonus_card)
			suit_list.sort(s_rank)
			return suit_list[0]
	
		def dont_follow_suit():
			"""Play a card when I have no trump cards"""
			valid_cards = filter(self.f_valid, self.hand)
			# If the queen is in my hand, and not well
			# protected, dump it now
			if (spades, queen) in valid_cards and (spade_problem() or exit_problem):
				return (spades, queen)
			# If the queen is in the deck, give priority
			# to unprotected high cards
			# Else favor discarding hearts
			best_score = 0
			best_card = None
			for suit in range(4):
                       		list = list_suit(valid_cards, suit)
				list.sort(s_rank, reverse=True)
				if len(list):
					# Favor Queen over any other spades
					if (spades, queen) in list: card = (spades, queen)
					else: card = list[0]
					# If Omnibus ruleset, don't discard bonus_card or
					# any of its protectors
					if self.bonus_card != None and card == self.bonus_card: continue
					score = self.num_below(card)
					above = self.num_above(card)
					# Prefer high spades if queen still in deck
					# unless well protected
					if suit == spades and (spades, queen) in self.deck \
					   and card[1] > queen \
					   and len(list) - self.num_top_two_spades(self.hand) < 4:
						score = score + 5
					# Don't discard cards which can not take a trick
					if not score: continue
					# Favor entries and short suits
					if not above: score = score + 5
					if len(list) == 1: score = score + 5
					# Greatly prefer high hearts in Spot Hearts ruleset
					if self.rules.ruleset == 'spot_hearts' and suit == hearts:
						score = score + card[1]
					# Prefer hearts if Queen not in deck
					if suit == hearts and not (spades, queen) in self.deck:
						score = score + 1
						if heart_problem or not self.hearts_played:
							score = score + 4
						# Greatly prefer stopping a shoot
						shooter = sole_shooter()
						if len(shooter):
							if not can_shooter_win():
								score = score + 10
							else: score = score - 5
					# Prefer cards received in the pass
					if card in self.received_cards:
						score = score + 1
					# Update best values	
					if score > best_score:
						best_score = score
						best_card = card
			# Discard most dangerous card
			if best_card != None:
				return choice(list_peers(best_card))

			# Even if the Queen is well protected, now is a good time to play it
			if (spades, queen) in valid_cards: return (spades, queen)

			# As a last resort, play the highest valid card,
			# but not the bonus card
			if self.bonus_card != None and self.bonus_card in valid_cards \
			 and len(valid_cards) > 1: valid_cards.remove(self.bonus_card)
			valid_cards.sort(s_rank, reverse=True)
			highest_card = valid_cards[0]
			return highest_card

		def spade_problem():
			"""
			Spades are not a problem if:
			  The queen has been played
			  I have no spades
			  I have none of the top three spades
			  I have more spades than there are low spades
			  outstanding minus the number of other players
			  who have not show out of spades
			"""
			if self.queen_played: return False
			spades_list = filter(f_spades, self.hand)
			if not len(spades_list): return False
			if not self.num_top_three_spades(self.hand): return False
        	        if len(spades_list) \
                          > (self.num_below((spades, queen)) - self.num_players_have(spades)):
				return False
			return True

		def safe_spade_lead():
			"""
			It is relatively safe to lead a low spade if:
			The queen is not in the deck and is not my lowest spade,
			or I have neither of the top two spades,
			or I have at least two low spades as protection.
			"""
			spades_list = filter(f_spades, self.hand)
			if not len(spades_list): return False
			spades_list.sort(s_rank)
			if spades_list[0][1] == queen: return False
			if not (spades, queen) in self.deck: return True
			top2list = filter(f_top_two, spades_list)
			if not len(top2list): return True
			if self.num_out(spades) == 1: return True
                        top3list = filter(f_top_three, spades_list)
			if len(spades_list) > len(top3list) +1: return True
			return False

		def heart_problem():
			"""
			Hearts are not a problem if
			  I have no hearts
			  I have more low hearts than high hearts
        	          and at least one lowest heart
			"""
			hearts_list = filter(f_hearts, self.hand)
			if not len(hearts_list): return False
			low_list = filter(f_low, hearts_list)
			high_list = filter(f_high, hearts_list)
			if len(high_list) > len(low_list): return True
			low_list.sort(s_rank)
			if len(low_list) and len(self.out_hearts) \
                           and low_list[0][1] > self.out_hearts[0][1]: return True
			return False

		def exit_problem():
			"""
			Returns true if there are no exits and no low cards
			"""
			win, exit, beat, above, below, high, low = 0, 0, 0, 0, 0, 0, 0
			for suit in range(4):
				high = high + len(list_high(suit))
				low = low + len(list_low(suit))
			for card in self.hand:
				above = above + self.num_above(card)
				below = below + self.num_below(card)
				if not self.num_above(card):
					win = win + 1
				elif self.num_above(card) and not self.num_below(card):
					exit = exit + 1
				elif self.num_above(card):
					beat = beat + 1
				win, exit, beat, above, below, high, low
			if not exit and not low: return True
			return False

		def already_played():
			"""Return true if hand with Queen has already played"""
			if (spades,queen) in self.pass_cards \
                                        and self.pass_dir + self.trick.num_played >= 3 \
                                        and not (spades, queen) in self.trick.card:
				return True
			return False

# Play card routines for trying to shoot
		def open_trick_shoot():
			valid_cards = filter(self.f_valid, self.hand)
			runnable_suits = []
			win_suits = []
			entry_suits = []
			noentry_suits = []
			void_suits = []
			low_suit = None
			low_length = 0
			high_suit = None
			high_length = 0
			discards = 0
			high_out = 0
			points = len(filter(f_point_cards, self.deck))

			# If hearts are ready to run, do so
			suit_list = list_suit(valid_cards, hearts)
			if len(suit_list):
				if self.is_runnable(hearts):
					return_card = low_win(hearts)
					if return_card != None:
						return return_card
				if self.is_duckable(hearts):
					suit_list.sort(s_rank, reverse=True)
					return suit_list[0]
			# Categorize suits as runnable, win, noentry, or void
			for suit in range(4):
				if suit == hearts: continue
				suit_list = list_suit(valid_cards, suit)
				length = len(suit_list);
				if length:
					suit_list.sort(s_rank, reverse=True)
					if self.is_runnable(suit):
						runnable_suits.append((suit, length))
						discards = discards + self.num_discards(suit)
					elif is_winner(suit_list[0]):
						win_suits.append((suit, length))
						high_out = high_out + self.num_above(suit_list[0])
					elif self.entry(suit_list):
						entry_suits.append((suit, length))
						high_out = high_out + self.num_above(suit_list[0])
					else:   noentry_suits.append((suit, length))	
					if length > low_length:
						low_suit = suit
						low_length = length
					if not self.num_above(suit_list[0]):
						if length > high_length:
							high_suit = suit
							high_length = length
					else: points += self.num_above(suit_list[0])
				else: void_suits.append((suit, length))

			# If we can generate enought discards, play high from runnable suit
			
			if len(runnable_suits):
				if discards >= points:
					# Run longest suit first, and minors before majors
					runnable_suits.sort(s_rank, reverse=True)
					runnable_suits.sort(s_suit)
					suit_list = list_suit(valid_cards, runnable_suits[0][0])
					suit_list.sort(s_rank, reverse=True)
					return_card = low_win(runnable_suits[0][0])
					if return_card != None:
						return return_card

			# Play low card from suit with entry, but no winner
			if len(entry_suits):
				# Try to set up our longest suit first
				entry_suits.sort(s_rank, reverse=True)
				for entry in entry_suits:
					suit = entry[0]
					if not self.num_players_have(suit) == 3: continue
					if not len(list_suit(self.deck, suit)) > 3: continue
					suit_list = list_suit(valid_cards, suit)
					suit_list.sort(s_rank)
					if suit_list[0] != (spades, queen):
						return suit_list[0]

			# Play low card from suit with no entry
			if len(noentry_suits):
				# Try to void our shortest suit first
				noentry_suits.sort(s_rank)
				for entry in noentry_suits:
					suit = entry[0]
					if not self.num_players_have(suit) == 3: continue
					if not len(list_suit(self.deck, suit)) > 3: continue
					suit_list = list_suit(valid_cards, suit)
					suit_list.sort(s_rank)
					if suit_list[0] == (spades, queen): continue
					return suit_list[0]

			# Play high from runnable suit regardless of number of discards
			if len(runnable_suits):
				# Run longest suit first
				runnable_suits.sort(s_rank, reverse=True)
				for entry in runnable_suits:
					suit_list = list_suit(valid_cards, runnable_suits[0][0])
					if suit == spades and len(runnable_suits) > 1: continue
					suit_list.sort(s_rank, reverse=True)
					return_card = low_win(runnable_suits[0][0])
					if return_card != None:
						return return_card

			# Play winner from longest valid suit which has one
			if high_suit != None:
				suit_list = list_suit(valid_cards, high_suit)	
				suit_list.sort(s_rank, reverse=True)
				return choice(list_peers(suit_list[0]))

			# Play winning heart, if possible
			if self.hearts_played:
				suit_list = list_suit(valid_cards, hearts)
				if len(suit_list):
					suit_list.sort(s_rank, reverse=True)
					if not self.num_above(suit_list[0]):
						return low_win(hearts)
			

			# Play low card from longest suit
			elif low_suit != None and self.num_players_have(low_suit) == 3:
				suit_list = list_suit(valid_cards, low_suit)	
				suit_list.sort(s_rank)
				return suit_list[0]

			# Play lowest valid card				
			valid_cards.sort(s_rank)
			return valid_cards[0]

		def follow_suit_shoot():
			if shoot_code == 7 and (spades, queen) in self.hand:
				# See if I can dump the queen
				if (spades, king) in self.trick.card \
                                or (spades, ace_high) in self.trick.card:
					return (spades, queen)
			valid_cards = filter(self.f_valid, self.hand)
			valid_cards.sort(s_rank)
			high_card = self.trick.get_highest_card()
			must_take, try_take = False, False
			point_cards = filter(f_point_cards,self.trick.card)
			play_card = None
			# Special case for 1st trick, always safe to duck trick
			if self.trick_num == 1 and self.rules.no_blood:
				return valid_cards[0]
			# Check to see if any point cards have already fallen
			if len(point_cards): must_take = True
			# Check to see if we are ready to run suits
			if self.hearts_played and self.is_runnable(hearts): try_take = True
			if not try_take:
				num_runnable = 0
				discards = 0
				points = len(filter(f_point_cards, self.deck))
				for suit in range(4):
					if suit == hearts: continue
					suit_list = list_suit(valid_cards, suit)
					length = len(suit_list);
					if length:
						suit_list.sort(s_rank, reverse=True)
						if self.is_runnable(suit):
							num_runnable = num_runnable + 1
							discards = discards + self.num_discards(suit)
				if discards >= points and num_runnable:	try_take = True			
			# We want this trick
			if must_take or try_take:
				# If in favorable position, play lowest card which will take trick
				if last_to_play() or (not must_take and self.trick.num_played == 2):
					for card in valid_cards:
						if card[1] > high_card[1]:
							if card == (spades, queen)  \
                                                          and ((spades, king) in self.hand \
                                                            or (spades, ace_high) in self.hand):
								continue
							return card
				# Try to win the trick from unfavorable position
				play_card = low_win(high_card)
				if play_card != None: return play_card
				if not must_take:
					# Try to take trick with highest card
					if valid_cards[-1][1] > high_card[1]:
						return valid_cards[-1]
				# Can't win, so abandon shoot.
				elif (spades, queen) in valid_cards: return (spades, queen)
				# Play highest card
				else: return valid_cards[-1]
					
			# We don't want this trick
			if (spades, queen) in valid_cards and len(valid_cards) > 1:
				valid_cards.remove((spades, queen))
			return valid_cards[0]				

		def dont_follow_suit_shoot():
			# Play lowest non-point card in shortest suit
			valid_cards = filter(self.f_valid, self.hand)
			low_suit = None
			low_length = 14
			for suit in range(4):
				if suit == hearts: continue
				suit_list = list_suit(valid_cards, suit)
				length = len(suit_list);
				if length:
					if length < low_length:
						low_suit = suit
						low_length = length
			if low_suit != None:
				suit_list = list_suit(valid_cards, low_suit)	
				suit_list.sort(s_rank)
				return suit_list[0]
			# Only hearts left
			valid_cards.sort(s_rank, reverse=True)
			return valid_cards[0]

		def duck_high(card):
			"""
			Returns the highest card from the current hand
			which is less than the specified card,
			and of the same suit. If Omnibus ruleset,
			don't return the bonus card.
			"""
			suit_list = list_suit(self.hand, card[0])
			if not len(suit_list): return None
			low_list = [item for item in suit_list if item[1] < card[1]]
			if len(low_list):		
				low_list.sort(s_rank, reverse=True)
				if self.bonus_card != None and self.bonus_card == low_list[0] \
				   and len(low_list) > 1:
					return low_list[1]
				return low_list[0]
			return None

		def low_win(suit):
			"""
			Returns the lowest card of the specified suit
			from the current hand which is higher than
			the highest outstanding card of that suit,
			or None
			"""
			suit_list = list_suit(self.hand, suit)
			if not len(suit_list): return None
			if (spades, queen) in suit_list and len(suit_list) > 1:
				suit_list.remove((spades, queen))
			suit_list.sort(s_rank)
			deck_list = list_suit(self.deck, suit)
			if not len(deck_list): return suit_list[0]
			deck_list.sort(s_rank, reverse=True)
			low_list = [item for item in suit_list if item[1] > deck_list[0][1]]
			if not len(low_list): return None
			low_list.sort(s_rank)
			return low_list[0]

		def bracket(card):
			"""
			Returns a two element list containing the next highest,
			and next lowest, deck cards to the specified card.
			"""
			deck_list = list_suit(self.deck, card[0])
			if not len(deck_list): return [None, None]
			high = None
			low = None
			deck_list.sort(s_rank)
			for item in deck_list:
				if item[1] > card[1]:
					high = item
					break
			deck_list.sort(s_rank, reverse=True)
			for item in deck_list:
				if item[1] < card[1]:
					low = item
					break
			return [high, low]

		def list_peers(card):
			"""
			Returns a list of cards from the current hand
			which are of the same effective rank as the
			the specified card. (The card itself is a member
			of the list, if it is in the current hand.)
			"""
			if card == (spades, queen): return [card]
			if self.bonus_card != None and card == self.bonus_card: return [card]
			suit_list = list_suit(self.hand, card[0])
			if not len(suit_list): return []
			bracket_list = bracket(card)
			high = 15
			low = 0
			if bracket_list[0] != None: high = bracket_list[0][1]
			if bracket_list[1] != None: low = bracket_list[1][1]
			peer_list = []
			for item in suit_list:
				if item[1] > low and item[1] < high and item != (spades, queen) \
				   and not (self.bonus_card != None and item == self.bonus_card):
					peer_list.append(item)
			return peer_list

# Play Card Entry               
		self.trick_num = 14 - len(self.hand)
		# If first trick of round
                if self.trick_num == 1:
			# Set bonus card for Omnibus ruleset
			if self.rules.ruleset == 'omnibus': self.bonus_card = (diamonds, jack)
			elif self.rules.ruleset == 'omnibus_alt': self.bonus_card = (diamonds, ten)
			else: self.bonus_card = None
			# Reset round variables
			self.hearts_played = False
			self.queen_played = False
	                self.shooting = False
	                self.hearts_split = False
			self.can_shoot = True
			self.void_counts = []
	                # Remove my hand from deck
			self.deck = deal()
                        for card in self.hand:
                            self.deck.remove(card)
                        self.out_clubs = filter(f_clubs, self.deck)
                        self.out_diamonds = filter(f_diamonds, self.deck)
                        self.out_hearts = filter(f_hearts, self.deck)
                        self.out_spades = filter(f_spades, self.deck)
                        self.suit_counts = [len(self.out_clubs), len(self.out_diamonds), \
                            len(self.out_hearts), len(self.out_spades)]

		# Check for shooting
		self.shooting = False
		shoot_code = try_to_shoot()
		if shoot_code: self.shooting = True
		score_list = []
		for index in range(4):
			if self.score.round[index] and index != self.direction:
				score_list.append(self.score.round[index])
		if len(score_list):
			self.can_shoot = False
			self.shooting = False
		if len (score_list) > 1 or self.score.round[self.direction]: self.hearts_split = True
                # invoke action routine
		valid_cards = filter(self.f_valid, self.hand)
                if len(valid_cards) == 1:
			 return valid_cards[0]
                # Routines for shooting
		if self.shooting:
			if self.trick.num_played == 0:
				return open_trick_shoot()
			elif have_suit(self.hand, self.trick.trump):
				return follow_suit_shoot()
			else:
				return dont_follow_suit_shoot()
		# Routines for not shooting
		if self.trick.num_played == 0:
			return open_trick()
		elif have_suit(self.hand, self.trick.trump):
			return follow_suit()
		else:
			return dont_follow_suit()
	
	def trick_end(self):
		"""update card lists and status flags"""
                # remove played cards from global lists
                for card in self.trick.card:
                    if card in self.deck:
			self.deck.remove(card)
		    if card in self.pass_cards:
			self.pass_cards.remove(card)
		    if card in self.received_cards:
			self.received_cards.remove(card)
                self.out_clubs = filter(f_clubs, self.deck)
                self.out_diamonds = filter(f_diamonds, self.deck)
                self.out_hearts = filter(f_hearts, self.deck)
                self.out_spades = filter(f_spades, self.deck)
		# Update global variables
                self.suit_counts = [len(self.out_clubs), len(self.out_diamonds), \
                            len(self.out_hearts), len(self.out_spades)]
		for index in range(4):
			card = self.trick.card[index]
			if (self.trick.trump, index) not in self.void_counts:
				if card[0] != self.trick.trump:
					self.void_counts.append((self.trick.trump, index),)
		if have_suit(self.trick.card, hearts):
			self.hearts_played = True
		if (spades, queen) in self.trick.card:
			self.queen_played = True
	
	def round_end(self):
		"""Reset pass globals"""
                self.pass_dir = keep
		self.received_cards = []

