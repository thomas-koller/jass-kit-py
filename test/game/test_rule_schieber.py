import unittest
from jass.game.const import *
from jass.game.rule_schieber import RuleSchieber


class RuleSchieberTestCase(unittest.TestCase):
    def setUp(self):
        self.hand = np.zeros(36, np.int32)
        self.rule = RuleSchieber()

    def test_obe_une(self):
        self.hand[[SA, SK, H7, HJ]] = 1

        # no color in hand
        valid = self.rule.get_valid_cards(self.hand, [CA], 1, OBE_ABE)
        self.assertTrue(np.all(self.hand == valid))

        valid = self.rule.get_valid_cards(self.hand, [C6], 1, UNE_UFE)
        self.assertTrue(np.all(self.hand == valid))

        # color in hand
        valid = self.rule.get_valid_cards(self.hand, [SQ], 1, OBE_ABE)
        expected = np.zeros(36, np.int32)
        expected[[SA, SK]] = 1
        self.assertTrue(np.all(expected == valid))

        valid = self.rule.get_valid_cards(self.hand, [S7], 1, UNE_UFE)
        self.assertTrue(np.all(expected == valid))

    def test_first_move(self):
        self.hand[[SA, SK, H7, HJ, C6, C7, D10]] = 1
        valid = self.rule.get_valid_cards(self.hand, [], 0, UNE_UFE)
        self.assertTrue(np.all(self.hand == valid))
        valid = self.rule.get_valid_cards(self.hand, [], 0, OBE_ABE)
        self.assertTrue(np.all(self.hand == valid))
        valid = self.rule.get_valid_cards(self.hand, [], 0, C)
        self.assertTrue(np.all(self.hand == valid))
        valid = self.rule.get_valid_cards(self.hand, [], 0, S)
        self.assertTrue(np.all(self.hand == valid))

    def test_trump_no_trump(self):
        self.hand[[SA, SK, H7, HJ, C6, C7]] = 1
        valid = self.rule.get_valid_cards(self.hand, [D10], 1, D)
        self.assertTrue(np.all(self.hand == valid))
        valid = self.rule.get_valid_cards(self.hand, [DJ, D9, D10], 3, D)
        self.assertTrue(np.all(self.hand == valid))

    def test_trump_have_trump(self):
        self.hand[[SA, SK, H7, HJ, C6, C7]] = 1
        # give one of the trumps
        valid = self.rule.get_valid_cards(self.hand, [SJ], 1, S)
        expected = np.zeros(36, np.int32)
        expected[[SA, SK]] = 1
        self.assertTrue(np.all(expected == valid))

        # give one of the trumps, including jack
        valid = self.rule.get_valid_cards(self.hand, [H10], 1, H)
        expected = np.zeros(36, np.int32)
        expected[[HJ, H7]] = 1
        self.assertTrue(np.all(expected == valid))

    def test_trump_jack(self):
        self.hand[[SA, SK, HJ, C6, C7]] = 1
        valid = self.rule.get_valid_cards(self.hand, [H6, H8], 2, H)
        # we do not have to give the jack, so any card is fine
        self.assertTrue(np.all(self.hand == valid))

    def test_other_color(self):
        self.hand[[SA, SK, HJ, C6, C7]] = 1
        valid = self.rule.get_valid_cards(self.hand, [S10, C6], 2, H)

        # give color or trump
        expected = np.zeros(36, np.int32)
        expected[[SA, SK, HJ]] = 1
        self.assertTrue(np.all(expected == valid))

        # do not have the color, so any card is fine
        valid = self.rule.get_valid_cards(self.hand, [DA, DK, D10], 3, H)
        self.assertTrue(np.all(self.hand == valid))

    def test_other_color_trump_played_H(self):
        self.hand[[SA, SK, HJ, H8, H6, C7, C6]] = 1
        valid = self.rule.get_valid_cards(self.hand, [C10, CA, H10], 3, H)

        # give color or higher trump (HJ)
        expected = np.zeros(36, np.int32)
        expected[[C7, C6, HJ]] = 1
        self.assertTrue(np.all(expected == valid))

        # same for higher trump played
        valid = self.rule.get_valid_cards(self.hand, [C10, CA, HA], 3, H)
        self.assertTrue(np.all(expected == valid))

    def test_other_color_trump_played_S(self):
        self.hand[[SA, SK, S7, H8, H6, C7, C6]] = 1
        valid = self.rule.get_valid_cards(self.hand, [HK, H8, SQ], 3, S)

        # give color or higher trump
        expected = np.zeros(36, np.int32)
        expected[[H8, H6, SA, SK]] = 1
        self.assertTrue(np.all(expected == valid))

        # no higher trump, only color allowed
        valid = self.rule.get_valid_cards(self.hand, [HK, SJ], 2, S)
        expected = np.zeros(36, np.int32)
        expected[[H8, H6]] = 1
        self.assertTrue(np.all(expected == valid))

    def test_other_color_trump_played_9(self):
        self.hand[[SA, SK, H9, H8, H6, C7, C6]] = 1
        valid = self.rule.get_valid_cards(self.hand, [C10, CA, H10], 3, H)

        # give color or higher trump (HJ)
        expected = np.zeros(36, np.int32)
        expected[[C7, C6, H9]] = 1
        self.assertTrue(np.all(expected == valid))

        # same for higher trump played
        valid = self.rule.get_valid_cards(self.hand, [C10, CA, HA], 3, H)
        self.assertTrue(np.all(expected == valid))

    def test_only_trump(self):
        self.hand[[DA, DK, D8]] = 1
        valid = self.rule.get_valid_cards(self.hand, [C10, DJ, H10], 3, D)
        self.assertTrue(np.all(self.hand == valid))

    def test_other_color_second_player(self):
        self.hand[[SA, SK, H9, H8, H6, C7, C6]] = 1
        valid = self.rule.get_valid_cards(self.hand, [C10], 1, H)

        # give color or trump
        expected = np.zeros(36, np.int32)
        expected[[C7, C6, H9, H8, H6]] = 1
        self.assertTrue(np.all(expected == valid))


if __name__ == '__main__':
    unittest.main()
