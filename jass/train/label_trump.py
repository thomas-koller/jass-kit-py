# HSLU
#
# Created by Thomas Koller on 08.09.19
#


class LabelTrump:
    """
    Class to define training information for a trump selection.

    This is to make it similar to selecting playing a card (the class LabelPlay), however for trump the only
    meaningful label, seems to be the trump selection (including the decision to pass :-) ).

    """
    def __init__(self,
                 trump: int,
                ):
        self.trump = trump
