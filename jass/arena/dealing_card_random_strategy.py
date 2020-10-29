# HSLU
#
# Created by Thomas Koller on 05.11.19
#
import numpy as np

from jass.arena.dealing_card_strategy import DealingCardStrategy
from jass.game.game_util import deal_random_hand


class DealingCardRandomStrategy(DealingCardStrategy):
    """
    Deal cards randomly. This is the default implementation.
    """
    def deal_cards(self, game_nr: int = 0, total_nr_games: int = 0) -> np.ndarray:
        return deal_random_hand()
