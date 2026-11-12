import os
import tempfile
import unittest

import numpy as np

from jass.agents.trump.features import PUSH_CLASS, FOREHAND_INDEX
from jass.train.trump.data import load_trump_csv


def row(cards, can_push, user, label):
    """Build a csv row; the csv stores the push flag inverted (0 = may push)."""
    hand = [0] * 36
    for c in cards:
        hand[c] = 1
    return ','.join(str(v) for v in hand + [0 if can_push else 1, user, label])


class LoadTrumpCsvTestCase(unittest.TestCase):
    NINE = list(range(9))

    def setUp(self):
        rows = [
            row(self.NINE, 1, 11, 1),        # hearts
            row(self.NINE, 1, 12, 10),       # push, old encoding
            row(self.NINE, 0, 13, 6),        # push without forehand -> dropped
            row(list(range(8)), 1, 14, 2),   # only 8 cards -> dropped
            row(self.NINE, 0, 15, 4),        # obe-abe
        ]
        fd, self.path = tempfile.mkstemp(suffix='.csv')
        with os.fdopen(fd, 'w') as f:
            f.write('\n'.join(rows) + '\n')

    def tearDown(self):
        os.remove(self.path)

    def test_loads_and_filters_illegal_rows(self):
        data = load_trump_csv(self.path)
        self.assertEqual((3, 37), data.X.shape)
        np.testing.assert_array_equal([1, PUSH_CLASS, 4], data.y)
        np.testing.assert_array_equal([11, 12, 15], data.users)
        self.assertEqual(np.float32, data.X.dtype)
        np.testing.assert_array_equal([1, 1, 0], data.X[:, FOREHAND_INDEX])


if __name__ == '__main__':
    unittest.main()
