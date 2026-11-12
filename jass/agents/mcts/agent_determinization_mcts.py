"""
Monte Carlo tree search agent for imperfect information by determinization: the unknown hands of the other players
are sampled repeatedly, each sample is searched as if it were the true state, and the visits of the cards are
summed over all samples.
"""
import logging
import math
import time
from typing import Optional

import numpy as np

from jass.agents.agent import Agent
from jass.agents.agent_rule_based_schieber import AgentRuleBasedSchieber
from jass.agents.mcts.mcts import MCTS, best_card
from jass.agents.mcts.sampling import sample_hands
from jass.agents.trump.trump_model import TrumpModel
from jass.game.game_observation import GameObservation
from jass.game.game_state_util import state_from_observation
from jass.game.rule_schieber import RuleSchieber


class AgentDeterminizationMCTS(Agent):
    """
    Select trump with the trained trump model if one is given, otherwise like the rule based agent, and play the
    card with the most visits summed over searches on sampled hands. If the search fails, the card of the rule
    based agent is played.
    """
    def __init__(self, time_budget: float = 1.0, iterations: Optional[int] = None, iterations_per_sample: int = 100,
                 c: float = math.sqrt(2), seed: Optional[int] = None, trump_model: Optional[TrumpModel] = None):
        """
        Args:
            trump_model: trained trump selection, None selects trump with the rule based agent
            time_budget: seconds of search for each card, a running sample is finished after the deadline
            iterations: total number of iterations for each card, replaces the time budget if given
            iterations_per_sample: number of iterations of the search on each sampled deal
            c: exploration parameter of UCB1
            seed: seed of the random number generator
        """
        self._logger = logging.getLogger(__name__)
        self._rule = RuleSchieber()
        self._time_budget = time_budget
        self._iterations = iterations
        self._iterations_per_sample = iterations_per_sample
        self._rng = np.random.default_rng(seed)
        self._mcts = MCTS(self._rule, self._rng, c=c)
        self._rule_based = AgentRuleBasedSchieber()
        self._trump_model = trump_model

    def action_trump(self, obs: GameObservation) -> int:
        if self._trump_model is not None:
            try:
                return self._trump_model.action_trump(obs)
            except Exception:
                self._logger.warning('Trump model failed, selecting trump like the rule based agent', exc_info=True)
        return self._rule_based.action_trump(obs)

    def action_play_card(self, obs: GameObservation) -> int:
        valid = np.flatnonzero(self._rule.get_valid_cards_from_obs(obs))
        if len(valid) == 1:
            return int(valid[0])
        try:
            totals = self._search(obs)
        except Exception:
            self._logger.warning('Search failed, playing the rule based card', exc_info=True)
            totals = {}
        if not totals:
            self._logger.warning('No search result, playing the rule based card')
            return self._rule_based.action_play_card(obs)
        return best_card(totals)

    def _search(self, obs: GameObservation) -> dict:
        deadline = time.perf_counter() + self._time_budget
        totals = {}
        nr_iterations = 0
        while True:
            state = state_from_observation(obs, sample_hands(obs, self._rng))
            # in time mode, the deadline also ends a running sample
            sample_deadline = None if self._iterations is not None else deadline
            for card, visits in self._mcts.search(state, iterations=self._iterations_per_sample,
                                                  deadline=sample_deadline).items():
                totals[card] = totals.get(card, 0) + visits
            nr_iterations += self._iterations_per_sample
            if self._iterations is not None:
                if nr_iterations >= self._iterations:
                    return totals
            elif time.perf_counter() >= deadline:
                return totals
