# HSLU
#
# Created by Thomas Koller on 05.11.19
#

from jass.arena.dealing_card_strategy import DealingCardStrategy

from jass.game.game_sim import GameSim
from jass.game.game_util import deal_random_hand


class DealingCardRandomStrategy(DealingCardStrategy):
    """
    Deal cards randomly. This is the default implementation.
    """
    def deal_cards(self, game: GameSim, game_nr: int, total_nr_games=0):
        return deal_random_hand()
