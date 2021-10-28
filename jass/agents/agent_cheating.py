# HSLU
#
# Created by Thomas Koller on 7/28/2020
#
from jass.game.game_state import GameState


class AgentCheating:
    """
    Agent to act as a player in a game of jass in cheating mode (all information is known).
    """
    def action_trump(self, state: GameState) -> int:
        """
        Determine trump action for the given observation
        Args:
            state: the game state, it must be in a state for trump selection

        Returns:
            selected trump as encoded in jass.game.const or jass.game.const.PUSH
        """
        raise NotImplementedError

    def action_play_card(self, state: GameState) -> int:
        """
        Determine the card to play.

        Args:
            state: the game state

        Returns:
            the card to play, int encoded as defined in jass.game.const
        """
        raise NotImplementedError
