import unittest

from jass.agents.agent_cheating_random_schieber import AgentCheatingRandomSchieber
from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.arena.arena import Arena


class GameSimTestCase(unittest.TestCase):

    def test_arena_in_non_cheating_mode(self):
        # setup the arena
        arena = Arena(nr_games_to_play=1, cheating_mode=False, check_move_validity=True)
        player = AgentRandomSchieber()
        my_player = AgentRandomSchieber()

        arena.set_players(my_player, player, my_player, player)
        arena.play_all_games()

        self.assertEqual(arena.nr_games_played, 1)

    def test_arena_in_cheating_mode(self):
        # setup the arena
        arena = Arena(nr_games_to_play=1, cheating_mode=True, check_move_validity=True)
        player = AgentCheatingRandomSchieber()
        my_player = AgentCheatingRandomSchieber()

        arena.set_players(my_player, player, my_player, player)
        arena.play_all_games()

        self.assertEqual(arena.nr_games_played, 1)

    def test_arena_in_non_cheating_mode_exception(self):
        # setup the arena
        arena = Arena(nr_games_to_play=1, cheating_mode=False, check_move_validity=True)
        player = AgentCheatingRandomSchieber()
        my_player = AgentCheatingRandomSchieber()

        with self.assertRaises(AssertionError):
            arena.set_players(my_player, player, my_player, player)

    def test_arena_in_cheating_mode_exception(self):
        # setup the arena
        arena = Arena(nr_games_to_play=1, cheating_mode=True, check_move_validity=True)
        player = AgentRandomSchieber()
        my_player = AgentRandomSchieber()

        with self.assertRaises(AssertionError):
            arena.set_players(my_player, player, my_player, player)


if __name__ == '__main__':
    unittest.main()
