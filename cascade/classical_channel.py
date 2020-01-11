from abc import ABC, abstractmethod

class ClassicalChannel(ABC):
    """
    An abstract base class that abstracts the interactions that Bob has with Alice over the
    classical channel.
    """

    @abstractmethod
    def start_reconciliation(self):
        """
        Bob tells Alice that he is starting a new Cascade reconciliation.
        """

    @abstractmethod
    def end_reconciliation(self):
        """
        Bob tells Alice that he is finished with a Cascade reconciliation.
        """

    @abstractmethod
    def ask_parities(self, blocks):
        """
        Bob asks Alice to compute the parities for a list of blocks.

        Params:
            blocks (list): A list of blocks for which the ask the parities.

        Returns:
            parities (list): A list of parities, where each parity is an int value 0 or 1. The list
            of parities must be in the same order as the list of blocks.
        """
