# HSLU
#
# Created by Thomas Koller on 7/28/2020
#
import logging
import numpy as np
from jass.agents.agent import Agent
from jass.game.const import PUSH, MAX_TRUMP, card_strings
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber


class AgentRandomSchieber (Agent):
    """
    Randomly select actions for the match of jass (Schieber)
    """
    def __init__(self):
        # log actions
        self._logger = logging.getLogger(__name__)
        # Use rule object to determine valid actions
        self._rule = RuleSchieber()
        # init random number generator
        self._rng = np.random.default_rng()

    def action_trump(self, obs: GameObservation) -> int:
        """
        Select trump randomly. Pushing is selected with probability 0.5 if possible.
        Args:
            obs: the current match
        Returns:
            trump action
        """
        if obs.forehand == -1:
            # if forehand is not yet set, we are the forehand player and can select trump or push
            if self._rng.choice([True, False]):
                return PUSH
        # if not push or forehand, select a trump
        return int(self._rng.integers(low=0, high=MAX_TRUMP, endpoint=True))

    def action_play_card(self, obs: GameObservation) -> int:
        """
        Select randomly a card from the valid cards
        Args:
            obs: The observation of the jass match for the current player
        Returns:
            card to play
        """
        # cards are one hot encoded
        valid_cards = self._rule.get_valid_cards_from_obs(obs)
        # convert to list and draw a value
        card = self._rng.choice(np.flatnonzero(valid_cards))
        self._logger.debug('Played card: {}'.format(card_strings[card]))
        return card

