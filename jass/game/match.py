# HSLU
#
# Created by Thomas Koller on 24.08.18
#
from jass.game.game_state import GameState

from jass.game.const import NORTH, EAST, SOUTH, WEST


class JassMatch:
    """
    A match consists of a number of (full) games that are played between 4 players.

    (Most of the logic and the available data is based on GameSim. The match is primarily used to store and load
    games that are played on the server. For that reason it is now extended to support the urls of the players
    and error that occurred while playing.
    """

    def __init__(self):
        self._players = ['', '', '', '']                # type: [str]
        self._urls = ['', '', '', '']                   # type: [str]
        self._player_ids = ['', '', '', '']             # type: [str]
        self._games = []                                # type: [GameState]
        self._points_team0 = 0                          # type: int
        self._points_team1 = 0                          # type: int
        self._winner = -1                               # type: int

        # time is not set by default, as the match can also be created by reading from db
        self._time_started = None
        self._time_finished = None

        # errors will be a list of str messages about possible errors while playing a match on the server
        # such as timeout or connection problems
        self._errors = []

    def __eq__(self, other: 'JassMatch'):
        """
        Compare two instances. Useful for tests when the representations are encoded and decoded. The objects are
        considered equal if they have the same properties. As the games contain numpy arrays, we can not compare
        dict directly.
        Args:
            other: the other object to compare to.

        Returns:
            True if the objects are the same.
        """
        result = \
            self._players == other._players and \
            self.points_team0 == other.points_team0 and \
            self.points_team1 == other.points_team1 and \
            self.time_started == other.time_started and \
            self.time_finished == other.time_finished and \
            self.errors == other.errors

        if not result:
            return False

        for i in range(self.nr_games):
            if not self._games[i] == other._games[i]:
                return False

        return True

    # Read only properties
    @property
    def points_team0(self) -> int:
        return self._points_team0

    @property
    def points_team1(self) -> int:
        return self._points_team1

    @property
    def round(self) -> [GameState]:
        return self._games

    @property
    def errors(self) -> [str]:
        return self._errors

    # Derived properties
    @property
    def nr_games(self) -> int:
        return len(self._games)

    # Read / Write properties
    @property
    def north(self) -> str:
        return self._players[NORTH]

    @north.setter
    def north(self, player: str):
        self._players[NORTH] = player

    @property
    def east(self) -> str:
        return self._players[EAST]

    @east.setter
    def east(self, player: str):
        self._players[EAST] = player

    @property
    def south(self) -> str:
        return self._players[SOUTH]

    @south.setter
    def south(self, player: str):
        self._players[SOUTH] = player

    @property
    def west(self) -> str:
        return self._players[WEST]

    @west.setter
    def west(self, player: str):
        self._players[WEST] = player

    @property
    def north_url(self) -> str:
        return self._urls[NORTH]

    @north_url.setter
    def north_url(self, url: str):
        self._urls[NORTH] = url

    @property
    def east_url(self) -> str:
        return self._urls[EAST]

    @east_url.setter
    def east_url(self, url: str):
        self._urls[EAST] = url

    @property
    def south_url(self) -> str:
        return self._urls[SOUTH]

    @south_url.setter
    def south_url(self, url: str):
        self._urls[SOUTH] = url

    @property
    def west_url(self) -> str:
        return self._urls[WEST]

    @west_url.setter
    def west_url(self, url: str):
        self._urls[WEST] = url

    @property
    def north_id(self):
        return self._player_ids[NORTH]

    @property
    def east_id(self):
        return self._player_ids[EAST]

    @property
    def south_id(self):
        return self._player_ids[SOUTH]

    @property
    def west_id(self):
        return self._player_ids[WEST]

    @property
    def winner(self) -> int:
        return self._winner

    @winner.setter
    def winner(self, value: int):
        self._winner = value

    @property
    def time_started(self):
        return self._time_started

    @time_started.setter
    def time_started(self, value):
        self._time_started = value

    @property
    def time_finished(self):
        return self._time_finished

    @time_finished.setter
    def time_finished(self, value):
        self._time_finished = value

    def set_players(self, north: str, east: str, south: str, west: str) -> None:
        """
        Set the players.
        Args:
            north: North player
            east: East player
            south: South player
            west: West player
        """
        self._players[NORTH] = north
        self._players[EAST] = east
        self._players[SOUTH] = south
        self._players[WEST] = west

    def set_urls(self, north_url: str, east_url: str, south_url: str, west_url: str) -> None:
        """
        Set the players.
        Args:
           north_url: url of north player
           east_url: url of east player
           south_url: url of south player
           west_url: url of west player
        """
        self._urls[NORTH] = north_url
        self._urls[EAST] = east_url
        self._urls[SOUTH] = south_url
        self._urls[WEST] = west_url

    def set_player_ids(self, north_id: str, east_id: str, south_id: str, west_id: str) -> None:
        """
        Set the players.
        Args:
           north_id: id of north player
           east_id: id of east player
           south_id: id of south player
           west_id: id of west player
        """
        self._player_ids[NORTH] = north_id
        self._player_ids[EAST] = east_id
        self._player_ids[SOUTH] = south_id
        self._player_ids[WEST] = west_id

    def add_game(self, game: GameState) -> None:
        """
        Add a game to the match. The points are adjusted from the game.
        Args:
            game: state of completed game to add

        """
        self._games.append(game)
        self._points_team0 += int(game.points[0])
        self._points_team1 += int(game.points[1])

    def add_error(self, error: str) -> None:
        """
        Add an error message.
        Args:
            error: Error message to add
        """
        self._errors.append(error)

    def to_json(self):
        """
        Generate a dict representation that can be converted to json.


        Returns:
            dict representation of the state
        """

        data = dict()
        data['north'] = self.north
        data['east'] = self.east
        data['south'] = self.south
        data['west'] = self.west
        data['northUrl'] = self.north_url
        data['eastUrl'] = self.east_url
        data['southUrl'] = self.south_url
        data['westUrl'] = self.west_url
        data['northId'] = self.north_id
        data['eastId'] = self.east_id
        data['southId'] = self.south_id
        data['westId'] = self.west_id
        data['winner'] = self.winner
        data['pointsTeam0'] = int(self.points_team0)
        data['pointsTeam1'] = int(self.points_team1)
        data['timeStarted'] = self.time_started
        data['timeFinished'] = self.time_finished

        if self.errors:
            data['errors'] = self.errors

        games = []
        for i in range(self.nr_games):
            game_data = self._games[i].to_json()
            games.append(game_data)
        data['games'] = games
        return data

    @classmethod
    def from_json(cls, data: dict):
        """
        Create match from dict (read from json)
        """
        match = JassMatch()

        match.set_players(data['north'], data['east'], data['south'], data['west'])
        match.winner = data['winner']
        match._points_team0 = data['pointsTeam0']
        match._points_team1 = data['pointsTeam1']
        match.time_started = data['timeStarted']
        match.time_finished = data['timeFinished']

        if 'errors' in data:
            match._errors = data['errors']

        games = data['games']

        games_read = []

        for game_data in games:
            game = GameState.from_json(game_data)
            games_read.append(game)

        match._games = games_read
        return match
