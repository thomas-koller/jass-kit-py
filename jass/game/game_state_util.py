# HSLU
#
# Created by Thomas Koller on 7/24/2020
#
import numpy as np

from jass.game.const import next_player, partner_player
from jass.game.game_observation import GameObservation
from jass.game.game_state import GameState


def calculate_starting_hands_from_game(game: GameState) -> np.ndarray:
    """
    Calculate the hands of the players at the beginning of the game from a completed game.
    Args:
        game: state of a completed game

    Returns:
        array with hand cards of each player

    """
    hands = np.zeros(shape=[4, 36], dtype=np.int32)
    for rnd_nr in range(0, 9):
        player = game.trick_first_player[rnd_nr]
        for card_nr in range(4):
            card_played = game.tricks[rnd_nr, card_nr]
            hands[player, card_played] = 1
            player = next_player[player]
    return hands


def calculate_points_from_tricks(state: 'GameState') -> np.ndarray:
    """
    Calculate the points of the teams from the trick points and trick winners in the state.
    Args:
        state: state from which to calculate points

    Returns:
        array containing the points of the players
    """
    points = np.zeros(2, dtype=np.int32)
    for trick in range(state.nr_tricks):
        if state.trick_winner[trick] == 0 or state.trick_winner[trick] == 2:
            points[0] += state.trick_points[trick]
        else:
            points[1] += state.trick_points[trick]
    return points


def observation_from_state(state: GameState, player: int = -1) -> GameObservation:
    """
    Initialize observation from game state for the given player or the current player if the player is not
    supplied.

    Args:
        state: The game state from which to determine the observation
        player: player for which to create the observation or -1 for the current player

    Returns:
        the observation for a given game state for the view of the player
    """
    obs = GameObservation()

    obs.dealer = state.dealer
    obs.player = state.player

    if player == -1:
        obs.player_view = state.player
    else:
        obs.player_view = player

    obs.trump = state.trump
    obs.forehand = state.forehand
    obs.declared_trump = state.declared_trump

    if state.nr_played_cards < 36:
        obs.hand[:] = state.hands[obs.player_view, :]

    obs.tricks[:, :] = state.tricks[:, :]
    obs.trick_winner[:] = state.trick_winner[:]
    obs.trick_points[:] = state.trick_points[:]
    obs.trick_first_player[:] = state.trick_first_player[:]
    obs.nr_tricks = state.nr_tricks
    obs.nr_cards_in_trick = state.nr_cards_in_trick

    # current trick is a view to the trick
    if state.nr_played_cards < 36:
        obs.current_trick = obs.tricks[obs.nr_tricks]
    else:
        obs.current_trick = None
    obs.nr_tricks = state.nr_tricks
    obs.nr_cards_in_trick = state.nr_cards_in_trick
    obs.nr_played_cards = state.nr_played_cards
    obs.points[:] = state.points[:]

    return obs


def state_from_observation(obs: GameObservation, hands: np.ndarray) -> GameState:
    """
    Initialize state from an observation and the distribution of all hands.

    Args:
        obs: The observation from which to create the state
        hands: The hands of all players, it must match the observation

    Returns:
        the state
    """
    state = GameState()

    state.dealer = obs.dealer
    state.player = obs.player

    state.player_view = obs.player

    state.trump = obs.trump
    state.forehand = obs.forehand
    state.declared_trump = obs.declared_trump

    state.hands[:, :] = hands[:, :]

    state.tricks[:, :] = obs.tricks[:, :]
    state.trick_winner[:] = obs.trick_winner[:]
    state.trick_points[:] = obs.trick_points[:]
    state.trick_first_player[:] = obs.trick_first_player[:]
    state.nr_tricks = obs.nr_tricks
    state.nr_cards_in_trick = obs.nr_cards_in_trick

    # current trick is a view to the trick
    if obs.nr_played_cards < 36:
        state.current_trick = state.tricks[state.nr_tricks]
    else:
        state.current_trick = None

    state.nr_tricks = obs.nr_tricks
    state.nr_cards_in_trick = obs.nr_cards_in_trick
    state.nr_played_cards = obs.nr_played_cards
    state.points[:] = obs.points[:]

    return state


