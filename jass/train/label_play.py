# HSLU
#
# Created by Thomas Koller on 19.07.19
#
import logging

import numpy as np

from jass.game.game_util import convert_one_hot_encoded_cards_to_str_encoded_list, get_cards_encoded_from_str


class LabelPlay:
    """
    Class to define (possible) training information for a specific action in the game when it is in the playing
    stage (i.e. not in the trump defining stage).

    This includes the card played, the points made in the current trick by the own team and the other, the player who
    won the trick, the points made in the round by the own team and the other and the hands the players had at the
    beginning of the game.

    (Adding both the points for own and opposite team for the points in the trick eliminates needing to know the
    current player. Adding the information about the exact winner (instead of the team) might help to forecast the
    result of the trick)

    """
    def __init__(self,
                 card_played: int,
                 points_in_trick_own: int,
                 points_in_trick_other: int,
                 trick_winner: int,
                 points_in_round_own: int,
                 points_in_round_other: int,
                 hands: np.ndarray):
        self.card_played = card_played
        self.points_in_trick_own = points_in_trick_own
        self.points_in_trick_other = points_in_trick_other
        self.trick_winner = trick_winner
        self.points_in_round_own = points_in_round_own
        self.points_in_round_other = points_in_round_other
        self.hands = hands
        
    def to_json(self) -> dict: 
        """
        Convert to json
        Returns:
            dict that can be serialized to json
        """
        return dict(
            card_played=int(self.card_played),
            points_in_trick_own=int(self.points_in_trick_own),
            points_in_trick_other=int(self.points_in_trick_other),
            trick_winner=int(self.trick_winner),
            points_in_round_own=int(self.points_in_round_own),
            points_in_round_other=int(self.points_in_round_other),
            hands_player_0=convert_one_hot_encoded_cards_to_str_encoded_list(self.hands[0, :]),
            hands_player_1=convert_one_hot_encoded_cards_to_str_encoded_list(self.hands[1, :]),
            hands_player_2=convert_one_hot_encoded_cards_to_str_encoded_list(self.hands[2, :]),
            hands_player_3=convert_one_hot_encoded_cards_to_str_encoded_list(self.hands[3, :])
        )

    @classmethod
    def from_json(cls, data):
        """
        Create label from dict (from json)
        Args:
            data: dict representation
        Returns:
            label from the data
        """
        hands = np.zeros(shape=[4, 36], dtype=np.int32)
        try:
            hands[0, :] = get_cards_encoded_from_str(data['hands_player_0'])
            hands[1, :] = get_cards_encoded_from_str(data['hands_player_1'])
            hands[2, :] = get_cards_encoded_from_str(data['hands_player_2'])
            hands[3, :] = get_cards_encoded_from_str(data['hands_player_3'])
        except KeyError as e:
            logging.getLogger(__name__).error('Key error: {}, data: {}'.format(e, data))
            raise e

        return LabelPlay(card_played=data['card_played'],
                         points_in_trick_own=data['points_in_trick_own'],
                         points_in_trick_other=data['points_in_trick_other'],
                         trick_winner=data['trick_winner'],
                         points_in_round_own=data['points_in_round_own'],
                         points_in_round_other=data['points_in_round_other'],
                         hands=hands)

