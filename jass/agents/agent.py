# HSLU
#
# Created by Thomas Koller on 7/28/2020
#
from jass.game.game_observation import GameObservation


class Agent:
    """
    Agent to act as a player in a game of jass.
    """
    def action_trump(self, obs: GameObservation) -> int:
        """
        Determine trump action for the given observation
        Args:
            obs: the game observation, it must be in a state for trump selection

        Returns:
            selected trump as encoded in jass.game.const or jass.game.const.PUSH
        """
        raise NotImplementedError

    def action_play_card(self, obs: GameObservation) -> int:
        """
        Determine the card to play.

        Args:
            obs: the game observation

        Returns:
            the card to play, int encoded as defined in jass.game.const
        """
        raise NotImplementedError
