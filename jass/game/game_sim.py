# HSLU
#
# Created by Thomas Koller on 7/22/2020
#

# Simulator for a game

import copy
import numpy as np

from jass.game.game_util import full_to_trump
from jass.game.const import next_player, PUSH, partner_player, NORTH, SOUTH, TRUMP_FULL_OFFSET
from jass.game.game_rule import GameRule
from jass.game.game_state import GameState
from jass.game.game_state_util import observation_from_state


class GameSim:
    """
    Class for simulating a game. A game consists of selecting trump and playing 36 cards, currently the trump selection
    phase is implemented for Schieber. For other versions of the game regarding the order of actions, the class can be
    overridden. The actual rules of the game, points scoring, winning tricks and calculating which cards are allowed
    to be played are implemented in the rule class.
    """
    def __init__(self, rule: GameRule):
        # the internal state of the game is stored in a GameState object that can be set and retrieved
        self._state = GameState()
        self._rule = rule

    def init_from_state(self, state: GameState):
        self._state = copy.deepcopy(state)

    def init_from_cards(self, hands: np.array, dealer: int):
        self._state.dealer = dealer
        self._state.player = next_player[dealer]
        self._state.trump = -1
        self._state.forehand = -1
        self._state.hands = hands.copy()
        self._state.tricks.fill(-1)
        self._state.trick_winner.fill(-1)
        self._state.trick_points.fill(0)
        self._state.trick_first_player.fill(-1)
        self._state.current_trick = self._state.tricks[0, :]
        self._state.nr_tricks = 0
        self._state.nr_cards_in_trick = 0
        self._state.nr_played_cards = 0
        self._state.points[0] = 0
        self._state.points[1] = 0

    @property
    def rule(self):
        return self._rule

    @property
    def state(self):
        return self._state

    def get_observation(self):
        """
        Get the observation for the current player in the current state of the game.

        Returns:
            The observation for the current player.
        """
        return observation_from_state(self._state)

    def action_trump(self, action: int) -> None:
        if self._state.forehand == -1:
            # this is the action of the forehand player
            if action == PUSH:
                self._state.forehand = 0
                self._state.player = partner_player[self._state.player]
            else:
                self._state.forehand = 1
                self._state.trump = action
                self._state.declared_trump = self._state.player
                self._state.trick_first_player[0] = self._state.player
                # player remains the same
        elif self._state.forehand == 0:
            # action of the partner of the forehand player
            self._state.trump = action
            self._state.declared_trump = self._state.player
            self._state.player = next_player[self._state.dealer]
            self._state.trick_first_player[0] = self._state.player
        else:
            raise ValueError('Unexpected value {} for forehand in action_trump'.format(self._state.forehand))

    def action_play_card(self, card: int) -> None:
        """
        Play a card as the current player and update the state of the round.

        Preconditions:
            self._state.nr_played_cards < 36
            self._state.hands[self.player,card] == 1
            (trump selection done according to rules of the jass variation)

        Postconditions:
            see assert_invariants

        Args:
            card: The card to play
        """
        # remove card from player
        self._state.hands[self._state.player, card] = 0

        # place in trick
        self._state.current_trick[self._state.nr_cards_in_trick] = card
        self._state.nr_played_cards += 1

        if self._state.nr_cards_in_trick < 3:
            if self._state.nr_cards_in_trick == 0:
                # make sure the first player is set on the first card of a new trick
                # (it will not have been set, if the round has been restored from dict)
                self._state.trick_first_player[self._state.nr_tricks] = self._state.player
            # trick is not yet finished
            self._state.nr_cards_in_trick += 1
            self._state.player = next_player[self._state.player]
        else:
            # finish current trick
            self._end_trick()

    def action(self, action: int):
        """
        Perform an action. The action can be a card or a trump.
        Args:
            action: full action that is either card or trump
        """
        if action < TRUMP_FULL_OFFSET:
            self.action_play_card(action)
        else:
            trump_action = full_to_trump(action)
            self.action_trump(trump_action)

    def is_done(self):
        """
        Return true if the game is finished.

        Returns:
            true if the game is finished, false otherwise
        """
        return self._state.nr_played_cards == 36

    def _end_trick(self) -> None:
        """
        End the current trick and update all the necessary fields.
        """
        # update information about the current trick
        points = self._rule.calc_points(self._state.current_trick, self._state.nr_played_cards == 36, self._state.trump)
        self._state.trick_points[self._state.nr_tricks] = points
        winner = self._rule.calc_winner(self._state.current_trick,
                                        self._state.trick_first_player[self._state.nr_tricks],
                                        self._state.trump)
        self._state.trick_winner[self._state.nr_tricks] = winner

        if winner == NORTH or winner == SOUTH:
            self._state.points[0] += points
        else:
            self._state.points[1] += points
        self._state.nr_tricks += 1
        self._state.nr_cards_in_trick = 0

        if self._state.nr_tricks < 9:
            # not end of round
            # next player is the winner of the trick
            self._state.trick_first_player[self._state.nr_tricks] = winner
            self._state.player = winner
            self._state.current_trick = self._state.tricks[self._state.nr_tricks, :]
        else:
            # end of round
            self._state.player = -1
            self._state.current_trick = None
