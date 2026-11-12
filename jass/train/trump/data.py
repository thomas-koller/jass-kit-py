"""
Load the Swisslos trump data set (e.g. 2018_10_18_trump.csv) into arrays for training.

Each row: 36 one-hot cards, flag (0 = may push, 1 = after push), user id, trump label (0..5, 6 or 10 for push).
Needs pandas, which is only a training dependency.
"""
import logging
from typing import NamedTuple, Optional

import numpy as np
import pandas as pd

from jass.agents.trump.features import NR_FEATURES, FOREHAND_INDEX, PUSH_CLASS, label_to_class

_logger = logging.getLogger(__name__)

USER_COLUMN = 37
LABEL_COLUMN = 38


class TrumpData(NamedTuple):
    X: np.ndarray      # (n, 37) float32, layout of jass.agents.trump.features
    y: np.ndarray      # (n,) int64, model classes 0..6
    users: np.ndarray  # (n,) int64, Swisslos user id, for grouped splits or filtering by player strength


def load_trump_csv(path, nrows: Optional[int] = None) -> TrumpData:
    """Read the csv and drop rows that are not a legal trump decision."""
    raw = pd.read_csv(path, header=None, nrows=nrows).to_numpy(dtype=np.int64)

    X = raw[:, :NR_FEATURES].astype(np.float32)
    # The csv flag is 0 when the player may push (forehand) and 1 after the partner pushed, despite the
    # notebook calling it "forehand yes = 1": every push in the data has flag 0. Flip it to our layout.
    X[:, FOREHAND_INDEX] = 1.0 - X[:, FOREHAND_INDEX]
    y =np.array([label_to_class(label) for label in raw[:, LABEL_COLUMN]], dtype=np.int64)
    users = raw[:, USER_COLUMN]

    nine_cards = X[:, :36].sum(axis=1) == 9
    # a push is only allowed for forehand; anything else is a logging error
    legal_push = (y != PUSH_CLASS) | (X[:, FOREHAND_INDEX] == 1)
    keep = nine_cards & legal_push
    if not keep.all():
        _logger.warning('Dropped %d of %d rows (not 9 cards: %d, push without forehand: %d)',
                        (~keep).sum(), len(keep), (~nine_cards).sum(), (~legal_push).sum())

    return TrumpData(X[keep], y[keep], users[keep])
