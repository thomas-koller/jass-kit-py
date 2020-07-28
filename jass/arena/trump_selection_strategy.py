# HSLU
#
# Created by Thomas Koller on 05.09.18
#
from jass.game.game_sim import GameSim


class TrumpStrategy:
    """
    Base class to implemented different strategies for selecting trump.
    """

    def determine_trump(self, game: GameSim, arena: 'Arena'):
        """
        Determine the trump. Must be implemented in the derived class. The selected trump must be set in the game.
        Args:
            rnd: the round for which to determine trump.
            arena: the arena to which this strategy belongs, needed to access the players and possibly other data
        """
        raise NotImplementedError