def state_from_complete_game(game: GameState, cards_played: int) -> GameState:
    """
    Create the state of a game from the state of a completed game for a specific card played

    Preconditions:
        0 <= cards_played <= 35
        game.nr_played_cards == 36

    Args:
        game: The state of the completed game from which to create the state.
        cards_played: the number of cards played for which the state should be created

    Returns:
        a GameState object for the state when the cards have been played.

    """
    state = GameState()
    state.dealer = game.dealer
    state.trump = game.trump
    state.forehand = game.forehand
    state.declared_trump = game.declared_trump

    state.nr_played_cards = cards_played

    # calculate the number of tricks played and how many cards in the current trick
    state.nr_tricks, state.nr_cards_in_trick = divmod(cards_played, 4)

    # copy the trick first player, this is also available after making trump, when no trick has been played yet
    state.trick_first_player[0:state.nr_tricks + 1] = game.trick_first_player[0:state.nr_tricks + 1]

    if cards_played > 0:
        if state.nr_cards_in_trick == 0:
            # only full tricks
            state.tricks[0:state.nr_tricks, :] = game.tricks[0:state.nr_tricks, :]

            # current trick is empty (or none if last card)
            if cards_played == 36:
                state.current_trick = None
            else:
                # this is the next trick, after the full ones
                state.current_trick = state.tricks[state.nr_tricks]

        else:
            # copy all the full tricks first
            state.tricks[0:state.nr_tricks, :] = game.tricks[0:state.nr_tricks, :]

            # copy the trick in progress
            state.tricks[state.nr_tricks, 0:state.nr_cards_in_trick] = \
                game.tricks[state.nr_tricks, 0:state.nr_cards_in_trick]
            # make sure the current trick points to that
            state.current_trick = state.tricks[state.nr_tricks]
        # copy the results from the tricks
        state.trick_winner[0:state.nr_tricks] = game.trick_winner[0:state.nr_tricks]
        state.trick_points[0:state.nr_tricks] = game.trick_points[0:state.nr_tricks]

        state.points[:] = calculate_points_from_tricks(state)

        # determine player
        state.player = (game.trick_first_player[state.nr_tricks]-state.nr_cards_in_trick) % 4
    else:
        # no cards played yet
        state.player = next_player[state.dealer]

    # determine hand still held by the player, which are the cards that the player will play in the next
    # tricks of the full game, that are not played yet

    # add cards for completed tricks
    nr_tricks_completed = state.nr_tricks
    if state.nr_cards_in_trick != 0:
        # there is a non complete trick, treat it specially by adding the cards not yet played in the current trick
        player = (game.trick_first_player[state.nr_tricks]-state.nr_cards_in_trick) % 4
        for card_nr in range(state.nr_cards_in_trick, 4):
            card_played = game.tricks[state.nr_tricks, card_nr]
            state.hands[player, card_played] = 1
            player = next_player[player]
        # exclude this trick from the full tricks
        nr_tricks_completed += 1
    for game_nr in range(nr_tricks_completed, 9):
        player = game.trick_first_player[game_nr]
        for card_nr in range(4):
            card_played = game.tricks[game_nr, card_nr]
            state.hands[player, card_played] = 1
            player = next_player[player]
    return state


def state_for_trump_from_complete_game(game: GameState, for_forhand: bool) -> GameState:
    """
    Create the state of a game from the state of a completed game for the trump selection.

    Preconditions:
        0 <= cards_played <= 35
        game.nr_played_cards == 36

    Args:
        game: The state of the completed game from which to create the state.
        for_forhand: Create the state for the forehand player

    Returns:
        a GameState object for the state when the trump has been selected

    """
    state = GameState()

    state.dealer = game.dealer
    state.trump = -1

    if for_forhand:
        state.forehand = -1
        state.player = next_player[state.dealer]
    else:
        if game.forehand == 1:
            raise ValueError('Requested action for backhand, when game was forehand ')
        else:
            state.forehand = 0
            state.player = partner_player[next_player[state.dealer]]

    state.nr_played_cards = 0

    state.hands[:, :] = calculate_starting_hands_from_game(game)

    return state


def obs_for_trump_from_complete_game(game: GameState) -> (GameObservation, GameObservation or None):
    """
    Get observations for trump selection for forehand and rearhand from a complete game record. If the game has
    trump declared as forehand, the second observation is None
    Args:
        game: full game
    Returns:
        tuple of observations
    """
    hands = calculate_starting_hands_from_game(game)

    obs = GameObservation()
    obs.dealer = game.dealer
    obs.player = next_player[game.dealer]
    obs.hand[:] = hands[obs.player, :]
    obs.forehand = -1
    obs.nr_played_cards = 0

    if game.forehand == 0:
        obs2 = GameObservation()
        obs2.dealer = game.dealer
        obs2.player = partner_player[next_player[game.dealer]]
        obs2.hand[:] = hands[obs2.player, :]
        obs2.forehand = 0
        obs2.nr_played_cards = 0

        return obs, obs2
    else:
        return obs, None
