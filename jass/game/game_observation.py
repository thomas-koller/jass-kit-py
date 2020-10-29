# HSLU
#
# Created by Thomas Koller on 7/24/2020
#
import logging

import numpy as np

from jass.game.const import JASS_SCHIEBER, next_player, partner_player, card_ids
from jass.game.game_util import convert_int_encoded_cards_to_str_encoded, \
    convert_one_hot_encoded_cards_to_str_encoded_list, convert_str_encoded_cards_to_int_encoded


class GameObservation:
    """
    Observation of the state of the game from a player's view. This is the same as the GameState, except that
    a player does not see the hands (cards) of the other players:
        - the dealer
        - the player that declared trump,
        - the trump chosen
        - trump was declared forehand (derived information)
        - the tricks that have been played so far
        - the winner and the first player (derived) of each trick
        - the number of points that have been made by the current jass_players team in this round
        - the number of points that have been made by the opponent team in this round
        - the number of cards played in the current trick
        - the cards played in the current trick
        - the current player
        - the hand of the player

     Similarly to game state, the GameObservation captures the information in the following stages of the game:
    - Cards have been dealt, but no trump is selected yet (and it is the player's turn to select trump)
    - The first player that is allowed to choose trump has passed this right to the partner, and it is the
    partners player's turn to select trump
    - Trump has been declared by either player from the team that declares trump, but no card has been played yet
    - Between 1 and 35 cards have been played

    The observation is usually from the point of view of the current player, but can also be from the point of view
    of another players. In that case, the hand array are the cards of that player. In order to distinguish between
    these cases, the variable GameObservation.player_view is used.
    """

    # version of game observation (in json)
    FORMAT_VERSION = 'V0.2'

    def __init__(self) -> None:
        """
        Initialize the class. All numpy arrays will be allocated.
        """
        # dealer of the game
        self.dealer: int = -1

        # player of the next action, i.e. declaring trump or playing a card. T
        self.player: int = -1

        # player for which this observation is
        self.player_view = -1

        # selected trump
        self.trump: int = -1

        # true (1) if trump was declared forehand, 0 if it was declared rearhand, -1 if it has not been declared yet
        self.forehand: int = -1

        # the player, who declared trump (derived)
        self.declared_trump: int = -1

        #
        # information about held and played cards
        #

        # the hand cards of the player, 1-hot encoded
        self.hand = np.zeros(shape=36, dtype=np.int32)

        # the tricks played so far, with the cards of the tricks int encoded in the order they are played
        # a value of -1 indicates that the card has not been played yet
        self.tricks = np.full(shape=[9, 4], fill_value=-1, dtype=np.int32)

        # the winner of the tricks
        self.trick_winner = np.full(shape=9, fill_value=-1, dtype=np.int32)

        # the points made in the tricks
        self.trick_points = np.zeros(shape=9, dtype=np.int32)

        # the first player of the trick (derived)
        self.trick_first_player = np.full(shape=9, fill_value=-1, dtype=np.int32)

        # the current trick is a view onto self.trick
        self.current_trick = self.tricks[0, :]

        # the number of completed tricks
        self.nr_tricks = 0

        # the number of card in the current trick
        self.nr_cards_in_trick = 0

        # the total number of played cards (derived)
        self.nr_played_cards = 0

        self.points = np.zeros(shape=2, dtype=np.int32)

    # noinspection PyUnresolvedReferences
    def __eq__(self, other: 'GameObservation') -> bool:
        if self.nr_played_cards == 36:
            assert self.current_trick is None
            assert other.current_trick is None
            current_tricks_same = True
        else:
            current_tricks_same = (self.current_trick == other.current_trick).all()
        return \
            self.dealer == other.dealer and \
            self.player == other.player and \
            self.player_view == other.player_view and \
            self.trump == other.trump and \
            self.forehand == other.forehand and \
            self.declared_trump == other.declared_trump and \
            (self.hand == other.hand).all() and \
            (self.tricks == other.tricks).all() and \
            (self.trick_first_player == other.trick_first_player).all() and \
            (self.trick_winner == other.trick_winner).all() and \
            (self.trick_points == other.trick_points).all() and \
            self.nr_tricks == other.nr_tricks and \
            current_tricks_same and \
            self.nr_cards_in_trick == other.nr_cards_in_trick and \
            self.nr_played_cards == other.nr_played_cards and \
            (self.points == other.points).all()

    def __repr__(self):
        return str(self.__dict__)

    def to_json(self):
        """
        Generate a dict representation that can be converted to json. The format is the same than used in
        GameState.

        Returns:
            dict representation of the state
        """
        data = dict()

        # change of version: trump and player are always written, even as -1 if they are not known yet
        data['version'] = GameObservation.FORMAT_VERSION
        data['trump'] = int(self.trump)
        data['dealer'] = int(self.dealer)
        data['currentPlayer'] = int(self.player)
        data['playerView'] = int(self.player_view)
        data['forehand'] = int(self.forehand)

        # played tricks
        tricks = []

        # tricks
        for i in range(min(self.nr_tricks + 1, 9)):
            # add at most one more trick as finished (for first player)
            trick = {}
            # add cards (if not empty)
            cards = convert_int_encoded_cards_to_str_encoded(self.tricks[i, :].tolist())
            if len(cards) > 0:
                trick['cards'] = cards
                if len(cards) == 4:
                    # only add points and winners for complete tricks
                    trick['points'] = int(self.trick_points[i])
                    trick['win'] = int(self.trick_winner[i])

            if self.trick_first_player[i] != -1:
                trick['first'] = int(self.trick_first_player[i])
            if trick:
                # add if not empty dict
                tricks.append(trick)

        data['tricks'] = tricks

        # cards in the hand of the players (empty if no more cards)
        hand_empty = dict(hand=[])
        player_data = [hand_empty, hand_empty, hand_empty, hand_empty]
        hand = dict(hand=convert_one_hot_encoded_cards_to_str_encoded_list(self.hand))
        player_data[self.player_view] = hand
        data['player'] = player_data

        data['jassTyp'] = JASS_SCHIEBER
        return data

    @classmethod
    def from_json(cls, data: dict):
        """
        Create observation from dict (read from json)
        """
        obs = GameObservation()

        # version must be present for observation data
        if 'version' not in data:
            logging.getLogger(__name__).error('no version information')
            return None

        if data['version'] != GameObservation.FORMAT_VERSION:
            logging.getLogger(__name__).error('Unexpected format version: {}'.format(data['version']))
            return None

        # not currently used
        # jass_typ = data['jassTyp']

        obs.dealer = data['dealer']
        obs.player = data['currentPlayer']
        obs.player_view = data['playerView']
        obs.trump = data['trump']
        obs.forehand = data['forehand']

        if obs.trump != -1:
            if obs.forehand == 1:
                obs.declared_trump = next_player[obs.dealer]
            else:
                obs.declared_trump = partner_player[next_player[obs.dealer]]

        tricks = data['tricks']
        for i, trick in enumerate(tricks):
            # list of strings in the trick
            if 'cards' in trick:
                cards = trick['cards']
                obs.nr_played_cards += len(cards)

                # convert to list of ids
                cards_in_trick = convert_str_encoded_cards_to_int_encoded(cards)
                # append -1 if trick is not complete
                while len(cards_in_trick) < 4:
                    cards_in_trick.append(-1)

                obs.tricks[i] = np.array(cards_in_trick)
            if 'win' in trick:
                obs.trick_winner[i] = trick['win']
            if 'points' in trick:
                obs.trick_points[i] = trick['points']
            # first must be present for all tricks
            if 'first' in trick:
                obs.trick_first_player[i] = trick['first']
            else:
                logging.getLogger(__name__).error('No first player set in trick {}'.format(i))

        obs.nr_tricks, obs.nr_cards_in_trick = divmod(obs.nr_played_cards, 4)

        # current trick points to the correct trick
        if obs.nr_played_cards != 36:
            obs.current_trick = obs.tricks[obs.nr_tricks]
        else:
            obs.current_trick = None

        for i, player_data in enumerate(data['player']):
            if 'hand' in player_data and len(player_data['hand']) > 0:
                if i != obs.player_view:
                    logging.getLogger(__name__).error('Hand data for wrong player {}'.format(i))
                hand = player_data['hand']
                for card_constant in hand:
                    obs.hand[card_ids[card_constant]] = 1

        obs.points[0] = 0
        obs.points[1] = 0
        for trick in range(obs.nr_tricks):
            if obs.trick_winner[trick] == 0 or obs.trick_winner[trick] == 2:
                obs.points[0] += obs.trick_points[trick]
            else:
                obs.points[1] += obs.trick_points[trick]
        return obs
