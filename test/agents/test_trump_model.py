import os
import tempfile
import unittest

import numpy as np

from jass.agents.trump.features import NR_CLASSES, NR_FEATURES, PUSH_CLASS
from jass.agents.trump.trump_model import DEFAULT_MODEL_PATH, TrumpModel
from jass.game.const import HEARTS, PUSH, SPADES
from jass.game.game_observation import GameObservation
from jass.game.game_util import get_cards_encoded_from_str

HAND = ['DA', 'DK', 'HJ', 'H9', 'SA', 'S6', 'CQ', 'C10', 'C7']


def obs_with(forehand):
    obs = GameObservation()
    obs.hand = get_cards_encoded_from_str(HAND)
    obs.forehand = forehand
    return obs


def model_preferring(first, second):
    """A model whose logits rank class `first` highest and `second` next, whatever the hand."""
    bias = np.zeros(NR_CLASSES, dtype=np.float32)
    bias[first], bias[second] = 2.0, 1.0
    return TrumpModel(np.zeros((NR_CLASSES, NR_FEATURES), dtype=np.float32), bias)


class TrumpModelTestCase(unittest.TestCase):

    def test_picks_the_highest_logit(self):
        self.assertEqual(SPADES, model_preferring(SPADES, HEARTS).action_trump(obs_with(forehand=-1)))

    def test_push_is_returned_as_game_action(self):
        self.assertEqual(PUSH, model_preferring(PUSH_CLASS, HEARTS).action_trump(obs_with(forehand=-1)))

    def test_never_pushes_after_partner_pushed(self):
        self.assertEqual(HEARTS, model_preferring(PUSH_CLASS, HEARTS).action_trump(obs_with(forehand=0)))

    def test_probabilities_sum_to_one_and_push_is_zero_when_masked(self):
        model = model_preferring(PUSH_CLASS, HEARTS)
        features = np.zeros((2, NR_FEATURES), dtype=np.float32)
        features[0, -1] = 1.0
        proba = model.probabilities(features)
        np.testing.assert_allclose([1.0, 1.0], proba.sum(axis=1), rtol=1e-6)
        self.assertEqual(0.0, proba[1, PUSH_CLASS])

    def test_load_round_trip_and_rejects_wrong_shape(self):
        fd, path = tempfile.mkstemp(suffix='.npz')
        os.close(fd)
        try:
            weights = np.random.default_rng(0).normal(size=(NR_CLASSES, NR_FEATURES)).astype(np.float32)
            np.savez(path, weights=weights, bias=np.zeros(NR_CLASSES), format_version=np.array(1))
            features = np.ones(NR_FEATURES, dtype=np.float32)
            np.testing.assert_allclose(features @ weights.T, TrumpModel.load(path).logits(features), rtol=1e-5)
        finally:
            os.remove(path)
        with self.assertRaises(ValueError):
            TrumpModel(np.zeros((6, NR_FEATURES)), np.zeros(6))

    @unittest.skipUnless(DEFAULT_MODEL_PATH.exists(), 'trained model not present')
    def test_shipped_model_returns_a_legal_action(self):
        model = TrumpModel.load()
        self.assertIn(model.action_trump(obs_with(forehand=-1)), [0, 1, 2, 3, 4, 5, PUSH])
        self.assertIn(model.action_trump(obs_with(forehand=0)), [0, 1, 2, 3, 4, 5])


if __name__ == '__main__':
    unittest.main()
