# HSLU
#
# Created by Thomas Koller on 24.07.18
#
"""
Constants, tables and small utility function for the jass game.
"""

# Implementation notes:
# - numpy arrays are used for all arrays
# - integer arrays are of type np.int32


import numpy as np

# format to read / write dates in dict/json
DATE_FORMAT = '%d.%m.%y %H:%M:%S'

#
# Numerical values correspond to the values in the obtained interface definition
#

# Players (players are numbered clockwise), playing is done counterclockwise
# noinspection PyPep8
NORTH       = 0                         # type: int
EAST        = 1                         # type: int
SOUTH       = 2                         # type: int
WEST        = 3                         # type: int
MAX_PLAYER  = 3                         # type: int

player_strings = ['North', 'East', 'South', 'West']

# Colors for trump, there is a long and a short constant for each
DIAMONDS    = 0                         # type: int  # Ecken / Schellen
D           = DIAMONDS
HEARTS      = 1                         # type: int  # Herz / Rosen
H           = HEARTS
SPADES      = 2                         # type: int  # Schaufeln / Schilten
S           = SPADES
CLUBS       = 3                         # type: int  # Kreuz / Eichel
C           = CLUBS
OBE_ABE     = 4                         # type: int
O           = OBE_ABE
UNE_UFE     = 5                         # type: int
U           = UNE_UFE
MAX_TRUMP   = 5                         # maximal value of a trump action (for loops)

# additional action available at trump selection phase, this is encoded as 10 in the Swisslos specification.
PUSH        = 10                        # type: int # Schieben
P           = PUSH

# alternative value for push (used in some ml approaches to be able to 1-hot encode the trump/push action
# (is translated to PUSH when the action is added to the round)
PUSH_ALT    = 6                         # type: int

# Strings for trumps
trump_strings_short = [
    'D', 'H', 'S', 'C', 'O', 'U', '', '', '', '', 'P'
]

# German strings for trumps
trump_strings_german_long = [
    'D: Schellen', 'H: Rosen', 'S: Schilten', 'C: Eichel', 'O: Obe-Abe', 'U: Une-Ufe'
]

# German string for 'Schieben'
trump_string_push_german = 'P: Schieben'

trump_ints = [
    DIAMONDS, HEARTS, SPADES, CLUBS, OBE_ABE, UNE_UFE
]

# Jass variants (jassTyp in request message)
JASS_SCHIEBER = 'SCHIEBER'
JASS_SCHIEBER_1000 = 'SCHIEBER_1000'
JASS_SCHIEBER_2500 = 'SCHIEBER_2500'
JASS_HEARTS = 'HEARTS'
JASS_ALL = [JASS_SCHIEBER_1000, JASS_SCHIEBER_2500, JASS_HEARTS]

# Card distributions (sets) like hands, cards played etc. will be modelled using arrays, corresponding to a 1-hot
# encoding. Also, this format will be used for neuronal networks. The following constants of all cards define the
# index of the cards in the array

# Diamonds
DA  = 0
DK  = 1
DQ  = 2
DJ  = 3
D10 = 4
D9  = 5
D8  = 6
D7  = 7
D6  = 8

# Hearts
HA  = 9
HK  = 10
HQ  = 11
HJ  = 12
H10 = 13
H9  = 14
H8  = 15
H7  = 16
H6  = 17

# Spades
SA  = 18
SK  = 19
SQ  = 20
SJ  = 21
S10 = 22
S9  = 23
S8  = 24
S7  = 25
S6  = 26

# Clubs
CA  = 27
CK  = 28
CQ  = 29
CJ  = 30
C10 = 31
C9  = 32
C8  = 33
C7  = 34
C6  = 35

# offsets from start of color
A_offset = 0
K_offset = 1
Q_offset = 2
J_offset = 3
Ten_offset = 4
Nine_offset = 5
Eight_offset = 6
Seven_offset = 7
Six_offset = 8

# offsets to start of cards for this color
color_offset = np.array([
    0, 9, 18, 27
], np.int32)

# array to generate string representations from the ids
card_strings = np.array([
    'DA',
    'DK',
    'DQ',
    'DJ',
    'D10',
    'D9',
    'D8',
    'D7',
    'D6',
    'HA',
    'HK',
    'HQ',
    'HJ',
    'H10',
    'H9',
    'H8',
    'H7',
    'H6',
    'SA',
    'SK',
    'SQ',
    'SJ',
    'S10',
    'S9',
    'S8',
    'S7',
    'S6',
    'CA',
    'CK',
    'CQ',
    'CJ',
    'C10',
    'C9',
    'C8',
    'C7',
    'C6',
], np.str)

