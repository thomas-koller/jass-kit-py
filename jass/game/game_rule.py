# HSLU
#
# Created by Thomas Koller on 7/24/2020
#
import numpy as np

from jass.game.game_observation import GameObservation
from jass.game.game_state import GameState


class GameRule:
    """
    Class for implementing rules of the jass match. The class includes rules that depend not on the process (like
    how trump is determined), but only upon cards. Currently this includes to determine the valid cards to play
    in a trick, to determine the winner of a trick and the points of a trick.

    This in an abstract base class that defines the interface.
    """

    def get_valid_cards(self, hand: np.array,
                        current_trick: np.ndarray or list,
                        move_nr: int,
                        trump: int or None) -> np.array:
        """
        Get the valid cards that can be played by the current player.

        Args:
            hand: one-hot encoded array of hands owned by the player
            current_trick: array with the indices of the cards for the previous moves in the current trick
            move_nr: which move the player has to make in the current trick, 0 for first move, 1 for second and so on
            trump: trump color (if used by the rule)

        Returns:
            one-hot encoded array of valid moves
        """
        raise NotImplementedError()

    def get_valid_cards_from_state(self, state: GameState):
        """
        Get the valid cards from the state for the current player.
        Args:
            state: The current state of the match
        Returns:
            one-hot encoded array of valid cards to play
        """
        return self.get_valid_cards(state.hands[state.player, :],
                                    state.current_trick,
                                    state.nr_cards_in_trick,
                                    state.trump)

    def get_valid_cards_from_obs(self, obs: GameObservation):
        """
        Get the valid cards from the observation.

        Precondition:
            The observation must be from the player whose turn it is too play (obs.player == obs.player_view)
        Args:
            obs: Observation of the match from players point of view
        Returns:
            one-hot encoded array of valid cards to play
        """
        return self.get_valid_cards(obs.hand,
                                    obs.current_trick,
                                    obs.nr_cards_in_trick,
                                    obs.trump)

    def calc_points(self, trick: np.ndarray, is_last: bool, trump: int = -1) -> int:
        """
        Calculate the points from the cards in the trick. Must be implemented in subclass

        Args:
            trick: the trick
            is_last: true if this is the last trick
            trump: the trump for the round (if needed by the rules)
        """
        raise NotImplementedError

    def calc_winner(self, trick: np.ndarray, first_player: int, trump: int = -1) -> int:
        """
        Calculate the winner of a completed trick. Must be implemented in subclass.

        Precondition:
            0 <= trick[i] <= 35, for i = 0..3
        Args:
            trick: the completed trick
            first_player: the first player of the trick
            trump: the trump for the round (if needed by the rules)

        Returns:
            the player who won this trick
        """
        raise NotImplementedError

    def assert_invariants(self, state: GameState) -> None:
        """
        Validates the internal consistency of the state according to the rules and throws an assertion exception if an
        error is detected.
        """
        raise NotImplementedError

