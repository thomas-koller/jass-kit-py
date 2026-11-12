import time
import unittest
from unittest import mock

import numpy as np

from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.agents.agent_rule_based_schieber import AgentRuleBasedSchieber
from jass.agents.mcts.agent_determinization_mcts import AgentDeterminizationMCTS
from jass.agents.mcts.mcts import MCTS
from jass.arena.arena import Arena
from jass.game.const import PUSH, SPADES
from jass.game.game_state_util import observation_from_state
from jass.game.rule_schieber import RuleSchieber
from .positions import random_observation
from .test_agent_cheating_mcts import dealt_state
from ..test_agent_rule_based_schieber import observation


class AgentDeterminizationMCTSTestCase(unittest.TestCase):

    def test_trump_like_rule_based(self):
        agent = AgentDeterminizationMCTS(iterations=10, seed=0)
        rule_based = AgentRuleBasedSchieber()
        for seed in range(20):
            state = dealt_state(seed)
            obs = observation_from_state(state, state.player)
            self.assertEqual(agent.action_trump(obs), rule_based.action_trump(obs))

    def test_trump_after_push_is_not_push(self):
        obs = observation(['D7', 'D8', 'H6', 'H8', 'S7', 'SQ', 'C9', 'C7', 'C10'], forehand=0)
        self.assertNotEqual(AgentDeterminizationMCTS(iterations=10, seed=0).action_trump(obs), PUSH)

    def test_trump_from_model_when_given(self):
        model = mock.Mock()
        model.action_trump.return_value = SPADES
        agent = AgentDeterminizationMCTS(iterations=10, seed=0, trump_model=model)
        obs = observation(['D7', 'D8', 'H6', 'H8', 'S7', 'SQ', 'C9', 'C7', 'C10'])
        self.assertEqual(SPADES, agent.action_trump(obs))
        model.action_trump.assert_called_once_with(obs)

    def test_trump_falls_back_to_rule_based_when_model_fails(self):
        model = mock.Mock()
        model.action_trump.side_effect = RuntimeError('broken model')
        agent = AgentDeterminizationMCTS(iterations=10, seed=0, trump_model=model)
        obs = observation(['D7', 'D8', 'H6', 'H8', 'S7', 'SQ', 'C9', 'C7', 'C10'])
        self.assertEqual(AgentRuleBasedSchieber().action_trump(obs), agent.action_trump(obs))

    def test_valid_cards_in_random_positions(self):
        rule = RuleSchieber()
        for seed in range(200):
            obs = random_observation(seed, seed % 36)
            agent = AgentDeterminizationMCTS(iterations=40, iterations_per_sample=20, seed=seed)
            self.assertIn(agent.action_play_card(obs), np.flatnonzero(rule.get_valid_cards_from_obs(obs)))

    def test_respects_time_budget(self):
        obs = random_observation(0, 0)
        agent = AgentDeterminizationMCTS(time_budget=0.3, seed=0)
        start = time.perf_counter()
        agent.action_play_card(obs)
        self.assertLess(time.perf_counter() - start, 0.8)

    def test_deadline_applies_within_a_sample(self):
        obs = random_observation(0, 0)
        agent = AgentDeterminizationMCTS(time_budget=0.3, iterations_per_sample=10 ** 6, seed=0)
        start = time.perf_counter()
        card = agent.action_play_card(obs)
        self.assertLess(time.perf_counter() - start, 0.6)
        self.assertIn(card, np.flatnonzero(RuleSchieber().get_valid_cards_from_obs(obs)))

    def test_fallback_on_error(self):
        obs = random_observation(6, 4)
        with mock.patch.object(MCTS, 'search', side_effect=RuntimeError('broken')):
            with self.assertLogs('jass.agents.mcts.agent_determinization_mcts', level='WARNING'):
                card = AgentDeterminizationMCTS(iterations=40, seed=0).action_play_card(obs)
        self.assertEqual(card, AgentRuleBasedSchieber().action_play_card(obs))

    def test_reproducible(self):
        obs = random_observation(9, 10)
        cards = [AgentDeterminizationMCTS(iterations=200, seed=3).action_play_card(obs) for _ in range(2)]
        self.assertEqual(cards[0], cards[1])

    def test_beats_random_in_arena(self):
        np.random.seed(1)
        arena = Arena(nr_games_to_play=20, print_every_x_games=100)
        mcts = AgentDeterminizationMCTS(iterations=50, iterations_per_sample=25, seed=1)
        arena.set_players(mcts, AgentRandomSchieber(), mcts, AgentRandomSchieber())
        arena.play_all_games()
        self.assertGreater(arena.points_team_0.sum(), arena.points_team_1.sum())


if __name__ == '__main__':
    unittest.main()
