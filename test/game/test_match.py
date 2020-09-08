import unittest
import json
import datetime

from jass.game.match import JassMatch
from jass.game.game_state import GameState


class MatchestCase(unittest.TestCase):
    def test_match(self):
        game_string = '{"trump":5,"dealer":3,"tss":1,"tricks":[' \
                       '{"cards":["C7","CK","C6","CJ"],"points":17,"win":0,"first":2},' \
                       '{"cards":["S7","SJ","SA","C10"],"points":12,"win":0,"first":0},' \
                       '{"cards":["S9","S6","SQ","D10"],"points":24,"win":3,"first":0},' \
                       '{"cards":["H10","HJ","H6","HQ"],"points":26,"win":1,"first":3},' \
                       '{"cards":["H7","DA","H8","C9"],"points":8,"win":1,"first":1},' \
                       '{"cards":["H9","CA","HA","DJ"],"points":2,"win":1,"first":1},' \
                       '{"cards":["HK","S8","SK","CQ"],"points":19,"win":1,"first":1},' \
                       '{"cards":["DQ","D6","D9","DK"],"points":18,"win":0,"first":1},' \
                       '{"cards":["S10","D7","C8","D8"],"points":31,"win":0,"first":0}],' \
                       '"player":[{"hand":[]},{"hand":[]},{"hand":[]},{"hand":[]}],"jassTyp":"SCHIEBER_2500"}'
        state = GameState.from_json(json.loads(game_string))

        match = JassMatch()
        match.set_players('north', 'east', 'south', 'west')
        self.assertEqual('north', match.north)
        self.assertEqual('east', match.east)
        self.assertEqual('south', match.south)
        self.assertEqual('west', match.west)

        match.time_started = datetime.datetime.now()

        match.add_game(state)
        self.assertEqual(1, match.nr_games)

        match.add_game(state)
        self.assertEqual(2, match.nr_games)

        match.time_finished = datetime.datetime.now()

        match.winner = 1

        match.add_error('Error: There was an error')
        match.add_error('Error: and another')

        # test __eq__
        self.assertTrue(match == match)

    def test_parser_generator(self):
        game_string = '{"trump":5,"dealer":3,"tss":1,"tricks":[' \
                       '{"cards":["C7","CK","C6","CJ"],"points":17,"win":0,"first":2},' \
                       '{"cards":["S7","SJ","SA","C10"],"points":12,"win":0,"first":0},' \
                       '{"cards":["S9","S6","SQ","D10"],"points":24,"win":3,"first":0},' \
                       '{"cards":["H10","HJ","H6","HQ"],"points":26,"win":1,"first":3},' \
                       '{"cards":["H7","DA","H8","C9"],"points":8,"win":1,"first":1},' \
                       '{"cards":["H9","CA","HA","DJ"],"points":2,"win":1,"first":1},' \
                       '{"cards":["HK","S8","SK","CQ"],"points":19,"win":1,"first":1},' \
                       '{"cards":["DQ","D6","D9","DK"],"points":18,"win":0,"first":1},' \
                       '{"cards":["S10","D7","C8","D8"],"points":31,"win":0,"first":0}],' \
                       '"player":[{"hand":[]},{"hand":[]},{"hand":[]},{"hand":[]}],"jassTyp":"SCHIEBER_2500"}'
        state = GameState.from_json(json.loads(game_string))

        match = JassMatch()

        match.set_players('north', 'east', 'south', 'west')
        match.add_game(state)
        match.add_game(state)
        match.winner = 0

        match.add_error('Error: There was an error')
        match.add_error('Error: and another')

        data = match.to_json()
        match_restored = JassMatch.from_json(data)

        self.assertTrue(match, match_restored)


if __name__ == '__main__':
    unittest.main()
