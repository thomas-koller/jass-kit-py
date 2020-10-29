# HSLU
#
# Created by Thomas Koller on 27.07.20
#
import logging
import sys
from datetime import datetime
from typing import List

import numpy as np

from jass.agents.agent import Agent
from jass.arena.dealing_card_random_strategy import DealingCardRandomStrategy
from jass.arena.dealing_card_strategy import DealingCardStrategy
from jass.game.const import NORTH, EAST, SOUTH, WEST, DIAMONDS, MAX_TRUMP, PUSH, next_player
from jass.game.game_observation import GameObservation
from jass.game.game_sim import GameSim
from jass.game.rule_schieber import RuleSchieber
from jass.logs.game_log_entry import GameLogEntry
from jass.logs.log_entry_file_generator import LogEntryFileGenerator


class Arena:
    """
    Class for arenas. An arena plays a number of games between two pairs of players. The number of
    games to be played can be specified. The arena keeps statistics of the games won by each side and also
    of the point difference when winning.

    The class uses some strategy and template methods patterns. Currently, this is only done for dealing cards.

    """

    def __init__(self,
                 nr_games_to_play: int,
                 dealing_card_strategy: DealingCardStrategy = None,
                 print_every_x_games: int = 5,
                 check_move_validity=True,
                 save_filename=None):
        """

        Args:
            nr_games_to_play: number of games in the arena
            dealing_card_strategy: strategy for dealing cards
            print_every_x_games: print results every x games
            check_move_validity: True if moves from the agents should be checked for validity
            save_filename: True if results should be save
        """
        self._logger = logging.getLogger(__name__)

        self._nr_games_played = 0
        self._nr_games_to_play = nr_games_to_play

        # the strategies
        if dealing_card_strategy is None:
            self._dealing_card_strategy = DealingCardRandomStrategy()
        else:
            self._dealing_card_strategy = dealing_card_strategy

        # the players
        self._players: List[Agent or None] = [None, None, None, None]

        # player ids to use in saved games (if written)
        self._player_ids: List[int] = [0, 0, 0, 0]

        # the current game that is being played
        self._game = GameSim(rule=RuleSchieber())

        # we store the points for each game
        self._points_team_0 = np.zeros(self._nr_games_to_play)
        self._points_team_1 = np.zeros(self._nr_games_to_play)

        # Print  progress
        self._print_every_x_games = print_every_x_games
        self._check_moves_validity = check_move_validity

        # Save file if enabled
        if save_filename is not None:
            self._save_games = True
            self._file_generator = LogEntryFileGenerator(basename=save_filename, max_entries=100000, shuffle=False)
        else:
            self._save_games = False

    @property
    def nr_games_to_play(self):
        return self._nr_games_to_play

        # We define properties for the individual players to set/get them easily by name

    @property
    def north(self) -> Agent:
        return self._players[NORTH]

    @north.setter
    def north(self, player: Agent):
        self._players[NORTH] = player

    @property
    def east(self) -> Agent:
        return self._players[EAST]

    @east.setter
    def east(self, player: Agent):
        self._players[EAST] = player

    @property
    def south(self) -> Agent:
        return self._players[SOUTH]

    @south.setter
    def south(self, player: Agent):
        self._players[SOUTH] = player

    @property
    def west(self) -> Agent:
        return self._players[WEST]

    @west.setter
    def west(self, player: Agent):
        self._players[WEST] = player

    @property
    def players(self):
        return self._players

    # properties for the results (no setters as the values are set by the strategies using the add_win_team_x methods)
    @property
    def nr_games_played(self):
        return self._nr_games_played

    @property
    def points_team_0(self):
        return self._points_team_0

    @property
    def points_team_1(self):
        return self._points_team_1

    def get_observation(self) -> GameObservation:
        """
        Creates and returns the observation for the current player

        Returns:
            the observation for the current player
        """
        return self._game.get_observation()

    def set_players(self, north: Agent, east: Agent, south: Agent, west: Agent,
                    north_id=0, east_id=0, south_id=0, west_id=0) -> None:
        """
        Set the players.
        Args:
            north: North player
            east: East player
            south: South player
            west: West player
            north_id: id to use for north in the save file
            east_id: id to use for east in the save file
            south_id: id to use for south in the save file
            west_id: id to use for west in the save file
        """
        self._players[NORTH] = north
        self._players[EAST] = east
        self._players[SOUTH] = south
        self._players[WEST] = west
        self._player_ids[NORTH] = north_id
        self._player_ids[EAST] = east_id
        self._player_ids[SOUTH] = south_id
        self._player_ids[WEST] = west_id

    def play_game(self, dealer: int) -> None:
        """
        Play a complete game (36 cards).
        """
        # init game
        self._game.init_from_cards(dealer=dealer, hands=self._dealing_card_strategy.deal_cards(
            game_nr=self._nr_games_played,
            total_nr_games=self._nr_games_to_play))

        # determine trump
        # ask first player
        trump_action = self._players[self._game.state.player].action_trump(self._game.get_observation())
        if trump_action < DIAMONDS or (trump_action > MAX_TRUMP and trump_action != PUSH):
            self._logger.error('Illegal trump (' + str(trump_action) + ') selected')
            raise RuntimeError('Illegal trump (' + str(trump_action) + ') selected')
        self._game.action_trump(trump_action)
        if trump_action == PUSH:
            # ask second player
            trump_action = self._players[self._game.state.player].action_trump(self._game.get_observation())
            if trump_action < DIAMONDS or trump_action > MAX_TRUMP:
                self._logger.error('Illegal trump (' + str(trump_action) + ') selected')
                raise RuntimeError('Illegal trump (' + str(trump_action) + ') selected')
            self._game.action_trump(trump_action)

        # play cards
        for cards in range(36):
            obs = self._game.get_observation()
            card_action = self._players[self._game.state.player].action_play_card(obs)
            if self._check_moves_validity:
                assert card_action in np.flatnonzero(self._game.rule.get_valid_cards_from_obs(obs)), \
                    'Invalid card played!'
            self._game.action_play_card(card_action)

        # update results
        self._points_team_0[self._nr_games_played] = self._game.state.points[0]
        self._points_team_1[self._nr_games_played] = self._game.state.points[1]
        self.save_game()

        self._nr_games_played += 1

    def save_game(self):
        """
        Save the current game if enabled.
        Returns:

        """
        if self._save_games:
            entry = GameLogEntry(game=self._game.state, date=datetime.now(), player_ids=self._player_ids)
            self._file_generator.add_entry(entry.to_json())

    def play_all_games(self):
        """
        Play the number of games.
        """
        if self._save_games:
            self._file_generator.__enter__()
        dealer = NORTH
        for game_id in range(self._nr_games_to_play):
            self.play_game(dealer=dealer)
            if self.nr_games_played % self._print_every_x_games == 0:
                points_to_write = int(self.nr_games_played / self._nr_games_to_play * 40)
                spaces_to_write = 40 - points_to_write
                sys.stdout.write("\r[{}{}] {:4}/{:4} games played".format('.' * points_to_write,
                                                                          ' ' * spaces_to_write,
                                                                          self.nr_games_played,
                                                                          self._nr_games_to_play))
            dealer = next_player[dealer]
        if self._save_games:
            self._file_generator.__exit__(None, None, None)
        sys.stdout.write('\n')