# dictionary to get the ids from the strings:
# noinspection PyPep8
card_ids = {
    'DA' : DA ,
    'DK' : DK ,
    'DQ' : DQ ,
    'DJ' : DJ ,
    'D10': D10,
    'D9' : D9 ,
    'D8' : D8 ,
    'D7' : D7 ,
    'D6' : D6 ,
    'HA' : HA ,
    'HK' : HK ,
    'HQ' : HQ ,
    'HJ' : HJ ,
    'H10': H10,
    'H9' : H9 ,
    'H8' : H8 ,
    'H7' : H7 ,
    'H6' : H6 ,
    'SA' : SA ,
    'SK' : SK ,
    'SQ' : SQ ,
    'SJ' : SJ ,
    'S10': S10,
    'S9' : S9 ,
    'S8' : S8 ,
    'S7' : S7 ,
    'S6' : S6 ,
    'CA' : CA ,
    'CK' : CK ,
    'CQ' : CQ ,
    'CJ' : CJ ,
    'C10': C10,
    'C9' : C9 ,
    'C8' : C8 ,
    'C7' : C7 ,
    'C6' : C6
}
#
# 2D array of scoring values for the cards in a trick, each row is the scoring for the cards for the trump indicated
# by the row
#
# noinspection PyPep8
card_values = np.array(
    [
       # DA DK DQ DJ D10 D9 D8 D7 D6 HA HK HQ HJ H10 H9 H8 H7 H6 SA SK SQ SJ S10 S9 S8 S7 S6 CA CK CQ CJ C10 C9 C8 C7 C6
        [11, 4, 3,20, 10,14, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0],
        [11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3,20, 10,14, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0],
        [11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3,20, 10,14, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0],
        [11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3, 2, 10, 0, 0, 0, 0,11, 4, 3,20, 10,14, 0, 0, 0],
        [11, 4, 3, 2, 10, 0, 8, 0, 0,11, 4, 3, 2, 10, 0, 8, 0, 0,11, 4, 3, 2, 10, 0, 8, 0, 0,11, 4, 3, 2, 10, 0, 8, 0, 0],
        [ 0, 4, 3, 2, 10, 0, 8, 0,11, 0, 4, 3, 2, 10, 0, 8, 0,11, 0, 4, 3, 2, 10, 0, 8, 0,11, 0, 4, 3, 2, 10, 0, 8, 0,11]
    ], np.int32)
#
# 2D array of masks which cards belong to a specific color, can be used to filter matching/non-matching cards
#
color_masks = np.array(
    [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ], np.int32
)

#
# 1D array of which color a card belongs to
#
color_of_card = np.array(
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3],
    np.int32
)

#
# 1D array of offset of each card
offset_of_card = np.array(
    [A_offset, K_offset, Q_offset, J_offset, Ten_offset, Nine_offset, Eight_offset, Seven_offset, Six_offset,
     A_offset, K_offset, Q_offset, J_offset, Ten_offset, Nine_offset, Eight_offset, Seven_offset, Six_offset,
     A_offset, K_offset, Q_offset, J_offset, Ten_offset, Nine_offset, Eight_offset, Seven_offset, Six_offset,
     A_offset, K_offset, Q_offset, J_offset, Ten_offset, Nine_offset, Eight_offset, Seven_offset, Six_offset],
    np.int32
)
#
#
# 2D array of higher trump cards, i.e. higher_trump[DA,:] will give the mask of higher trumps than DA (i.e. DJ, DN)
# (used to make the logic for determining the valid moves slightly easier to read). The full array is constructed
# from a smaller array higher_trump_card for the card values only
#
higher_trump_card = np.array(
    [
        [0, 0, 0, 1, 0, 1, 0, 0, 0],  # A
        [1, 0, 0, 1, 0, 1, 0, 0, 0],  # K
        [1, 1, 0, 1, 0, 1, 0, 0, 0],  # Q
        [0, 0, 0, 0, 0, 0, 0, 0, 0],  # J
        [1, 1, 1, 1, 0, 1, 0, 0, 0],  # 10
        [0, 0, 0, 1, 0, 0, 0, 0, 0],  # 9
        [1, 1, 1, 1, 1, 1, 0, 0, 0],  # 8
        [1, 1, 1, 1, 1, 1, 1, 0, 0],  # 7
        [1, 1, 1, 1, 1, 1, 1, 1, 0]   # 6
    ], np.int32
)
# lower trump cards also include the card itself
lower_trump_card = 1 - higher_trump_card

# full array for each card
higher_trump = np.zeros([36, 36], np.int32)
higher_trump[0:9, 0:9] = higher_trump_card
higher_trump[9:18, 9:18] = higher_trump_card
higher_trump[18:27, 18:27] = higher_trump_card
higher_trump[27:36, 27:36] = higher_trump_card

# same for lower trump
lower_trump = np.zeros([36, 36], np.int32)
lower_trump[0:9, 0:9] = lower_trump_card
lower_trump[9:18, 9:18] = lower_trump_card
lower_trump[18:27, 18:27] = lower_trump_card
lower_trump[27:36, 27:36] = lower_trump_card

# next player of player with given index
next_player = [3, 0, 1, 2]

# partner player of player with given index
partner_player = [2, 3, 0, 1]

# true if same_player[i, j] are in the same team for players i, j
same_team = np.array(
    [
        [True, False, True, False],
        [False, True, False, True],
        [True, False, True, False],
        [False, True, False, True]
    ], np.bool)

# team 0/1 of players
team = np.array([0, 1, 0, 1])

# alternativevalues for trump for 'full' actions, i.e.both trump and cards are valid actions
TRUMP_FULL_OFFSET = 36
TRUMP_FULL_D = TRUMP_FULL_OFFSET + DIAMONDS
TRUMP_FULL_H = TRUMP_FULL_OFFSET + HEARTS
TRUMP_FULL_S = TRUMP_FULL_OFFSET + SPADES
TRUMP_FULL_C = TRUMP_FULL_OFFSET + CLUBS
TRUMP_FULL_O = TRUMP_FULL_OFFSET + OBE_ABE
TRUMP_FULL_U = TRUMP_FULL_OFFSET + UNE_UFE
TRUMP_FULL_P = TRUMP_FULL_OFFSET + PUSH_ALT
ACTION_SET_FULL_SIZE = TRUMP_FULL_P + 1
