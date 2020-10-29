# HSLU
#
# Created by Ruedi Arnold on 16.01.2018
# Changed to use blueprint, Thomas Koller on 12.10.2018
# Changed to refactored jass-kit library
#

"""
Code for the Jass player web interface, i.e. the "web part" receiving requests and serving them accordingly.
This file handles requests like action_trump and action_play_card and delegates them to a one of the registered Jass
agents.
"""

import logging
from http import HTTPStatus

from flask import request, jsonify, Blueprint, current_app

from jass.game.const import card_strings
from jass.game.game_observation import GameObservation

JASS_PATH_PREFIX = '/jass/players/'
SELECT_TRUMP_PATH_PREFIX = '/action_trump'
PLAY_CARD_PATH_PREFIX = '/action_play_card'
SEND_INFO_PREFIX = '/game_info'

players = Blueprint(JASS_PATH_PREFIX, __name__)


@players.route('/<string:player_name>' + PLAY_CARD_PATH_PREFIX, methods=['POST'])
def action_play_card(player_name: str):
    """
    Takes a action_play_card request, validates its data and returns the card to play.
    Args:
        player_name: the name of the desired player
    Returns:
        the http response to answer the given request
    """
    # check if player registered at that name
    player = current_app.get_player_for_name(player_name)
    if player is None:
        logging.warning('player {} not found'.format(player_name))
        return jsonify(error='player not found'), HTTPStatus.BAD_REQUEST

    # check request type and parse data into a game observation
    if not request.is_json:
        logging.warning('request is not json')
        return jsonify(error='json data expected'), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    try:
        request_dict = request.get_json()
        obs = GameObservation.from_json(request_dict)
    except Exception as e:
        logging.warning('Error parsing request to GameObservation')
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST

    try:
        card = player.action_play_card(obs)
        # convert card from int to string
        data = dict(card=card_strings[card])
        return jsonify(data), HTTPStatus.OK
    except Exception as e:
        logging.warning('Error in action_play_card')
        return jsonify(error=str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


@players.route('/<string:player_name>' + SELECT_TRUMP_PATH_PREFIX, methods=['POST'])
def action_trump(player_name: str):
    """
    Takes a action_trump request, validates its data and returns the selected trump
    Args:
        player_name: the name of the desired player
    Returns:
        the http response to answer the given request

    """
    # check if player registered at that name

    player = current_app.get_player_for_name(player_name)
    if player is None:
        logging.warning('player {} not found'.format(player_name))
        return jsonify(error='player not found'), HTTPStatus.BAD_REQUEST

    # check request type and parse data into a game observation
    if not request.is_json:
        logging.warning('request is not json')
        return jsonify(error='json data expected'), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    try:
        request_dict = request.get_json()
        obs = GameObservation.from_json(request_dict)
    except Exception as e:
        logging.warning('Error parsing request to GameObservation')
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST

    try:
        trump = player.action_trump(obs)
        data = dict(trump=trump)
        return jsonify(data), HTTPStatus.OK
    except Exception as e:
        logging.warning('Error in action_trump: {}'.format(e))
        return jsonify(error=str(e)), HTTPStatus.INTERNAL_SERVER_ERROR


@players.route('/<string:player_name>' + SEND_INFO_PREFIX, methods=['POST'])
def game_info(player_name: str):
    """
    Receives a game info message about a current changes in the game, which does not require
    an action from the player.

    This might be used to inform a player about cards played by the other player or the result
    at the end of the game.

    Args:
        player_name: the name of the desired player
    Returns:
        the http response to answer the given request

    """
    # check if player registered at that name
    player = current_app.get_player_for_name(player_name)
    if player is None:
        logging.warning('player {} not found'.format(player_name))
        return jsonify(error='player not found'), HTTPStatus.BAD_REQUEST

    # check request type and parse data into a game observation
    if not request.is_json:
        logging.warning('request is not json')
        return jsonify(error='json data expected'), HTTPStatus.UNSUPPORTED_MEDIA_TYPE

    try:
        request_dict = request.get_json()
        _ = GameObservation.from_json(request_dict)
        # currently we dont do anything with the data
        return jsonify(''), HTTPStatus.OK
    except Exception as e:
        logging.warning('Error parsing request to GameObservation')
        return jsonify(error=str(e)), HTTPStatus.BAD_REQUEST


@players.route('/<string:player_name>', methods=['GET'])
def check_player(player_name: str):
    """
    Provides basic information about this player.

    Args:
        player_name:  the player name as provided in the request path.

    Returns:
        different strings depending on the player found
    """
    player = current_app.get_player_for_name(player_name)
    if player is not None:
        return jsonify('Player {} here'.format(player_name)), HTTPStatus.OK
    else:
        return jsonify('No such player {}'.format(player_name)), HTTPStatus.NOT_FOUND
