# HSLU
#
# Created by Thomas Koller on 27.07.20
#
from jass.game.game_sim import GameSim


class DealingCardStrategy:
    """
    Abstract base class to deal for a game in the arena

    """
    def deal_cards(self, game: GameSim, game_nr: int, total_nr_games=0):
        """

        Args:
            game: game simulation, will be changed with new hand cards
            game_nr: number of games played so far, starting with 1 for the first game
            total_nr_games: total number of games to be played, or 0 if not used

        """
        raise NotImplementedError
