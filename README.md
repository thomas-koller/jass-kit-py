# jass-kit-py

Base components to program agents for the game of
[Jass](https://en.wikipedia.org/wiki/Jass) (Schieber): the rules, the game
state, the observation a player has of it, an arena to let agents play against
each other, and a service to make an agent available over the network.

This package is intentionally small and has no machine learning dependencies -
numpy is all it needs. Writing an agent means implementing two methods.

## Installation

```bash
pip install -e .                 # the game
pip install -e '.[service]'      # additionally flask, to serve an agent
```

## Writing an agent

Derive from `Agent` and implement the two decisions of a Schieber game:

```python
import numpy as np
from jass.agents.agent import Agent
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.game.const import PUSH, DIAMONDS


class MyAgent(Agent):
    def __init__(self):
        self._rule = RuleSchieber()
        self._rng = np.random.default_rng()

    def action_trump(self, obs: GameObservation) -> int:
        # obs.forehand == -1 means we are the forehand and may push
        if obs.forehand == -1 and self._rng.random() < 0.5:
            return PUSH
        return DIAMONDS

    def action_play_card(self, obs: GameObservation) -> int:
        # only ever play a card the rules allow
        valid_cards = self._rule.get_valid_cards_from_obs(obs)
        return int(self._rng.choice(np.flatnonzero(valid_cards)))
```

`AgentRandomSchieber` is a complete random agent to compare against, and
`examples/arena/arena_play.py` shows a simple heuristic agent.
`AgentRuleBasedSchieber` is a stronger baseline that plays by rules of thumb:
it scores its hand for each trump (and pushes weak hands), pulls trumps when
its team declared, cashes sure winners, gives points to a partner who wins the
trick and otherwise wins cheaply or discards its least valuable card. Against
the random agent it makes about 68% of the points.

`jass.agents.mcts` contains Monte Carlo tree search players that choose trump
like the rule based agent. `AgentCheatingMCTS` searches the complete game state
and is a reference point for what perfect information is worth.
`AgentDeterminizationMCTS` only uses its observation: it repeatedly samples the
hands of the other players (respecting the colors they are known to be out
of), searches each sample and plays the card with the most visits over all
samples. It searches for `time_budget` seconds per card (default 1) and falls
back to the rule based card if the search fails. The service serves it as
`mcts`, and as `mcts_ml` with the trained trump model of `jass.agents.trump`.

`examples/arena/evaluate.py` measures one agent against others with
`jass.arena.evaluation`: fixed deals, each played from both sides, reported as
the mean point difference per deal with a 95% confidence interval and logged to
`results/evaluations.jsonl`.

The two methods return **encoded integers**, described below. Returning an
invalid card is an error; `get_valid_cards_from_obs` tells you which cards are
allowed, and using it is the easiest way to be correct.

### What the agent sees

`GameObservation` is the game **from one player's point of view**: their own
hand, the tricks played so far, who dealt, what trump is, how many points each
team has. It deliberately does not contain the other players' hands.

`GameState` is the complete state including all four hands. An agent that gets
it would be cheating, which is why it is a separate class and why cheating
agents derive from `AgentCheating` instead. Such agents are useful as an upper
bound on how well one could play, not as opponents.

## Letting agents play

```python
from jass.arena.arena import Arena

arena = Arena(nr_games_to_play=1000)
arena.set_players(my_agent, opponent, my_agent, opponent)   # north, east, south, west
arena.play_all_games()
print(arena.points_team_0.sum(), arena.points_team_1.sum())
```

Partners sit across from each other: north and south are team 0, east and west
are team 1. 157 points are distributed per game, so a result is usually reported
as a percentage of 157.

## Serving an agent over the network

`jass.service` wraps agents in a flask application, which is how they are
deployed and how the online platform reaches them:

```python
from jass.service.player_service_app import PlayerServiceApp

app = PlayerServiceApp('my_service')
app.add_player('my_agent', MyAgent())
# flask run --host=0.0.0.0 --port=8888
```

See `examples/service/player_service.py`. `AgentByNetwork` is the counterpart: an
agent that forwards the decisions to such a service, so a remote agent can play
in a local arena.

The `Dockerfile` packages that service; every push to `master` publishes it to
`ghcr.io/sili-dev/jass-kit-py`. `deploy/umbrel` describes running it on an
Umbrel server with Arcane and automatic updates.

## Encodings

Getting these wrong is the most common source of confusion.

**Cards** are 0..35, grouped by suit and descending by rank within a suit:

| Range | Suit | |
| --- | --- | --- |
| 0..8 | diamonds | DA, DK, DQ, DJ, D10, D9, D8, D7, D6 |
| 9..17 | hearts | HA .. H6 |
| 18..26 | spades | SA .. S6 |
| 27..35 | clubs | CA .. C6 |

A hand is a one-hot array of 36 entries, not a list of card numbers.
`jass.game.game_util` converts between the representations
(`convert_one_hot_encoded_cards_to_str_encoded_list` and friends).

**Trump** is 0..5: diamonds, hearts, spades, clubs, obenabe (4), unenufe (5).

**Push** is the constant `PUSH`, which is *not* 6 - use the constant. It may only
be returned when `obs.forehand == -1`, that is when you are the forehand player
and the decision has not been passed to you already.

**Players** are north 0, east 1, south 2, west 3, and play goes
counter-clockwise, so `next_player[NORTH]` is west. The `next_player` and
`partner_player` tables in `jass.game.const` avoid arithmetic mistakes here.

## Contents

| Package | Content |
| --- | --- |
| `jass.game` | State, observation, rules (`RuleSchieber`), the simulation (`GameSim`), constants and conversion helpers |
| `jass.agents` | The `Agent` and `AgentCheating` interfaces, random, rule based and MCTS agents, `AgentByNetwork` |
| `jass.arena` | Playing many games between agents, with card dealing strategies (random or seeded) |
| `jass.service` | Flask application to serve agents over REST |
| `jass.logs` | Reading and writing logged games |

`Overview.md` and the `*.puml` files hold class diagrams of the game classes.

## Tests

```bash
python -m unittest discover -s test -p "*test*.py"
```

## Related repositories

This package is the base; machine learning, training and evaluation live
elsewhere. See
[jass-docs](https://github.com/thomas-koller/jass-docs) for the overview.
Note that this package stays deliberately free of those dependencies, so that
writing an agent needs nothing but numpy.
