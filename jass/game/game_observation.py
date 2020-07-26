# HSLU
#
# Created by Thomas Koller on 7/24/2020
#
import numpy as np


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