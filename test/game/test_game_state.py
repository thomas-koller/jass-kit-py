import copy
import json
import unittest
import numpy as np

from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.game.const import NORTH, PUSH
from jass.game.game_observation import GameObservation
from jass.game.game_sim import GameSim
from jass.game.game_state import GameState
from jass.game.game_state_util import observation_from_state, calculate_starting_hands_from_game, \
    state_from_complete_game, state_for_trump_from_complete_game, state_from_observation
from jass.game.game_util import deal_random_hand
from jass.game.rule_schieber import RuleSchieber


class MyTestCase(unittest.TestCase):
    def test_copy(self):
        game_state = GameState()
        game_state_shallow = copy.copy(game_state)
        game_state_deep = copy.deepcopy(game_state)

        self.assertEqual(-1, game_state_shallow.dealer)
        self.assertEqual(-1, game_state_deep.dealer)
        self.assertEqual(0, game_state_shallow.hands[0, 0])
        self.assertEqual(0, game_state_deep.hands[0, 0])

        # change dealer
        game_state.dealer = 1

        # values have not changes
        self.assertEqual(-1, game_state_shallow.dealer)
        self.assertEqual(-1, game_state_deep.dealer)

        # change value in numpy array
        game_state.hands[0, 0] = 1

        # shallow copy takes value from changed state
        self.assertEqual(1, game_state_shallow.hands[0, 0])

        # deep copy keeps value
        self.assertEqual(0, game_state_deep.hands[0, 0])

    def test_eq(self):
        game_sim = GameSim(rule=RuleSchieber())

        hands = deal_random_hand()

        game_sim.init_from_cards(hands, NORTH)

        game_state = game_sim.state
        game_state_shallow = copy.copy(game_state)
        game_state_deep = copy.deepcopy(game_state)

        self.assertTrue(game_state == game_state_shallow)
        self.assertTrue(game_state == game_state_deep)

    def test_to_from_json(self):
        # play a random match
        rule = RuleSchieber()
        game = GameSim(rule=rule)
        agent = AgentRandomSchieber()

        game.init_from_cards(hands=deal_random_hand(), dealer=NORTH)

        # Read/Write at start of match
        json_str = json.dumps(game.state.to_json())
        state_read = GameState.from_json(json.loads(json_str))
        self.assertTrue(game.state == state_read)
        # same for observation
        for i in range(4):
            obs = observation_from_state(game.state, player=i)
            json_str = json.dumps(obs.to_json())
            obs_read = GameObservation.from_json(json.loads(json_str))
            self.assertTrue(obs == obs_read)

        # start match with pushing for trump selection
        game.action_trump(PUSH)
        json_str = json.dumps(game.state.to_json())
        state_read = GameState.from_json(json.loads(json_str))
        self.assertTrue(game.state == state_read)
        # same for observation
        for i in range(4):
            obs = observation_from_state(game.state, player=i)
            json_str = json.dumps(obs.to_json())
            obs_read = GameObservation.from_json(json.loads(json_str))
            self.assertTrue(obs == obs_read)

        # use agent to select trump
        game.action_trump(agent.action_trump(game.get_observation()))
        json_str = json.dumps(game.state.to_json())
        state_read = GameState.from_json(json.loads(json_str))
        self.assertTrue(game.state == state_read)
        # same for observation
        for i in range(4):
            obs = observation_from_state(game.state, player=i)
            json_str = json.dumps(obs.to_json())
            obs_read = GameObservation.from_json(json.loads(json_str))
            self.assertTrue(obs == obs_read)

        while not game.is_done():
            game.action_play_card(agent.action_play_card(game.get_observation()))

            # write and read from state
            json_str = json.dumps(game.state.to_json())
            state_read = GameState.from_json(json.loads(json_str))
            self.assertTrue(game.state == state_read)

            # same for observation
            for i in range(4):
                obs = observation_from_state(game.state, player=i)
                json_str = json.dumps(obs.to_json())
                obs_read = GameObservation.from_json(json.loads(json_str))
                self.assertTrue(obs == obs_read)

    def test_from_complete_game(self):
        # play a random match
        rule = RuleSchieber()
        game = GameSim(rule=rule)
        agent = AgentRandomSchieber()

        hands_initial = deal_random_hand()

        game.init_from_cards(hands=hands_initial, dealer=NORTH)

        # select trump randomly
        state_trump_forehand = copy.deepcopy(game.state)
        action = agent.action_trump(game.get_observation())
        game.action_trump(action)

        state_trump_rearhand = None

        if action == PUSH:
            state_trump_rearhand = copy.deepcopy(game.state)
            action = agent.action_trump(game.get_observation())
            game.action_trump(action)

        states = []
        while not game.is_done():
            states.append(copy.deepcopy(game.state))
            game.action_play_card(agent.action_play_card(game.get_observation()))


        # calculate starting hands from complete games
        hands_calculated = calculate_starting_hands_from_game(game.state)
        self.assertTrue((hands_initial == hands_calculated).all())

        for c in range(36):
            state_calculated = state_from_complete_game(game.state, c)
            rule.assert_invariants(state_calculated)
            self.assertTrue(state_calculated == states[c])

        state_calculated_forehand = state_for_trump_from_complete_game(game.state, for_forhand=True)
        self.assertTrue(state_trump_forehand == state_calculated_forehand)

        if game.state.forehand == 0:
            state_calculated_rearhand = state_for_trump_from_complete_game(game.state, for_forhand=False)
            self.assertTrue(state_trump_rearhand == state_calculated_rearhand)

    def test_obs_state(self):
        # test convertion from state to obs and back

        # play a random match
        rule = RuleSchieber()
        game = GameSim(rule=rule)
        agent = AgentRandomSchieber()

        game.init_from_cards(hands=deal_random_hand(), dealer=NORTH)

        # start match with pushing for trump selection
        game.action_trump(PUSH)

        obs = observation_from_state(game.state, player=-1)
        state_back = state_from_observation(obs, game.state.hands)
        self.assertTrue(game.state == state_back)

        # use agent to select trump
        game.action_trump(agent.action_trump(game.get_observation()))
        obs = observation_from_state(game.state, player=-1)
        state_back = state_from_observation(obs, game.state.hands)
        self.assertTrue(game.state == state_back)

        while not game.is_done():
            game.action_play_card(agent.action_play_card(game.get_observation()))

            obs = observation_from_state(game.state, player=-1)
            state_back = state_from_observation(obs, game.state.hands)
            self.assertTrue(game.state == state_back)


if __name__ == '__main__':
    unittest.main()
