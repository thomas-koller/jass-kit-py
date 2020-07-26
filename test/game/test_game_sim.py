import unittest
import numpy as np

from jass.game.const import *
from jass.game.game_sim import GameSim
from jass.game.game_state import GameState
from jass.game.game_util import deal_random_hand, get_cards_encoded
from jass.game.rule_schieber import RuleSchieber


class GameSimTestCase(unittest.TestCase):

    def test_init_from_cards(self):
        game = GameSim(rule=RuleSchieber())
        hands = deal_random_hand()
        game.init_from_cards(hands=hands, dealer=NORTH)

        # play random game
        game.action_trump(SPADES)

        while not game.is_done():
            valid_cards = game.rule.get_valid_cards_from_state(game.state)
            card = np.random.choice(np.flatnonzero(valid_cards))
            game.action_play_card(card)
            game.rule.assert_invariants(game.state)

    def test_calc_points(self):
        rule = RuleSchieber()
        trick = np.array([SA, SK, SQ, SJ])
        points = rule.calc_points(trick, is_last=False, trump=DIAMONDS)
        self.assertEqual(20, points)

        points = rule.calc_points(trick, is_last=True, trump=HEARTS)
        self.assertEqual(25, points)

        points = rule.calc_points(trick, is_last=False, trump=SPADES)
        self.assertEqual(38, points)

        points = rule.calc_points(trick, is_last=False, trump=CLUBS)
        self.assertEqual(20, points)

        trick = np.array([SA, SJ, S6, S9])
        points = rule.calc_points(trick, is_last=False, trump=SPADES)
        self.assertEqual(45, points)
        
    def test_calc_winner(self):
        rule = RuleSchieber()
        first_player = EAST
        #                 E   N   W   S
        trick = np.array([SA, SK, HQ, C7])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=DIAMONDS), EAST)
        self.assertEqual(rule.calc_winner(trick, first_player, trump=HEARTS), WEST)
        self.assertEqual(rule.calc_winner(trick, first_player, trump=SPADES), EAST)
        self.assertEqual(rule.calc_winner(trick, first_player, trump=CLUBS), SOUTH)
        self.assertEqual(rule.calc_winner(trick, first_player, trump=OBE_ABE), EAST)
        self.assertEqual(rule.calc_winner(trick, first_player, trump=UNE_UFE), NORTH)

        #                 E   N    W   S
        trick = np.array([S9, S10, SQ, SK])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=SPADES), EAST)

        #                 E   N    W   S
        trick = np.array([S9, S10, SJ, SK])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=SPADES), WEST)

        #                E   N    W   S
        trick = np.array([SA, D6, D7, SJ])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=HEARTS), EAST)

        #                 E   N    W   S
        trick = np.array([SA, D6, D7, SJ])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=DIAMONDS), WEST)

        #                 E   N    W   S
        trick = np.array([SA, D6, D7, SJ])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=SPADES), SOUTH)

        #                E   N    W   S
        trick = np.array([SA, D6, D7, S9])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=SPADES), SOUTH)

        #                E   N    W   S
        trick = np.array([D7, SA, D6, S9])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=UNE_UFE), WEST)

        #                E   N    W   S
        trick = np.array([SA, D6, D7, S9])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=UNE_UFE), SOUTH)

        #                E   N    W   S
        trick = np.array([SA, D6, D7, S9])
        self.assertEqual(rule.calc_winner(trick, first_player, trump=OBE_ABE), EAST)
        
    def test_complete_game(self):
        # replay game manually from a log file entry
        # {"trump":5,"dealer":3,"tss":1,"tricks":[{"cards":["C7","CK","C6","CJ"],"points":17,"win":0,"first":2},
        rule = RuleSchieber()
        game = GameSim(rule=rule)
        hands = np.array([
            get_cards_encoded([C6, S7, S9, HQ, DA, CA, S8, D6, S10]),      # N
            get_cards_encoded([CK, C10, D10, H6, H7, H9, HK, DQ, D8]),     # E
            get_cards_encoded([C7, SA, SQ, HJ, C9, DJ, CQ, DK, C8]),       # S
            get_cards_encoded([CJ, SJ, S6, H10, H8, HA, SK, D9, D7 ]),     # W
        ], dtype=np.int32)
        
        game.init_from_cards(hands=hands, dealer=WEST)
        game.action_trump(PUSH)
        game.action_trump(U)

        game.action_play_card(C7)        # S
        rule.assert_invariants(game.state)

        game.action_play_card(CK)        # E
        rule.assert_invariants(game.state)

        game.action_play_card(C6)        # N
        rule.assert_invariants(game.state)

        game.action_play_card(CJ)        # W
        rule.assert_invariants(game.state)
        self.assertEqual(1, game.state.nr_tricks)
        self.assertEqual(17, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(NORTH, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(2, game.state.trick_first_player[game.state.nr_tricks-1])

        # {"cards":["S7","SJ","SA","C10"],"points":12,"win":0,"first":0},
        game.action_play_card(S7), rule.assert_invariants(game.state) # N
        game.action_play_card(SJ), rule.assert_invariants(game.state) # W
        game.action_play_card(SA), rule.assert_invariants(game.state) # S
        game.action_play_card(C10), rule.assert_invariants(game.state) # E
        self.assertEqual(2, game.state.nr_tricks)
        self.assertEqual(12, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(NORTH, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(0, game.state.trick_first_player[game.state.nr_tricks-1])

        # {"cards":["S9","S6","SQ","D10"],"points":24,"win":3,"first":0},
        game.action_play_card(S9), rule.assert_invariants(game.state) # N
        game.action_play_card(S6), rule.assert_invariants(game.state)
        game.action_play_card(SQ), rule.assert_invariants(game.state)
        game.action_play_card(D10), rule.assert_invariants(game.state)
        self.assertEqual(3, game.state.nr_tricks)
        self.assertEqual(24, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(WEST, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(0, game.state.trick_first_player[game.state.nr_tricks-1])

        # {"cards":["H10","HJ","H6","HQ"],"points":26,"win":1,"first":3},
        game.action_play_card(H10), rule.assert_invariants(game.state) #W
        game.action_play_card(HJ), rule.assert_invariants(game.state)
        game.action_play_card(H6), rule.assert_invariants(game.state)
        game.action_play_card(HQ), rule.assert_invariants(game.state)
        self.assertEqual(4, game.state.nr_tricks)
        self.assertEqual(26, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(EAST, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(3, game.state.trick_first_player[game.state.nr_tricks-1])

        # {"cards":["H7","DA","H8","C9"],"points":8,"win":1,"first":1},
        game.action_play_card(H7), rule.assert_invariants(game.state) # E
        game.action_play_card(DA), rule.assert_invariants(game.state)
        game.action_play_card(H8), rule.assert_invariants(game.state)
        game.action_play_card(C9), rule.assert_invariants(game.state)
        self.assertEqual(5, game.state.nr_tricks)
        self.assertEqual(8, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(EAST, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(1, game.state.trick_first_player[game.state.nr_tricks-1])

        # {"cards":["H9","CA","HA","DJ"],"points":2,"win":1,"first":1},
        game.action_play_card(H9), rule.assert_invariants(game.state) # E
        game.action_play_card(CA), rule.assert_invariants(game.state)
        game.action_play_card(HA), rule.assert_invariants(game.state)
        game.action_play_card(DJ), rule.assert_invariants(game.state)
        self.assertEqual(6, game.state.nr_tricks)
        self.assertEqual(2, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(EAST, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(1, game.state.trick_first_player[game.state.nr_tricks-1])

        # {"cards":["HK","S8","SK","CQ"],"points":19,"win":1,"first":1},
        game.action_play_card(HK), rule.assert_invariants(game.state) # E
        game.action_play_card(S8), rule.assert_invariants(game.state)
        game.action_play_card(SK), rule.assert_invariants(game.state)
        game.action_play_card(CQ), rule.assert_invariants(game.state)
        self.assertEqual(7, game.state.nr_tricks)
        self.assertEqual(19, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(EAST, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(1, game.state.trick_first_player[game.state.nr_tricks-1])

        # {"cards":["DQ","D6","D9","DK"],"points":18,"win":0,"first":1},
        game.action_play_card(DQ), rule.assert_invariants(game.state) # E
        game.action_play_card(D6), rule.assert_invariants(game.state)
        game.action_play_card(D9), rule.assert_invariants(game.state)
        game.action_play_card(DK), rule.assert_invariants(game.state)
        self.assertEqual(8, game.state.nr_tricks)
        self.assertEqual(18, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(NORTH, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(1, game.state.trick_first_player[game.state.nr_tricks-1])

        # {"cards":["S10","D7","C8","D8"],"points":31,"win":0,"first":0}]
        game.action_play_card(S10), rule.assert_invariants(game.state) #N
        game.action_play_card(D7), rule.assert_invariants(game.state)
        game.action_play_card(C8), rule.assert_invariants(game.state)
        game.action_play_card(D8), rule.assert_invariants(game.state)
        self.assertEqual(9, game.state.nr_tricks)
        self.assertEqual(31, game.state.trick_points[game.state.nr_tricks-1])
        self.assertEqual(0, game.state.trick_winner[game.state.nr_tricks-1])
        self.assertEqual(0, game.state.trick_first_player[game.state.nr_tricks-1])

        # test equality operator
        self.assertTrue(game == game)


if __name__ == '__main__':
    unittest.main()
