import unittest

import numpy as np

from jass.agents.trump.features import (obs_to_trump_features, label_to_class, class_to_action,
                                        NR_FEATURES, FOREHAND_INDEX, PUSH_CLASS)
from jass.game.const import PUSH, HEARTS, UNE_UFE, card_ids
from jass.game.game_observation import GameObservation
from jass.game.game_util import get_cards_encoded_from_str


def obs_with(hand, forehand):
    obs = GameObservation()
    obs.hand = get_cards_encoded_from_str(hand)
    obs.forehand = forehand
    return obs


class TrumpFeaturesTestCase(unittest.TestCase):
    HAND = ['DA', 'DK', 'HJ', 'H9', 'SA', 'S6', 'CQ', 'C10', 'C7']

    def test_cards_are_one_hot_in_const_order(self):
        features = obs_to_trump_features(obs_with(self.HAND, forehand=-1))
        self.assertEqual(NR_FEATURES, len(features))
        self.assertEqual(9, features[:36].sum())
        for card in self.HAND:
            self.assertEqual(1.0, features[card_ids[card]])

    def test_forehand_flag_is_set_only_when_push_is_allowed(self):
        self.assertEqual(1.0, obs_to_trump_features(obs_with(self.HAND, forehand=-1))[FOREHAND_INDEX])
        self.assertEqual(0.0, obs_to_trump_features(obs_with(self.HAND, forehand=0))[FOREHAND_INDEX])

    def test_label_mapping_round_trips(self):
        self.assertEqual(HEARTS, label_to_class(HEARTS))
        self.assertEqual(UNE_UFE, label_to_class(UNE_UFE))
        self.assertEqual(PUSH_CLASS, label_to_class(6))
        self.assertEqual(PUSH_CLASS, label_to_class(10))
        self.assertEqual(PUSH, class_to_action(PUSH_CLASS))
        self.assertEqual([0, 1, 2, 3, 4, 5], [class_to_action(c) for c in range(6)])


if __name__ == '__main__':
    unittest.main()
