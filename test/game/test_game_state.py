import copy
import unittest
import numpy as np

from jass.game.const import NORTH
from jass.game.game_sim import GameSim
from jass.game.game_state import GameState
from jass.game.game_util import deal_random_hand
from jass.game.rule_schieber import RuleSchieber


class MyTestCase(unittest.TestCase):
    def test_copy(self):
        game_state = GameState()
        game_state_shallow = copy.copy(game_state)
        game_state_deep = copy.deepcopy(game_state)

        self.assertEqual(-1, game_state_shallow.dealer)
        self.assertEqual(-1, game_state_deep.dealer)
        self.assertEqual(0, game_state_shallow.hands[0, 0])
        self.assertEqual(0, game_state_deep.hands[0, 0])

        # change dealer
        game_state.dealer = 1

        # values have not changes
        self.assertEqual(-1, game_state_shallow.dealer)
        self.assertEqual(-1, game_state_deep.dealer)

        # change value in numpy array
        game_state.hands[0, 0] = 1

        # shallow copy takes value from changed state
        self.assertEqual(1, game_state_shallow.hands[0, 0])

        # deep copy keeps value
        self.assertEqual(0, game_state_deep.hands[0, 0])

    def test_eq(self):
        game_sim = GameSim(rule=RuleSchieber())

        hands = deal_random_hand()

        game_sim.init_from_cards(hands, NORTH)

        game_state = game_sim.state
        game_state_shallow = copy.copy(game_state)
        game_state_deep = copy.deepcopy(game_state)

        self.assertTrue(game_state == game_state_shallow)
        self.assertTrue(game_state == game_state_deep)


if __name__ == '__main__':
    unittest.main()
