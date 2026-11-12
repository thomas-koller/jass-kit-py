"""
Numpy-only trump model for the bot, reading the weights exported by jass.train.trump.train.
"""
import os
from pathlib import Path

import numpy as np

from jass.agents.trump.features import FOREHAND_INDEX, NR_CLASSES, NR_FEATURES, PUSH_CLASS, class_to_action, \
    obs_to_trump_features
from jass.game.game_observation import GameObservation

FORMAT_VERSION = 1

# the model in the source tree; set JASS_TRUMP_MODEL when the package is installed elsewhere (e.g. in docker)
MODEL_PATH_ENV = 'JASS_TRUMP_MODEL'
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[3] / 'models' / 'trump_linear.npz'


def default_model_path() -> Path:
    return Path(os.environ.get(MODEL_PATH_ENV, DEFAULT_MODEL_PATH))


class TrumpModel:
    """Linear softmax model: logits = features @ weights.T + bias, one logit per class 0..6."""

    def __init__(self, weights: np.ndarray, bias: np.ndarray):
        if weights.shape != (NR_CLASSES, NR_FEATURES) or bias.shape != (NR_CLASSES,):
            raise ValueError('Expected weights {} and bias {}, got {} and {}'.format(
                (NR_CLASSES, NR_FEATURES), (NR_CLASSES,), weights.shape, bias.shape))
        self._weights = weights.astype(np.float32)
        self._bias = bias.astype(np.float32)

    @classmethod
    def load(cls, path=None) -> 'TrumpModel':
        """Load exported weights from path, by default from default_model_path()."""
        path = default_model_path() if path is None else path
        with np.load(path) as data:
            version = int(data['format_version'])
            if version != FORMAT_VERSION:
                raise ValueError('Unsupported trump model format {} in {}'.format(version, path))
            return cls(data['weights'], data['bias'])

    def logits(self, features: np.ndarray) -> np.ndarray:
        """Logits for one feature vector (37,) or a batch (n, 37); push is -inf where it is not allowed."""
        logits = features @ self._weights.T + self._bias
        not_allowed = features[..., FOREHAND_INDEX] == 0
        logits[..., PUSH_CLASS] = np.where(not_allowed, -np.inf, logits[..., PUSH_CLASS])
        return logits

    def probabilities(self, features: np.ndarray) -> np.ndarray:
        logits = self.logits(features)
        exp = np.exp(logits - logits.max(axis=-1, keepdims=True))
        return exp / exp.sum(axis=-1, keepdims=True)

    def action_trump(self, obs: GameObservation) -> int:
        """The trump action for the game: 0..5, or PUSH."""
        return class_to_action(int(np.argmax(self.logits(obs_to_trump_features(obs)))))
