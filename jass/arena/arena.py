# HSLU
#
# Created by Thomas Koller on 27.07.20
#
from typing import List

from jass.arena.dealing_card_random_strategy import DealingCardRandomStrategy
from jass.arena.trump_selection_strategy import TrumpStrategy
from jass.arena.dealing_card_strategy import DealingCardStrategy


class Arena:
    """
    Class for arenas. An arena plays a number of games between two pairs of players. The number of
    games to be played can be specified. The arena keeps statistics of the games won by each side and also
    of the point difference when winning.

    The class uses the strategy and template methods patterns. Most common behaviour can be modified by using the
    appropriate strategies.

    """

    def __init__(self,
                 nr_games: int,
                 trump_strategy: TrumpStrategy,
                 dealing_card_strategy: DealingCardStrategy=None,
                 print_every_x_games: int = 5,
                 check_move_validity=True,
                 save_filename=None):
        """

        Args:
            nr_games: number of games in the arena
            trump_strategy: strategy for trump selection
            dealing_card_strategy: strategy for dealing cards
            print_every_x_games: print results every x games
            check_move_validity: True if moves from the agents should be checked for validity
            save_filename: True if results should be save
        """
        self._nr_games_to_play = nr_games

        # the strategies
        self._trump_strategy = trump_strategy
        if dealing_card_strategy is None:
            self._dealing_card_strategy = DealingCardRandomStrategy()
        else:
            self._dealing_card_strategy = dealing_card_strategy

        # the players
        self._players = [None, None, None, None]  # type: List[Player]

        # player ids to use in saved games (if written)
        self._player_ids = [0, 0, 0, 0]  # type: List[int]

        # the current round that is being played
        self._game = None  # type: Round

        # Statistics about the games played
        self._nr_wins_team_0 = 0  # type: int
        self._nr_wins_team_1 = 0  # type: int
        self._nr_draws = 0  # type: int
        self._nr_games_played = 0  # type: int
        self._delta_points = 0  # type: int

        # we store the points for each game, if there is more than one
        self._points_team_0 = np.zeros(1, dtype=np.int)
        self._points_team_1 = np.zeros(1, dtype=np.int)

        # Print  progress
        self._print_every_x_games = print_every_x_games
        self._play_card_strat: Callable[[int], None] = self._play_card_checked if check_move_validity else self._play_card_unchecked

        # Save file if enabled
        if save_filename is not None:
            self._save_rounds = True
            self._file_generator = RoundLogEntryFileGenerator(basename=save_filename, max_entries=100000)
        else:
            self._save_rounds = False