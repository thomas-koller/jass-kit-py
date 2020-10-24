import unittest
from datetime import datetime

from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.game.const import NORTH, PUSH
from jass.game.game_sim import GameSim
from jass.game.game_util import deal_random_hand
from jass.game.rule_schieber import RuleSchieber
from jass.logs.game_log_entry import GameLogEntry
from jass.logs.game_obs_action_log_entry import GameObsActionLogEntry


class GameLogTestCase(unittest.TestCase):
    def test_read_write(self):
        # play a random, complete match

        rule = RuleSchieber()
        game = GameSim(rule=rule)
        agent = AgentRandomSchieber()

        game.init_from_cards(hands=deal_random_hand(), dealer=NORTH)

        # start match with pushing for trump selection
        game.action_trump(PUSH)
        # use agent to select trump
        game.action_trump(agent.action_trump(game.get_observation()))

        while not game.is_done():
            obs = game.get_observation()
            action = agent.action_play_card(obs)

            # read/write observation
            now = datetime.now().replace(microsecond=0)
            log_entry = GameObsActionLogEntry(obs=obs, action=action, date=now, player_id=obs.player_view)
            data = log_entry.to_json()
            log_entry_read = GameObsActionLogEntry.from_json(data)
            self.assertTrue(log_entry == log_entry_read)

            game.action_play_card(action)

        # create log entry with the match

        # only create time with seconds resolution, as more is not saved
        now = datetime.now().replace(microsecond=0)
        log_entry = GameLogEntry(game=game.state, date=now, player_ids=[0, 1, 2, 3])
        log_entry.date.replace(microsecond=0)

        data = log_entry.to_json()
        log_entry_read = GameLogEntry.from_json(data)

        self.assertTrue(log_entry.game == log_entry_read.game)
        self.assertTrue(log_entry.date == log_entry_read.date)
        self.assertTrue(log_entry.player_ids == log_entry_read.player_ids)
        self.assertTrue(log_entry == log_entry_read)


if __name__ == '__main__':
    unittest.main()
