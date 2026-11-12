import unittest

import numpy as np

from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.agents.agent_rule_based_schieber import AgentRuleBasedSchieber
from jass.arena.evaluation import evaluate, play_deal


# top level factories, so they can be pickled for worker processes
def rule_based(seed):
    return AgentRuleBasedSchieber()


def random_agent(seed):
    return AgentRandomSchieber(seed=seed)


class EvaluationTestCase(unittest.TestCase):

    def test_agent_against_itself_is_exactly_even(self):
        # deterministic agent: swapping the seats must cancel the cards exactly
        result = evaluate(rule_based, rule_based, deals=20, seed=1)
        np.testing.assert_array_equal(np.zeros(20), result.diffs)
        self.assertEqual(0.5, result.point_share)

    def test_every_deal_distributes_all_points(self):
        points_a, points_b = play_deal(rule_based, random_agent, seed=1, deal_nr=3)
        # two games of 157 points each, plus 100 for each match (all tricks) that happened
        self.assertEqual(0, (points_a + points_b - 2 * 157) % 100)

    def test_rule_based_beats_random(self):
        result = evaluate(rule_based, random_agent, deals=60, seed=1)
        low, high = result.ci95
        self.assertGreater(low, 0)
        self.assertLess(low, result.mean)
        self.assertLess(result.mean, high)

    def test_result_is_reproducible_and_independent_of_workers(self):
        serial = evaluate(random_agent, rule_based, deals=12, seed=5, workers=1)
        again = evaluate(random_agent, rule_based, deals=12, seed=5, workers=1)
        parallel = evaluate(random_agent, rule_based, deals=12, seed=5, workers=3)
        np.testing.assert_array_equal(serial.diffs, again.diffs)
        np.testing.assert_array_equal(serial.diffs, parallel.diffs)

    def test_different_seeds_give_different_deals(self):
        a = evaluate(random_agent, rule_based, deals=10, seed=1)
        b = evaluate(random_agent, rule_based, deals=10, seed=2)
        self.assertFalse(np.array_equal(a.diffs, b.diffs))


if __name__ == '__main__':
    unittest.main()
