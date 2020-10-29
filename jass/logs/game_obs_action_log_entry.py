# HSLU
#
# Created by Thomas Koller on 7/31/2020
#
from datetime import datetime

from jass.game.const import DATE_FORMAT
from jass.game.game_observation import GameObservation


class GameObsActionLogEntry:
    """
    Write logs containing the game observation for a single player and the action. The action could either be
    a trump action or a play card action (or combined).

    Date and player_id information is added so that entries could be filtered by player.
    """
    def __init__(self, obs: GameObservation, action: int, date: datetime, player_id: int):
        self.obs = obs
        self.action = action
        self.date = date
        self.player_id = player_id

    def __eq__(self, other: 'GameObsActionLogEntry'):
        return \
            self.obs == other.obs and \
            self.action == other.action and \
            self.date == other.date and \
            self.player_id == other.player_id

    def to_json(self) -> dict:
        """
        Convert to dict (for json)
        Returns:
            dict representation
        """
        return dict(obs=self.obs.to_json(),
                    action=self.action,
                    date=datetime.strftime(self.date, DATE_FORMAT),
                    player_id=self.player_id)

    @classmethod
    def from_json(cls, data: dict) -> 'GameObsActionLogEntry':
        """
        Convert data from dict to GameObsActionLogEntry
        Args:
            data: dict containing the serialized GameObsActionLogEntry
        Returns:
            GameObsActionLogEntry
        """
        return GameObsActionLogEntry(obs=GameObservation.from_json(data['obs']),
                                     action=int(data['action']),
                                     date=datetime.strptime(data['date'], DATE_FORMAT),
                                     player_id=int(data['player_id']))
