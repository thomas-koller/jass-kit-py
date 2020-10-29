# HSLU
#
# Created by Thomas Koller on 7/30/2020
#
import logging

import requests

from jass.agents.agent import Agent
from jass.agents.agent_random_schieber import AgentRandomSchieber
from jass.game.const import card_ids
from jass.game.game_observation import GameObservation
from jass.service.player_service_route import SEND_INFO_PREFIX, SELECT_TRUMP_PATH_PREFIX, PLAY_CARD_PATH_PREFIX


class AgentByNetwork(Agent):
    """
    Forwards the request to a player service. Used for locally playing against deployed services.

    A random agent is used as standing player, if the service does not answer within a timeout.
    """

    def __init__(self, url, timeout=10):
        self._logger = logging.getLogger(__name__)
        self._standin_player = AgentRandomSchieber()
        self._base_url = url
        self._url_info = self._base_url + SEND_INFO_PREFIX
        self._url_trump = self._base_url + SELECT_TRUMP_PATH_PREFIX
        self._url_play = self._base_url + PLAY_CARD_PATH_PREFIX
        self._timeout = timeout

    def action_trump(self, obs: GameObservation) -> int:
        data = obs.to_json()
        data['gameId'] = 0
        # noinspection PyBroadException
        try:
            self._logger.info('Sending request...')
            response = requests.post(self._url_trump, json=data, timeout=self._timeout)
            response_data = response.json()
            self._logger.info('got response: {}'.format(response_data))
            trump = int(response_data['trump'])
            return trump
        except Exception:
            self._logger.error('No response from network player, using standin player')
            return self._standin_player.action_trump(obs)

    # noinspection PyBroadException
    def action_play_card(self, obs: GameObservation) -> int:
        data = obs.to_json()
        data['gameId'] = 0
        try:
            self._logger.info('Sending request...')
            response = requests.post(self._url_play, json=data, timeout=self._timeout)
            response_data = response.json()
            self._logger.info('got response: {}'.format(response_data))
            card = response_data['card']
            card_id = card_ids[card]
            return card_id
        except Exception:
            self._logger.error('No response from network player, using standin player')
            return self._standin_player.action_play_card(obs)
