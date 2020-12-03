# HSLU
#
# Created by Thomas Koller on 7/25/2020
#
import numpy as np

from typing import List

from jass.game.const import card_ids, card_strings, TRUMP_FULL_OFFSET, PUSH_ALT, PUSH

"""
Utilities
"""


def get_cards_encoded(cards: List[int]) -> np.ndarray:
    """
    Get the 1-hot encoded array of the cards in the list.

    Args:
        cards: the cards

    Returns:
        1-hot encoded numpy array of the cards in the list
    """
    result = np.zeros(36, np.int32)
    result[cards] = 1
    return result


def get_cards_encoded_from_str(cards: List[str]) -> np.ndarray:
    """
    Get the 1-hot encoded array of the cards in the list.

    Args:
        cards: the cards

    Returns:
        1-hot encoded numpy array of the cards in the list
    """
    cards_int = convert_str_encoded_cards_to_int_encoded(cards)
    result = np.zeros(36, np.int32)
    result[cards_int] = 1
    return result


def convert_str_encoded_cards_to_int_encoded(cards: List[str]) -> List[int]:
    """
    Get the int encoded array of the str encoded cards in the list
    Args:
        cards: the cards as str encoded

    Returns:
        list of the cards, int encoded
    """
    return [card_ids[card] for card in cards]


def convert_int_encoded_cards_to_str_encoded(cards: List[int]) -> List[str]:
    """
    Get the int encoded array of the str encoded cards in the list
    Args:
        cards: the cards as int encoded

    Returns:
        list of the cards, str encoded
    """
    return [card_strings[i] for i in cards if i != -1]


def convert_one_hot_encoded_cards_to_str_encoded_list(cards: np.ndarray) -> List[str]:
    """
    Get the str encoded array of a one hot encoded array
    Args:
        cards: the cards, 1-hot encoded

    Returns:
        list of the cards as str
    """
    return [card_strings[i] for i in np.flatnonzero(cards)]


def convert_one_hot_encoded_cards_to_int_encoded_list(cards: np.ndarray):
    """
    Get the int encoded array of a one hot encoded array
    Args:
        cards: the cards, 1-hot encoded

    Returns:
        list of the cards as int
    """
    return np.flatnonzero(cards).tolist()


def count_colors(cards: np.ndarray) -> np.ndarray:
    """
    Count the colors in the cards. The return value is an array of size 4 that indicates how many cards of each
    color D, H, S and C are in the hand
    Args:
        cards: a one-hot encoded array of length 36 indicating the cards

    Returns:
        a an array of length for containing the number of cards of colors D, H, S and C
    """
    result = np.zeros(4, np.int32)
    cards.sum()
    result[0] = (cards[0:9]).sum()
    result[1] = (cards[9:18]).sum()
    result[2] = (cards[18:27]).sum()
    result[3] = (cards[27:36]).sum()
    return result


def deal_random_hand() -> np.ndarray:
    """
    Deal random cards for each hand.

    Returns:
        one hot encoded 4x36 array
    """
    # shuffle card ids
    cards = np.arange(0, 36, dtype=np.int32)
    np.random.shuffle(cards)
    hands = np.zeros(shape=[4, 36], dtype=np.int32)

    # convert to one hot encoded
    hands[0, cards[0:9]] = 1
    hands[1, cards[9:18]] = 1
    hands[2, cards[18:27]] = 1
    hands[3, cards[27:39]] = 1

    return hands


def full_to_trump(full_action: int) -> int:
    action = full_action - TRUMP_FULL_OFFSET
    if action == PUSH_ALT:
        return PUSH
    else:
        return action


def trump_to_full(action: int) -> int:
    return action + TRUMP_FULL_OFFSET