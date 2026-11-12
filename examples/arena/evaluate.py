"""
Compare an agent with a set of opponents on fixed deals, each played from both sides (exercise 6).

    python examples/arena/evaluate.py --agent mcts_ml --against mcts --deals 200
    python examples/arena/evaluate.py --agent mcts                    # against the reference set

MCTS agents search a fixed number of iterations per card (not a time budget), so results do not depend on the
machine or the number of workers. Every result is appended to results/evaluations.jsonl together with the
configuration and git commit, so experiments stay comparable.
"""
import argparse
import functools
import json
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.agents.agent_rule_based_schieber import AgentRuleBasedSchieber
from jass.agents.mcts.agent_determinization_mcts import AgentDeterminizationMCTS
from jass.agents.trump.trump_model import TrumpModel
from jass.arena.evaluation import evaluate

REFERENCE_OPPONENTS = ['random', 'rule_based']
REPO = Path(__file__).resolve().parents[2]


# agent builders: top level so that they can be pickled for the worker processes

def build_random(seed, iterations):
    return AgentRandomSchieber(seed=seed)


def build_rule_based(seed, iterations):
    return AgentRuleBasedSchieber()


@functools.lru_cache(maxsize=None)
def trump_model() -> TrumpModel:
    """Loaded once per worker process."""
    return TrumpModel.load()


def build_mcts(seed, iterations):
    return AgentDeterminizationMCTS(iterations=iterations, seed=seed)


def build_mcts_ml(seed, iterations):
    return AgentDeterminizationMCTS(iterations=iterations, seed=seed, trump_model=trump_model())


AGENTS = {
    'random': build_random,
    'rule_based': build_rule_based,
    'mcts': build_mcts,
    'mcts_ml': build_mcts_ml,
}


def git_commit() -> str:
    """Commit of the code that produced the result, with '+dirty' if there are uncommitted changes."""
    try:
        commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=REPO, capture_output=True,
                                text=True, check=True).stdout.strip()
        dirty = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=REPO,
                               capture_output=True, text=True, check=True).stdout.strip()
        return commit + ('+dirty' if dirty else '')
    except (OSError, subprocess.CalledProcessError):
        return 'unknown'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--agent', choices=sorted(AGENTS), required=True)
    parser.add_argument('--against', nargs='+', choices=sorted(AGENTS), default=REFERENCE_OPPONENTS)
    parser.add_argument('--deals', type=int, default=200, help='each deal is played twice, once from each side')
    parser.add_argument('--iterations', type=int, default=400, help='MCTS iterations per card')
    parser.add_argument('--seed', type=int, default=2026, help='fixes the deals; keep it for comparable runs')
    parser.add_argument('--workers', type=int, default=os.cpu_count())
    parser.add_argument('--out', type=Path, default=REPO / 'results' / 'evaluations.jsonl')
    parser.add_argument('--no-save', action='store_true', help='only print, do not append to --out')
    args = parser.parse_args()
    logging.basicConfig(level=logging.WARNING)

    commit = git_commit()
    agent = functools.partial(AGENTS[args.agent], iterations=args.iterations)
    for name in args.against:
        opponent = functools.partial(AGENTS[name], iterations=args.iterations)
        result = evaluate(agent, opponent, deals=args.deals, seed=args.seed, workers=args.workers)
        low, high = result.ci95
        verdict = 'better' if low > 0 else 'worse' if high < 0 else 'no significant difference'
        print('{} vs {}: {:+.1f} points per deal (95% CI {:+.1f} .. {:+.1f}), share {:.1%}, {} deals, {:.0f}s -> {}'
              .format(args.agent, name, result.mean, low, high, result.point_share, result.deals,
                      result.seconds, verdict))

        if not args.no_save:
            record = dict(time=datetime.now().isoformat(timespec='seconds'), commit=commit,
                          agent=args.agent, opponent=name, iterations=args.iterations, seed=args.seed,
                          deals=result.deals, mean=round(result.mean, 2), ci_low=round(low, 2),
                          ci_high=round(high, 2), point_share=round(result.point_share, 4),
                          seconds=round(result.seconds, 1))
            args.out.parent.mkdir(parents=True, exist_ok=True)
            with open(args.out, 'a') as f:
                f.write(json.dumps(record) + '\n')


if __name__ == '__main__':
    main()
