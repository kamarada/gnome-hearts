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
from pprint import pprint

class PlayerAI_Ling(Player):
	def __init__(self, direction, trick, score, rules):
		# Alternative names: "Mikhi" and "Bruno"
		Player.__init__(self, direction, trick, score, rules)
		self.name = "Ling"

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
		
		return "%s of %s" % (rank, suit)
	
	def print_card_list(self, list):
		for card in list:
			print self.card_string(card)

	def record_played_cards(self):
		"""
		Add all the cards played thus far to the list seen_cards
		"""
		
		# record my own cards!
		if len(self.seen_cards) == 0:
			self.seen_cards.extend(self.hand)
		
		for card in self.trick.card:
			if card != None and card not in self.seen_cards:
				self.seen_cards.append(card)

	def num_above(self, card, card_list):
		"""
		return number of cards in card_list above card (same suit)
		"""

		return len([x for x in card_list if x[0] == card[0] and x[1] > card[1]])

	def num_below(self, card, card_list):
		"""
		return number of cards in card_list below card (same suit)
		"""

		return len([x for x in card_list if x[0] == card[0] and x[1] < card[1]])

	def is_giveaway_card(self, card):
		"""
		returns true if the only unseen cards of same suit beat this card
		"""

		return (self.unseen_below(card) == 0 and
			self.unseen_above(card) > 0)

	def is_played(self,card):
		return card not in self.hand and card in self.seen_cards
	
	def is_probable_giveaway_card(self, card):
		"""
		returns true if the number of unseen cards of same
		suit below card is fewer than the number of players
		that presumably have the suit.  Of course, we require
		at least one player above this card!
		"""
		if (3 - self.num_players_out(card[0]) > self.unseen_below(card)
		    and self.unseen_above(card) > 0):
			return True
		return False
		


	def is_scoring_suit(self, suit):
		"""
		returns true if the suit still has some scoring cards unseen,
		i.e., if the suit is either hearts or spades with an unplayed Queen.
		"""
		if suit == hearts:
			return True
		
		if suit == spades and not self.is_played((spades, queen)):
			return True
		
		return False
	
	def num_unseen(self, suit):
		"""
		returns number of cards in suit not accounted for
		"""
		return 13 - len([x for x in self.seen_cards if x[0] == suit])
	
	def num_players_out(self, suit):
		"""
		returns number of players out of a suit (some player
		doesn't have it) Note: includes the player himself in
		this count, but that should be harmless.
		"""
		return len([x for x in self.player_out_suits if x[0] == suit])

	def moon_shooter(self):
		"""
		returns true if the guy who is currently winning the
		trick has scored more than 14 pts. this hand and no
		one else has scored a single pt.  If so, then we need
		to change strategy so that he can't shoot the moon.
		"""

		scorers=[x for x in range(4) if self.score.round[x] > 0]
		first_played=self.trick.card[self.trick.first_played]
		# A list of all the non-zero scorers. If there's only
		# one, then he might be shooting the moon.
		
		if first_played == None:
			return False
		
		if len(scorers) > 1:
			return False

		# If he is dropping a high spade as the only scorer,
		# then he's pretty suspicious!
				
		if (first_played[0] == spades
		    and first_played[1] > jack
		    and (not self.is_played((spades,queen))
			 or (spades,queen) == first_played)):
			return True
		
		if (first_played[0] == hearts
		    and first_played[1] > 10):
			return True

		if len(scorers) == 1:
			scorer=scorers[0]
			
			# If the only guy with points isn't currently
			# taking the trick, then we won't worry.
			# NOTE: He may not have played yet, but if
			# not, then he is not in control, so we won't
			# worry.
			
			if self.trick.card[scorer] == self.trick.get_highest_card():
			
				# Let's assume moon_shooter if he has more
				# than 14 points so far or if he has more than
				# 6 points and the queen hasn't shown up yet.

				# He's taken the queen and at least two other hearts.
				if self.score.round[scorer] > 14:
					return True

				# He's taken more than six hearts
			
				if (self.score.round[scorer] > 6 and
				    (not self.is_played((spades, queen))
				     or (spades,queen) in self.trick.card)):
					return True

				# If he's led with the highest unseen
				# card of a suit that someone is out
				# of.  This leads to some false
				# positives (Luis is stoopid!), so
				# let's restrict it to the case in
				# which he's already taken at least
				# two points.
				
				his_card=self.trick.card[scorer]

				if (self.unseen_above(his_card) == 0
				    and self.num_players_out(his_card[0]) > 0
				    and self.score.round[scorer] > 1):
					
					# If we can take the trick,
					# then he wouldn't know that,
					# so let's not count it as a
					# moon shooter in that case.
					if (self.num_players_out(his_card[0]) == 1
					    and len([x for x in filter(self.f_valid, self.hand) if x[0] == his_card[0]]) > 0):
						return False
					return True
				
				return False
		return False
			
	def moon_defense(self):
		"""
		Someone is threatening to shoot the moon.  We'll take
		it if we can and if we aren't currently the high
		score.  Otherwise, we will play the card with the
		fewest unseen cards less than it (any suit) in hopes
		that we may take a later trick. 
		"""
		high_card=self.trick.get_highest_card()
		valid_cards = filter(self.f_valid, self.hand)

		# Check to see if we are the highest score.  If so, to
		# heck with it.  Let someone else make the sacrifice.

		if (self.score.game[self.direction] != max(self.score.game)
		    or (self.score.game[self.direction] < min(self.score.game) + 10
			and self.score.game[self.direction] < 85)
		    or self.score.game[self.direction] < 26):

			if valid_cards[0][0] == high_card[0]:
				
				winning = [x for x in valid_cards if x[1] > high_card[1]]

				if len(winning) > 0:

					# We can take the trick.  If it is
					# dangerous, we should take it with
					# the lowest card that will do.
					# Otherwise, might as well take it
					# with the highest card that will do.
					if not self.is_dangerous_trick(high_card):
						winning.sort(s_rank, reverse=True)
						return self.choose_equiv(winning[0],winning)


					# winning contains a list of cards
					# that could take the trick.

					winning.sort(s_rank)

					# Play the lowest card that will take
					# the trick.
					return self.choose_equiv(winning[0],winning)
				
			
			# We can't take the trick.  Let's look at the lowest
			# card in each suit.  We'd like to get rid of the
			# card with the fewest unseen cards *below* it, so
			# that we keep our high cards in our hand.  We might
			# still need to take a trick.

			# Exception: If I have a single card from this suit
			# which has no unseen cards above it, then I can
			# throw out cards below that card.  After all, if he
			# ever plays that suit, I'll take it.
				
			low_cards=[]

			for fil in [f_diamonds, f_clubs, f_hearts, f_spades]:
				this_suit = filter(fil, valid_cards)
				if len(this_suit) > 0:
					
					# If one of our cards from
					# this suit has no unseen
					# cards above it, then get
					# rid of something equivalent
					# to the second highest card
					# of this suit.
					
					if (len(this_suit) > 1
					    and self.unseen_above(max(this_suit)) == 0):
						this_suit.sort(s_rank,reverse=True)
						return self.choose_equiv(this_suit[1],this_suit)

					low_cards.append(min(this_suit))
				
			best = low_cards.pop()

			while len(low_cards) > 0:
				candidate = low_cards.pop()
				if self.unseen_below(best) > self.unseen_below(candidate):
					best = candidate

			return self.choose_equiv(best,valid_cards)
		return None
				
	def get_dull_suit_cards(self, list, include_bonus = True):
		""" return all clubs and diamonds
		"""
		return [x for x in list if x[0] == clubs or x[0] == diamonds]
	
	def dump_cards_from_list(self, list, result):
		"""
		list is a subset of our hand that we'd like to get rid
		of. Put the highest cards from list into the result
		and remove them from list and hand.
		"""
		list.sort(s_rank, reverse=True)
		
		while len(result) < 3 and len(list) > 0:
			self.select_card(list.pop(0), result)
	
	def select_cards(self, direction):
		"""
		This function is called when you have to select three
		cards to pass to the next player. Return a list of
		three cards.
		
		- If I have ace or king of spades, get rid of it.

		- If I have fewer than four spades, get rid of the
		queen.

		- If my lowest heart is greater than 6, get rid of
		every heart over 10.

		- If I have fewer than three diamonds, get rid of as
		many as possible.

		- If I have fewer than four clubs, get rid of as many
		as possible.

		- Get rid of the highest diamonds/clubs.
		"""

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
		
		# if our lowest heart is above six, get rid of all
		# heart face cards.
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
		
		return result

	def same_suit_from_list(self,card,card_list):
		return [x for x in card_list if x[0] == card[0]]

	def s_dump_rank(self,a,b):
		"""
		We prefer to dump a if there are fewer cards beneath a
		such that unseen_above is > 0.
		"""
		valid_cards =  filter(self.f_valid, self.hand)
		return (len([x for x in self.same_suit_from_list(b,valid_cards) if self.unseen_above(x) > 0])
			- len([x for x in self.same_suit_from_list(a,valid_cards) if self.unseen_above(x) > 0]))
	
	def s_len(self, a, b):
		""" Sort a multidimensional array by array length
		"""
		return len(a) - len(b)

	def s_prob_give_pref(self, a, b):
		""" Sort a multidimensional array of cards by an ad
		hoc method.  Suits with only one card are lowest.  If
		two suits have more than one card, then we rank the
		suits as follows: check the number of unseen cards
		above the *second* member of the suit, the more the
		better.

		If spades are iffy, rank them higher than anything
		else.
		"""
		if a[0][0] == spades and self.spades_is_iffy():
			return -1

		if b[0][0] == spades and self.spades_is_iffy():
			return 1

		if len(a) == 1:
			return 1
		if len(b) == 1:
			return -1
		
		return self.unseen_above(a[1]) - self.unseen_above(b[1])
	
		
	def unseen_below(self,card):
		"""
		return the number of unseen cards that are below card.
		"""
		suit_seen = [x for x in self.same_suit_from_list(card,self.seen_cards) if x[1] < card[1]]
		return card[1] - 2 - len(suit_seen)
			
	def unseen_above(self, card):
		""" Return the number of unseen cards that beat this card
		"""
		suit_seen = [x for x in self.same_suit_from_list(card,self.seen_cards) if x[1] > card[1]]
		count = 14 - card[1] - len(suit_seen)
		
		return count
	
	def spades_is_iffy(self):
		"""
		Spades are iffy if I have the queen or a card higher
		than the queen
		"""
		return (not self.is_played(queen)
			and len([x for x in self.hand if x[0] == spades and x[1] > jack]) > 0)

	def will_take_trick(self,card):
		high = self.trick.get_highest_card()
		return (high != None
			and high[0] == card[0]
			and high[1] <= card[1])
		    
	def is_equiv(self,a,b):
		"""
		Two cards are equivalent if they have the same suit,
		the same unseen_above (and hence the same
		unseen_below) and either both of them or neither of
		them take the current trick.
		"""

		return (a[0] == b[0]
			and self.unseen_above(a) == self.unseen_above(b)
			and self.will_take_trick(a) == self.will_take_trick(b))
	
	def choose_equiv(self,card,card_list):
		"""
		Randomly select a card from list which has the same unseen_above score as card.
		"""

		return choice([x for x in card_list if self.is_equiv(x,card)])


	def s_unseen_above(self,a, b):
		return self.unseen_above(a) - self.unseen_above(b)

	def s_unseen_below(self,a, b):
		return self.unseen_below(a) - self.unseen_below(b)
		
	def choose_lead_card(self):
		"""
		call a card a giveaway card if it is lower than any
		card in the suit not yet seen and someone has a card
		in the suit not yet seen.  If we lead with a giveaway
		card, someone else will take the trick.
		
		If I have the ace or king of a non-dangerous suit,
		then play it.
		
		If I do not have anything queen or above of spades and
		if spades are not bad, then play the highest spade
		below the queen.
		
		Play a giveaway heart.
		
		Even if spades are bad, play a low spade provided I
		have nothing above Jack in my hand.
		
		Play a giveaway card in any suit.  Choose the suit
		with the most folks out of it.
		
		Pick the card that has the most trump cards above it
		unseen.  (We may as well restrict ourselves to the
		lowest card of each suit.)
		"""
		
		# If I have any cards with unseen_above of 0 and a
		# non-dangerous suit and there are at least 8 unplayed
		# cards of that suit, play it.

		# Example: If I have the J and K and the Q and A have
		# both been played, then both J and K qualify.  Play
		# one of them.
	
		valid_cards = filter(self.f_valid, self.hand)
		cards = [[], [], [], []]

		# If I have the Queen and there are no unseen spades
		# beneath it and at least one unseen spade above it,
		# play it!  What a giveaway!

		if ((spades,queen) in valid_cards
		    and self.unseen_below((spades,queen)) == 0
		    and self.unseen_above((spades,queen)) > 0):
			return (spades,queen)
		
		for i in range(4):
			cards[i] = [x for x in valid_cards if x[0] == i]
		cards = [x for x in cards if len(x) > 0]
		cards.sort(self.s_len, reverse=True)
		
		
		for list in cards:

			# Form a list of all those cards with 0 cards
			# unseen above.  Ace is always in this list
			# (if you have it).  King is in the list if
			# you've seen the Ace, and so on.
			
			high_cards = [x for x in list if self.unseen_above(x) == 0]

			if len(high_cards) == 0:
				continue

			# Randomly pick a card.  Don't always choose
			# the highest, since that gives too much
			# information.
			
			card = choice(high_cards)
			
			if (not self.is_scoring_suit(card[0])
			    and self.num_players_out(card[0]) == 0
			    and self.num_unseen(card[0]) > 5):
				return card
		
		# If I do not have anything queen or above of spades
		# and if no one is out of spades, then play the
		# highest spade below the queen.
		
		if (have_suit(valid_cards, spades)
		    and self.num_players_out(spades) == 0
		    and not self.is_played((spades, queen))
		    and not self.spades_is_iffy()):
			
			spades_list = filter(f_spades, valid_cards)

			spades_list.sort(s_rank,reverse=True)

			# card is the highes spade below the queen.
			# Let's form a new list of all those cards
			# which are "equivalent" to it.
			# self.print_card_list(spades_list)

			card=spades_list[0]

			return self.choose_equiv(card,spades_list)
		
		# Play a giveaway heart
		
		giveaway_hearts = [x for x in filter(f_hearts, valid_cards) if self.is_giveaway_card(x)]
		if len(giveaway_hearts) > 0:
			return choice(giveaway_hearts)
		
		# Even if spades are bad, play a low spade provided I
		# have nothing above Jack in my hand and the Queen is
		# still out.
		
		if (have_suit(valid_cards, spades)
		    and not self.is_played((spades, queen))
		    and not self.spades_is_iffy()):
			
			spades_list = filter(f_spades, valid_cards)
			spades_list.sort(s_rank)

			card=spades_list[0]

			return self.choose_equiv(spades_list[0],spades_list)
		
		# Play a giveaway card in any suit.  Choose the suit
		# with the most folks out of it.

		for list in cards:
			if len(list) == 0:
				continue

			if (cards[0][0] == spades and self.spades_is_iffy()):
				continue
			giveaways = [x for x in list if self.is_giveaway_card(x)]
			if len(giveaways) > 0:
				return choice(giveaways)

		# Play a "probable giveaway".  This is a card where
		# the number of cards unseen below it is fewer than
		# the 4 - number of players out of the suit.  Of
		# course, we still require that there is at least one
		# unseen card above this card!

		candidate_suits = [x for x in cards if len(x) > 0 and self.is_probable_giveaway_card(x[0]) and (not x[0][0] == spades or not self.spades_is_iffy())]

		# If we have a probable giveaway that is the only card
		# in that suit, play it first.

		# Otherwise, rank preference according to the number
		# of cards unseen above the *second* card of the suit.
		
		candidate_suits.sort(self.s_prob_give_pref)

		if len(candidate_suits) > 0:
			return self.choose_equiv(candidate_suits[0][0], candidate_suits[0])
	
		# Pick the card that has the most trump cards above it
		# unseen.  (We may as well restrict ourselves to the
		# lowest card of each suit.)
		best_suit = []
		count = 0
		
		for challenger in cards:
			if (len(challenger) > 0
			    and (challenger[0][0] != spades
				or not self.spades_is_iffy())):

				# If we have the Queen or above in
				# Spades, then it's not the best bet,
				# unless either there is no best_suit
				# or the best_suit has count of 0

				challenger.sort(s_rank)
				if len(best_suit) == 0:
					best_suit = challenger
					count = self.unseen_above(best_suit[0])

				else:
					c_count = self.unseen_above(challenger[0])
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
						if (len(pointless) > 0
						    and self.unseen_above(pointless[0]) > 0):
							
							return self.choose_equiv(pointless[0],pointless)
			return self.choose_equiv(best_suit[0],best_suit)
		else:
			cards.sort(self.s_prob_give_pref)
			return self.choose_equiv(cards[0][0], cards[0])
	
	
	def avoid_trick(self, valid_cards, high_card):
		"""
		I don't want to take the trick!
		"""

		## If we can avoid taking the trick, do so
		## with the highest card possible (up to
		## equivalence)
		below = [x for x in valid_cards if x[1] < high_card[1]]
		if len(below) > 0:
			below.sort(s_rank,reverse=True)
			return self.choose_equiv(below[0],below)

			
		# we can't dodge, so take it with the fewest points.
		# If we're the last player, use a high card.
		# Otherwise use a low card and hope that someone else
		# gets it.

		# remove the queen of spades, since we don't want to
		# play her unless we have to.
		if len(valid_cards) > 1:
			valid_cards=[x for x in valid_cards if x != (spades,queen)]
		if self.trick.num_played == 3:
			valid_cards.sort(s_rank, reverse=True)
		else:
			valid_cards.sort(s_rank)
		
		return self.choose_equiv(valid_cards[0],valid_cards)
	
	def take_trick(self, valid_cards, high_card):

		# if someone else will take the Queen, play it!
		# Getting rid of the Queen is important.
		if (spades, queen) in valid_cards and queen < high_card[1]:
			return (spades, queen)
		
		# Play the highest card that's not a point
		pointless_cards = filter(f_pointless_cards, valid_cards)
		if len(pointless_cards):
			pointless_cards.sort(s_rank, reverse=True)

			# Try not to trump the queen of spades
			
			if (high_card[0] == spades and
			    not self.is_played((spades, queen))):
				safe_cards=[x for x in pointless_cards if x[1] < queen]
				if len(safe_cards):
					return self.choose_equiv(safe_cards[0],safe_cards)
				# Can't avoid playing a dangerous spade.
			return self.choose_equiv(pointless_cards[0],pointless_cards)
		
		# Have to play a point. Go low
		valid_cards.sort(s_rank)
		return self.choose_equiv(valid_cards[0],valid_cards)
	
	def dump_cards(self, valid_cards, high_card):
		# We don't have the suit at all.  First, try to dump
		# high spades.

		if (spades, queen) in valid_cards:
			return (spades, queen)

		if ((spades, ace_high) in valid_cards
		    and self.is_scoring_suit(spades)):
			return (spades, ace_high)
		
		if ((spades, king) in valid_cards and
		    self.is_scoring_suit(spades)):
			return (spades, king)

		# Dump any card which is the last card of the suit,
		# has some unseen card below it and has no unseen
		# cards above it.
		
		lone_cards = [x for x in valid_cards if len(self.same_suit_from_list(x, valid_cards)) == 1 and self.unseen_below(x) > 0 and self.unseen_above(x) == 0]
		if len(lone_cards) > 0:
			return choice(lone_cards)

		# Dump any card which is the last card of the suit and
		# has some unseen card below it.

		lone_cards = [x for x in valid_cards if len(self.same_suit_from_list(x, valid_cards)) == 1 and self.unseen_below(x) > 0]
		if len(lone_cards) > 0:
			return choice(lone_cards)
		
		# Dump any card with no cards unseen above it.
		
		# If there are candidates from several suits, then
		# choose the suit with the fewest safety cards (cards
		# with unseen_above > 0).

		high_cards = [x for x in valid_cards
			      if self.unseen_above(x) == 0 and self.unseen_below(x) > 0]
		
		high_cards.sort(self.s_dump_rank)

		if len(high_cards) > 0:
			return self.choose_equiv(high_cards[0],high_cards)
		
		# Dump the highest point card we have.
		point_cards = filter(f_point_cards, valid_cards)
		if len(point_cards):
			point_cards.sort(s_rank, reverse=True)
			return self.choose_equiv(point_cards[0],
						 point_cards)

		## Try to dump cards that have some unseen cards below
		## them and few unseen cards above them first.
		candidates=[x for x in valid_cards if self.unseen_below(x) > 0]
		if len(candidates) > 0:
			candidates.sort(self.s_unseen_above)
			return self.choose_equiv(candidates[0],candidates)
		
			## None of my cards have any unseen cards
			## below them.  I'm not sure, but it seems to
			## me that this is a safe situation.  Just
			## pick one.

		return choice(valid_cards)
			
		
		
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
		
		if have_suit(valid_cards, high_card[0]):
			if len(filter(f_point_cards, self.trick.card)) > 0:
				return self.avoid_trick(valid_cards, high_card)
			
			return self.take_trick(valid_cards, high_card)
		
		return self.dump_cards(valid_cards, high_card)
	
	def is_dangerous_trick(self, high_card):
		"""
		return true if one of the remaining players doesn't
		have the suit of the trick and either (has hearts or
		queen of spades is not played)
		"""

		#First trick: no points possible, so not dangerous!
		if len(self.hand) == 13:
			return False

		if len(filter(f_point_cards, self.trick.card)) > 0:
			return True
		
		if self.num_unseen(high_card[0]) + self.trick.num_played < 6:
			return True
		
		for index in range(4):
			card = self.trick.card[index]
			if (card is None
			    and (self.trick.trump, index) in self.player_out_suits
			    and ((hearts, index) not in self.player_out_suits
				 or ((spades, queen) not in self.seen_cards
				     and (spades,index) not in self.player_out_suits))):
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
		
		if have_suit(valid_cards, high_card[0]):
			if (len(filter(f_point_cards, self.trick.card)) > 0
			    or self.is_dangerous_trick(high_card)):
				return self.avoid_trick(valid_cards, high_card)
			
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

		# self.print_card_list(filter(self.f_valid, self.hand))
		
		if self.moon_shooter():
			ret = self.moon_defense()
			if ret != None:
				return ret
		
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

