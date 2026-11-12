"""
Measure whether one agent is stronger than another (exercise 6).

Every deal is fixed by (seed, deal number) and played twice, with agent A first at north/south and then at
east/west, so both sides hold the same cards once and the luck of the deal cancels exactly. The result per deal
is half the point difference of A over B summed over both games; the mean over deals comes with a 95% confidence
interval.

Agents are built by factories that take a seed, fresh for every game, so a result depends only on the factories,
the seed and the deal numbers, not on how the deals are split over worker processes. Factories must be picklable
(top level functions or functools.partial) when workers > 1.
"""
import math
import time
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Callable, List, Sequence, Tuple

import numpy as np

from jass.agents.agent import Agent
from jass.arena.dealing_card_seeded_strategy import DealingCardSeededStrategy
from jass.game.const import PUSH
from jass.game.game_sim import GameSim
from jass.game.rule_schieber import RuleSchieber

AgentFactory = Callable[[int], Agent]

NORTH_SOUTH, EAST_WEST = 0, 1


@dataclass
class Evaluation:
    """Result of A against B; diffs[i] is A's mean point advantage on deal i over both seatings."""
    diffs: np.ndarray
    points_a: float
    points_b: float
    seconds: float

    @property
    def deals(self) -> int:
        return len(self.diffs)

    @property
    def mean(self) -> float:
        return float(self.diffs.mean())

    @property
    def ci95(self) -> Tuple[float, float]:
        """Normal approximation, fine for the 100+ deals an evaluation should have."""
        if self.deals < 2:
            return float('nan'), float('nan')
        half_width = 1.96 * self.diffs.std(ddof=1) / math.sqrt(self.deals)
        return self.mean - half_width, self.mean + half_width

    @property
    def point_share(self) -> float:
        return self.points_a / (self.points_a + self.points_b)


def play_game(team_ns: Agent, team_ew: Agent, hands: np.ndarray, dealer: int) -> np.ndarray:
    """Play one game of 36 cards and return the points of north/south and east/west."""
    game = GameSim(rule=RuleSchieber())
    game.init_from_cards(hands=hands, dealer=dealer)

    def agent():
        return team_ns if game.state.player % 2 == NORTH_SOUTH else team_ew

    trump = agent().action_trump(game.get_observation())
    game.action_trump(trump)
    if trump == PUSH:
        game.action_trump(agent().action_trump(game.get_observation()))

    while not game.is_done():
        game.action_play_card(agent().action_play_card(game.get_observation()))
    return game.state.points.copy()


def play_deal(factory_a: AgentFactory, factory_b: AgentFactory, seed: int, deal_nr: int) -> Tuple[float, float]:
    """Play deal deal_nr with both seatings; return the total points of A and of B over the two games."""
    hands = DealingCardSeededStrategy(seed).deal_cards(game_nr=deal_nr)
    dealer = deal_nr % 4
    # distinct agent seeds for every game and team, derived from the deal only
    agent_seeds = np.random.SeedSequence([seed, deal_nr]).generate_state(4)

    a_first = play_game(factory_a(int(agent_seeds[0])), factory_b(int(agent_seeds[1])), hands, dealer)
    b_first = play_game(factory_b(int(agent_seeds[2])), factory_a(int(agent_seeds[3])), hands, dealer)
    points_a = a_first[NORTH_SOUTH] + b_first[EAST_WEST]
    points_b = a_first[EAST_WEST] + b_first[NORTH_SOUTH]
    return float(points_a), float(points_b)


def _play_deals(args) -> List[Tuple[float, float]]:
    factory_a, factory_b, seed, deal_nrs = args
    return [play_deal(factory_a, factory_b, seed, nr) for nr in deal_nrs]


def evaluate(factory_a: AgentFactory, factory_b: AgentFactory, deals: int, seed: int = 2026,
             workers: int = 1, first_deal: int = 0) -> Evaluation:
    """Play deals first_deal .. first_deal + deals - 1 for A against B, in parallel if workers > 1."""
    start = time.time()
    deal_nrs: Sequence[int] = range(first_deal, first_deal + deals)
    if workers <= 1:
        points = _play_deals((factory_a, factory_b, seed, deal_nrs))
    else:
        chunks = [deal_nrs[i::workers] for i in range(workers)]
        with ProcessPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(_play_deals, [(factory_a, factory_b, seed, c) for c in chunks]))
        # undo the round robin split so that points[i] belongs to deal_nrs[i]
        points = [None] * deals
        for worker, chunk_points in enumerate(results):
            points[worker::workers] = chunk_points

    points = np.array(points)
    return Evaluation(diffs=(points[:, 0] - points[:, 1]) / 2,
                      points_a=float(points[:, 0].sum()),
                      points_b=float(points[:, 1].sum()),
                      seconds=time.time() - start)
