# HSLU
#
# Created by Thomas Koller on 27.07.20
#
import numpy as np


class DealingCardStrategy:
    """
    Abstract base class to deal for a game in the arena

    """
    def deal_cards(self, game_nr: int = 0, total_nr_games: int = 0) -> np.ndarray:
        """
        Args:
            game_nr: number of games played so far, starting with 1 for the first game
            total_nr_games: total number of games to be played, or 0 if not used

        """
        raise NotImplementedError
