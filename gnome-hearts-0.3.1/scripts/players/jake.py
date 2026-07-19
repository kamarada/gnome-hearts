# Hearts - jake.py
# Copyright 2008 Jesse F. Hughens and Sander Marechal
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

# This is a reasonably good player written by Jesse Hughes, adapted
# from the stock_ai included in gnome_hearts 0.1.3.  This player has
# perfect recall of what has been played (which isn't exactly fair), but
# he's not the cleverest lad around.  After all, he was written by a
# piss-poor hearts player.

# Jake is originally designed and written by Jesse Hughes in Lua for the
# 0.1.3 branch of gnome-hearts. It was ported to Python by Sander Marechal

from definitions import *
from player import Player
from player_api import *
from random import choice

class PlayerAI_Jake(Player):
	def __init__(self, direction, trick, score, rules):
		Player.__init__(self, direction, trick, score, rules)
		self.name = "Jake" # Alternative names: "Jesse" and "Quincy"

		# The following array keeps track of bad suits: a suit that some
		# other player doesn't have.  These suits can be dangerous to take.
		# list of tuples (suit, player)
		self.player_out_suits = []
		self.seen_cards = []

	def select_card(self, card, result):
		""" remove card from hand and add it to result
		"""
		if card in self.hand:
			result.append(card)
			self.hand.remove(card)
	
	def card_string(self, card):
		suit, rank = None, None
		
		if card[0] == clubs:
			suit = "clubs"
		elif card[0] == diamonds:
			suit = "diamonds"
		elif card[0] == hearts:
			suit = "hearts"
		elif card[0] == spades:
			suit = "spades"
		
		if card[1] == ace or card[1] == ace_high:
			rank = "ace"
		elif card[1] == king:
			rank = "king"
		elif card[1] == queen:
			rank = "queen"
		elif card[1] == jack:
			rank = "jack"
		else:
			rank = card[1]
		
		if suit == None or rank == None:
			return "??"
		
		return "%s of %s" % (suit, rank)
	
	def print_card_list(self, list):
		for card in list:
			print self.card_string(card)
	
	def record_played_cards(self):
		""" Add all the cards played thus far to the list seen_cards
		"""
		
		# record my own cards!
		if len(self.seen_cards) == 0:
			self.seen_cards.extend(self.hand)
		
		for card in self.trick.card:
			if card != None and card not in self.seen_cards:
				self.seen_cards.append(card)
	
	def is_giveaway_card(self, card):
		""" returns true if the only unseen cards of same suit beat this card
		"""
		if len([x for x in self.seen_cards if x[1] == card[1]]) == 13:
			return False
		
		for i in range(2, card[1]):
			if (card[1], i) not in self.seen_cards:
				return False
		
		return True
	
	def is_scoring_suit(self, suit):
		"""
		returns true if the suit still has some scoring cards unseen,
		i.e., if the suit is either hearts or spades with an unplayed Queen.
		"""
		
		if suit == hearts:
			return True
		
		if suit == spades and ((spades, queen) not in self.seen_cards or (spades, queen) in self.hand):
			return True
		
		return False
	
	def num_unseen(self, suit):
		""" returns number of cards not accounted for
		"""
		unseen = 13 - len([x for x in self.seen_cards if x[0] == suit])
		# print "%d unseen for suit %s" % (unseen, suit)
		return unseen
	
	def num_players_out(self, suit):
		"""
		returns number of players out of a suit (some player doesn't have it) 
		Note: includes the player himself in this count, but that should be
		harmless.
		"""
		return len([x for x in self.player_out_suits if x[0] == suit])
	
	def get_dull_suit_cards(self, list, include_bonus = True):
		""" return all clubs and diamonds
		"""
		return [x for x in list if x[0] == clubs or x[0] == diamonds]
	
	def dump_cards_from_list(self, list, result):
		"""
		list is a subset of our hand that we'd like to get rid of. Put the
		highest cards from list into the result and remove them from list and
		hand.
		"""
		list.sort(s_rank, reverse=True)
		
		while len(result) < 3 and len(list) > 0:
			self.select_card(list.pop(0), result)
	
	def select_cards(self, direction):
		"""
		This function is called when you have to select three cards to pass to the
		next player. Return a list of three cards.
		
		- If I have ace or king of spades, get rid of it.
		- If I have fewer than four spades, get rid of the queen.
		- If my lowest heart is greater than 6, get rid of every heart over 10.
		- If I have fewer than three diamonds, get rid of as many as possible.
		- If I have fewer than four clubs, get rid of as many as possible.
		- Get rid of the highest diamonds/clubs.
		"""
		# self.print_card_list(self.hand)
		
		result = []
		
		clubs_list = filter(f_clubs, self.hand)
		diamonds_list = filter(f_diamonds, self.hand)
		hearts_list = filter(f_hearts, self.hand)
		spades_list = filter(f_spades, self.hand)
		
		# first pass on the high spades
		if (spades, ace_high) in spades_list:
			self.select_card((spades, ace_high), result)
		if (spades, king) in spades_list:
			self.select_card((spades, king), result)
		if (spades, queen) in spades_list and len(spades_list) < 4:
			self.select_card((spades, queen), result)
		
		# if our lowest heart is above six, get rid of all heart face cards.
		if len(hearts_list) > 0:
			hearts_list.sort(s_rank)
			
			if hearts_list[0][1] > 6:
				faces = [x for x in hearts_list if x[1] > 10]
				
				while len(result) < 3 and len(faces) > 0:
					self.select_card(faces.pop(0), result)
		
		# Try to clear diamonds and clubs
		if len(clubs_list) < len(diamonds_list):
			if len(clubs_list) > 0 and len(clubs_list) < 4:
				self.dump_cards_from_list(clubs_list, result)
			if len(diamonds_list) > 0 and len(diamonds_list) < 4:
				self.dump_cards_from_list(diamonds_list, result)
		else:
			if len(diamonds_list) > 0 and len(diamonds_list) < 4:
				self.dump_cards_from_list(diamonds_list, result)
			if len(clubs_list) > 0 and len(clubs_list) < 4:
				self.dump_cards_from_list(clubs_list, result)
		
		# dump dull cards
		self.dump_cards_from_list(self.get_dull_suit_cards(self.hand), result)
		
		# I shouldn't need to dump any more hearts or spades, but
		# it's always possible that I was dealt only these two suits!
		# PS: I think that the original Lua code had a bug here. It tried to
		# dump more cards from the dull list
		self.dump_cards_from_list(hearts_list, result)
		self.dump_cards_from_list(spades_list, result)
		
		# print "Passing:"
		# self.print_card_list(result)
		# print "----"
		
		return result
	
	def s_len(self, a, b):
		""" Sort a multidimensional array by array length
		"""
		return len(a) - len(b)
	
	def unseen_above(self, card):
		""" Return the number of unseen cards that beat this card
		"""
		suit_seen = [x for x in self.seen_cards if x[0] == card[0] and x[1] > card[1]]
		count = 14 - card[1] - len(suit_seen)
		
		return count
	
	def spades_is_iffy(self):
		""" Spades are iffy if I have the queen or a card higher than the queen
		"""
		iffy_spades = [x for x in self.hand if x[0] == spades and x[1] >= queen]
		return len(iffy_spades) > 0
	
	def choose_lead_card(self):
		"""
		call a card a giveaway card if it is lower than any card in the
		suit not yaet seen and someone has a card in the suit not yet
		seen.  If we lead with a giveaway card, someone else will take
		the trick.
		
		If I have the ace or king of a non-dangerous suit, then play it.
		
		If I do not have anything queen or above of spades and if spades
		are not bad, then play the highest spade below the queen.
		
		Play a giveaway heart.
		
		Even if spades are bad, play a low spade provided I have nothing
		above Jack in my hand.
		
		Play a giveaway card in any suit.  Choose the suit with the most
		folks out of it.
		
		Pick the card that has the most trump cards above it unseen.
		(We may as well restrict ourselves to the lowest card of each
		suit.)
		"""
		
		# If I have an ace or king of a non-dangerous suit and there are
		# at least 8 unplayed cards of that suit, play it.
		valid_cards = filter(self.f_valid, self.hand)
		cards = [[], [], [], []]
		
		# print "Player %d picking from" % self.direction
		# self.print_card_list(valid_cards)
		
		for i in range(4):
			cards[i] = [x for x in valid_cards if x[0] == i]
		cards.sort(self.s_len, reverse=True)
		
		for list in cards:
			if len(list) == 0:
				continue
			
			list.sort(s_rank, reverse=True)
			card = list[0]
			if (card[1] > queen
				and not self.is_scoring_suit(card[0])
				and self.num_players_out(card[0]) == 0
				and self.num_unseen(card[0]) > 5):
				# print "Seems safe to lead with %s" % card
				return card
		
		# If I do not have anything queen or above of spades and if no one
		# is out of spades, then play the highest spade below the queen.
		if have_suit(valid_cards, spades) and self.num_players_out(spades) == 0 and (spades, queen) not in self.seen_cards:
			spades_list = filter(f_spades, valid_cards)
			spades_list.sort(s_rank,reverse=True)
			high_spade = spades_list[0]
			if high_spade[1] < queen:
				# print "Cough out a high spade: %s" % high_spade
				return high_spade
		
		# Play a giveaway heart
		hearts_list = filter(f_hearts, valid_cards)
		if len(hearts_list) > 0:
			hearts_list.sort(s_rank)
			low_heart = hearts_list[0]
			if self.is_giveaway_card(low_heart):
				# print "Giveaway: %s" % low_heart
				return low_heart
		
		# Even if spades are bad, play a low spade provided I
		# have nothing above Jack in my hand and the Queen is
		# still out.
		
		if have_suit(valid_cards, spades) and (spades, queen) not in self.seen_cards:
			spades_list = filter(f_spades, valid_cards)
			spades_list.sort(s_rank, reverse=True)
			if spades_list[0][1] < queen:
				spades_list.sort(s_rank)
				low_spade = spades_list[0]
				# print "Cough up a low spade: %s" % low_spade
				return low_spade
		
		# Play a giveaway card in any suit.  Choose the suit with the most
		# folks out of it.
		for list in cards:
			if len(list) == 0:
				continue
			
			list.sort(s_rank)
			if self.is_giveaway_card(list[0]) and (list[0][0] != spades or list[-1][1] < queen):
				# print "Giveaway card: %s" % list[0]
				return list[0]
		
		# Pick the card that has the most trump cards above it unseen.
		# (We may as well restrict ourselves to the lowest card of each
		# suit.)
		best_suit = []
		count = 0
		
		for challenger in cards:
			if len(challenger) > 0 and (challenger[0][0] != spades or not self.spades_is_iffy()):
				# If we have the Queen or above in Spades, then it's not the best bet, unless
				# either there is no best_suit or the best_suit has count of 0
				challenger.sort(s_rank)
				if len(best_suit) == 0:
					best_suit = challenger
					count = self.unseen_above(best_suit[0])
					# print "Default best card %s count %d" % (self.card_string(best_suit[0]), count)
				else:
					c_count = self.unseen_above(challenger[0])
					# print "%d unseen cards above %s" % (c_count, self.card_string(challenger[0]))
					
					if c_count > count:
						best_suit = challenger
						count = c_count
		
		if len(best_suit) > 0:
			# try a non-points spade
			if count == 0:
				for challenger in cards:
					if len(challenger) == 0:
						continue
					
					if challenger[0][0] == spades:
						pointless = filter(f_pointless_cards, challenger)
						pointless.sort(s_rank)
						if len(pointless) > 0 and self.unseen_above(pointless[0]) > 0:
							# print "Might as well go with a spade: %s" % pointless[0]
							return pointless[0]
			
			# print "Best bet: %s" % best_suit[0]
			return best_suit[0]
		else:
			valid_cards.sort(s_rank)
			# print "Scraping: %s" % valid_cards[0]
			return valid_cards[0]
	
	
	def avoid_trick(self, valid_cards, high_card):
		# lifted from stock_ai.
		# play the higest card that doesn't take the trick
		valid_cards.sort(s_rank, reverse=True)
		for card in valid_cards:
			if card[0] != high_card[0] or card[1] < high_card[1]:
				return card
		
		# we can't dodge, so take it with the fewest points.
		# If we're the last player, use a high card.  Otherwise use a low
		# card and hope that someone else gets it.
		if self.trick.num_played == 3:
			valid_cards.sort(s_rank, reverse=True)
		else:
			valid_cards.sort(s_rank)
		
		# Don't give myself the queen of spades
		if valid_cards[0] == (spades, queen) and len(valid_cards) > 1:
			return valid_cards[1]
		
		return valid_cards[0]
	
	def take_trick(self, valid_cards, high_card):
		# if someone else will take the Queen, play it!
		# Getting rid of the Queen is important.
		if (spades, queen) in valid_cards and queen < high_card[1]:
			return (spades, queen)
		
		# Play the highest card that's no a point
		pointless_cards = filter(f_pointless_cards, valid_cards)
		if len(pointless_cards):
			pointless_cards.sort(s_rank, reverse=True)
			
			# Try not to trump the queen of spades
			if high_card[0] == spades and (spades, queen) not in self.seen_cards:
				for card in pointless_cards:
					if card[1] < queen:
						return card
			
			return pointless_cards[0]
		
		# Have to play a point. Go low
		valid_cards.sort(s_rank)
		return valid_cards[0]
	
	def dump_cards(self, valid_cards, high_card):
		# We don't have the suit at all.  First, try to dump high spades.
		if (spades, queen) in valid_cards:
			return (spades, queen)
		if (spades, ace_high) in valid_cards and self.is_scoring_suit(spades):
			return (spades, ace_high)
		if (spades, king) in valid_cards and self.is_scoring_suit(spades):
			return (spades, king)
		
		# Dump high cards (above queen), any suit.
		valid_cards.sort(s_rank, reverse=True)
		if valid_cards[0][1] > jack:
			return valid_cards[0]
		
		# Dump the highest point card we have.
		point_cards = filter(f_point_cards, valid_cards)
		if len(point_cards):
			point_cards.sort(s_rank, reverse=True)
			return point_cards[0]
		
		# Dump any card
		return valid_cards[0]
	
	def choose_final_card(self):
		"""
		Called when we are the fourth player on the trick.
		
		Have the suit:
		- If there are no points in the trick, take it with the highest card we have.
		- If there are points in the trick, play the highest card that won't take it.  
		- If we are forced to take it, take it with the highest card we have.
		Not have the suit:
		- Play the Queen of Spades.
		- Play the King or Ace of Spades
		- Play the highest Queen or above card we have.
		- Play the highest heart.
		- Play the highest card we have.
		"""
		valid_cards = filter(self.f_valid, self.hand)
		high_card = self.trick.get_highest_card()
		
		# print "---"
		# print "Player %d picking final card from" % self.direction
		# self.print_card_list(valid_cards)
		
		if have_suit(valid_cards, high_card[0]):
			if len(filter(f_point_cards, self.trick.card)) > 0:
				# print "I should avoid it"
				return self.avoid_trick(valid_cards, high_card)
			
			# print "I should take it"
			return self.take_trick(valid_cards, high_card)
		
		return self.dump_cards(valid_cards, high_card)
	
	def is_dangerous_trick(self, high_card):
		"""
		return true if one of the remaining players doesn't have the suit
		of the trick and either (has hearts or queen of spades is not played)
		"""
		
		if self.num_unseen(high_card[0]) + self.trick.num_played < 6:
			# print "Not enough cards! Dangerous!"
			return True
		
		for index in range(4):
			card = self.trick.card[index]
			if (card is None
			    and (self.trick.trump, index) in self.player_out_suits
			    and ((hearts, index) not in self.player_out_suits
				 or ((spades, queen) not in self.seen_cards
				     and (spades,index) not in self.player_out_suits))):
				# print "Upcoming player is dangerous!"
				return True
		
		return False
	
	def choose_mid_card(self):
		"""
		Have the suit:
		- If the suit is not dangerous and has at least 7 cards in other folks hands, 
		  play the highest card we have.
		- Else, play the highest card that won't take the trick.
		Not have the suit:
		- Play the Queen of Spades.
		- Play the highest Queen or above card we have.
		- Play the highest heart.
		
		- If the suit is not dangerous and has at least 7 cards in other folks hands, 
		  play the highest card we have.
		"""
		valid_cards = filter(self.f_valid, self.hand)
		high_card = self.trick.get_highest_card()
		
		# print "---"
		# print "Player %d picking middle card from" % self.direction
		# self.print_card_list(valid_cards)
		
		if have_suit(valid_cards, high_card[0]):
			if len(filter(f_point_cards, self.trick.card)) > 0 or self.is_dangerous_trick(high_card):
				# print "I should avoid it"
				return self.avoid_trick(valid_cards, high_card)
			
			# print "I should take it"
			return self.take_trick(valid_cards, high_card)
		
		return self.dump_cards(valid_cards, high_card)
	
	def play_card(self):
		"""
		LEADING:
		
		Call a suit bad if I know that one player is out of that suit.
		
		Call a suit dangerous if either it contains an unseen scoring
		card (i.e., spades before the queen has been seen or hearts anytime) or
		it is bad.
		
		If I have the ace or king of a non-dangerous suit, then play it.
		
		If I do not have anything queen or above of spades and if spades
		are not bad, then play the highest spade below the queen.
		
		If I have a heart that I know will not take the trick, play it
		(if possible).  (Play the highest heart that won't take the trick).
		
		Even if spades are bad, play a low spade provided I have nothing
		above Jack in my hand.
		
		Play the highest diamond/club that will not take the trick.
		
		FOLLOWING:
		
		Not fourth:
			Have the suit:
				If the suit is not dangerous and has at least 7 cards in other folks hands, 
				play the highest card we have.
				Else, play the highest card that won't take the trick.
			Not have the suit:
				Play the Queen of Spades.
				Play the highest Queen or above card we have.
				Play the highest heart.
		Fourth:
			Have the suit:
				If there are no points in the trick, take it with the highest card we have.
				If there are points in the trick, play the highest card that won't take it.  
				If we are forced to take it, take it with the highest card we have.
			Not have the suit:
				As above.
		"""
		self.record_played_cards()
		
		if self.trick.num_played == 0:
			return self.choose_lead_card()
		
		if self.trick.num_played == 3:
			return self.choose_final_card()
		
		return self.choose_mid_card()
	
	def trick_end(self):
		for index in range(4):
			card = self.trick.card[index]
			if (self.trick.trump, index) not in self.player_out_suits:
				if card[0] != self.trick.trump:
					self.player_out_suits.append((self.trick.trump, index),)
		
		self.record_played_cards()
	
	def round_end(self):
		self.player_out_suits = []
		self.seen_cards = []

