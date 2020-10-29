# HSLU
#
# Created by Thomas Koller on 7/23/2020
#
import logging
import numpy as np

from jass.game.const import JASS_SCHIEBER, partner_player, next_player, card_ids
from jass.game.game_util import convert_int_encoded_cards_to_str_encoded, \
    convert_one_hot_encoded_cards_to_str_encoded_list, convert_str_encoded_cards_to_int_encoded


class GameState:
    """
    State of the game.

     A GameState object captures the information in the following stages of the game:
    - Cards have been dealt, but no trump is selected yet
    - The first player that is allowed to choose trump has passed this right to the partner (optional)
    - Trump has been declared by either player from the team that declares trump, but no card has been played yet
    - Between 1 and 35 cards have been played
    - The last card has been played, which is the end of the game.

    The class captures only the data without any logic how to change the data consistently.
    """

    # version of game state
    FORMAT_VERSION = 'V0.2'

    def __init__(self) -> None:
        """
        Initialize the class. All numpy arrays will be allocated.
        """
        # dealer of the game
        self.dealer: int = -1

        # player of the next action, i.e. declaring trump or playing a card
        self.player: int = -1

        # selected trump
        self.trump: int = -1

        # true (1) if trump was declared forehand, 0 if it was declared rearhand, -1 if it has not been declared yet
        self.forehand: int = -1

        # the player, who declared trump (derived)
        self.declared_trump: int = -1

        #
        # information about held and played cards
        #

        # the current hands of all the players, 1-hot encoded
        self.hands = np.zeros(shape=[4, 36], dtype=np.int32)

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
        self.nr_tricks: int = 0

        # the number of card in the current trick
        self.nr_cards_in_trick: int = 0

        # the total number of played cards (derived)
        self.nr_played_cards: int = 0

        self.points = np.zeros(shape=2, dtype=np.int32)

    def __eq__(self, other: 'GameState') -> bool:
        if self.nr_played_cards == 36:
            assert self.current_trick is None
            assert other.current_trick is None
            current_tricks_same = True
        else:
            # noinspection PyUnresolvedReferences
            current_tricks_same = (self.current_trick == other.current_trick).all()
        return \
            self.dealer == other.dealer and \
            self.player == other.player and \
            self.trump == other.trump and \
            self.forehand == other.forehand and \
            self.declared_trump == other.declared_trump and \
            (self.hands == other.hands).all() and \
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
        GameObservation.

        Returns:
            dict representation of the state
        """
        data = dict()

        # change of version: trump and player are always written, even as -1 if they are not known yet
        data['version'] = GameState.FORMAT_VERSION
        data['trump'] = int(self.trump)
        data['dealer'] = int(self.dealer)
        data['currentPlayer'] = int(self.player)
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
        for player in range(4):
            hand = dict(hand=convert_one_hot_encoded_cards_to_str_encoded_list(self.hands[player]))
            player_data[player] = hand
            data['player'] = player_data

        data['jassTyp'] = JASS_SCHIEBER
        return data

    def get_card_played(self, card_nr: int) -> int:
        """
        Get the card played at a certain time. Utility method.

        Returns:
            the card that was played as the card_nr card in the game
        """
        nr_trick, card_in_trick = divmod(card_nr, 4)
        return int(self.tricks[nr_trick, card_in_trick])

    @classmethod
    def from_json(cls, data: dict):
        """
        Create state from dict (read from json)
        """
        state = GameState()

        # if the version is present, it must be the correct version
        # if it is not there we accept the data for backward compatibility and in the future will assume this
        # version number if absent
        if 'version' in data:
            if data['version'] != GameState.FORMAT_VERSION:
                logging.getLogger(__name__).error('Unexpected format version: {}'.format(data['version']))
                return None

        # not currently used
        # jass_typ = data['jassTyp']

        state.dealer = data['dealer']

        if 'currentPlayer' in data:
            state.player = data['currentPlayer']
        else:
            state.player = -1

        if 'trump' in data:
            state.trump = data['trump']
        else:
            state.trump = -1

        # version 0.2 handling
        if 'forehand' in data:
            state.forehand = data['forehand']
        # previous version handling
        else:
            if 'tss' in data and data['tss'] == 1:
                state.forehand = 0
            elif state.trump != -1:
                # only set if trump has been declared
                state.forehand = 1
            else:
                # beginning of the game, when trump has not been set yet
                state.forehand = -1

        if state.trump != -1:
            if state.forehand == 1:
                state.declared_trump = next_player[state.dealer]
            else:
                state.declared_trump = partner_player[next_player[state.dealer]]

        tricks = data['tricks']
        for i, trick in enumerate(tricks):
            # list of strings in the trick
            if 'cards' in trick:
                cards = trick['cards']
                state.nr_played_cards += len(cards)

                # convert to list of ids
                cards_in_trick = convert_str_encoded_cards_to_int_encoded(cards)
                # append -1 if trick is not complete
                while len(cards_in_trick) < 4:
                    cards_in_trick.append(-1)

                state.tricks[i] = np.array(cards_in_trick)
            if 'win' in trick:
                state.trick_winner[i] = trick['win']
            if 'points' in trick:
                state.trick_points[i] = trick['points']
            # first must be present for all tricks
            if 'first' in trick:
                state.trick_first_player[i] = trick['first']
            else:
                logging.getLogger(__name__).error('No first player set in trick {}'.format(i))

        state.nr_tricks, state.nr_cards_in_trick = divmod(state.nr_played_cards, 4)

        # current trick points to the correct trick
        if state.nr_played_cards != 36:
            state.current_trick = state.tricks[state.nr_tricks]
        else:
            state.current_trick = None

        for i, player_data in enumerate(data['player']):
            if 'hand' in player_data and len(player_data['hand']) > 0:
                hand = player_data['hand']
                for card_constant in hand:
                    state.hands[i, card_ids[card_constant]] = 1

        state.points[0] = 0
        state.points[1] = 0
        for trick in range(state.nr_tricks):
            if state.trick_winner[trick] == 0 or state.trick_winner[trick] == 2:
                state.points[0] += state.trick_points[trick]
            else:
                state.points[1] += state.trick_points[trick]
        return state
