"""
Feature encoding for trump selection, shared by training and by the agent at runtime.

The layout matches the Swisslos trump data set: 36 one-hot cards in the order of jass.game.const
(DA..D6, HA..H6, SA..S6, CA..C6), followed by one forehand flag that is 1 when the player may still push.
"""
import numpy as np

from jass.game.const import PUSH, PUSH_ALT
from jass.game.game_observation import GameObservation

NR_FEATURES = 37
FOREHAND_INDEX = 36

# model classes: 0..5 are the trump modes of jass.game.const, 6 is push
NR_CLASSES = 7
PUSH_CLASS = 6


def trump_features(hand: np.ndarray, can_push: bool) -> np.ndarray:
    """Encode a one-hot hand of 36 cards and the push flag as a float vector of length 37."""
    features = np.zeros(NR_FEATURES, dtype=np.float32)
    features[:36] = hand
    features[FOREHAND_INDEX] = 1.0 if can_push else 0.0
    return features


def obs_to_trump_features(obs: GameObservation) -> np.ndarray:
    """Encode the observation of the player who has to choose trump (forehand == -1 means push is allowed)."""
    return trump_features(obs.hand, can_push=obs.forehand == -1)


def label_to_class(label: int) -> int:
    """Map a trump label from the data (0..5, 6 or 10 for push) to a model class 0..6."""
    return PUSH_CLASS if label in (PUSH, PUSH_ALT) else int(label)


def class_to_action(cls: int) -> int:
    """Map a model class 0..6 back to the trump action the game expects (push is PUSH = 10)."""
    return PUSH if cls == PUSH_CLASS else int(cls)
