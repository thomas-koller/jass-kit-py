# HSLU
#
# Created by Thomas Koller on 7/23/2020
#
import numpy as np


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
        self.nr_tricks = 0

        # the number of card in the current trick
        self.nr_cards_in_trick = 0

        # the total number of played cards (derived)
        self.nr_played_cards = 0

        self.points = np.zeros(shape=2, dtype=np.int32)

    def __eq__(self, other: 'GameState') -> bool:
        if self.nr_played_cards == 36:
            assert self.current_trick is None
            assert other.current_trick is None
            current_tricks_same = True
        else:
            current_tricks_same = (self.current_trick == other.current_trick).all()
        return self.dealer == other.dealer and \
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

