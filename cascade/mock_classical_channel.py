from cascade.classical_channel import ClassicalChannel
from cascade.key import Key

class MockClassicalChannel(ClassicalChannel):
    """
    A mock concrete implementation of the ClassicalChannel base class, which is used for the
    experiments.
    """

    # TODO: Add unit test

    def __init__(self, correct_key):
        assert isinstance(correct_key, Key)
        self._correct_key = correct_key
        self._id_to_shuffle = {}
        self._reconciliation_started = False

    def start_reconciliation(self):
        assert not self._reconciliation_started
        self._reconciliation_started = True

    def end_reconciliation(self):
        assert self._reconciliation_started
        self._reconciliation_started = False
        self._id_to_shuffle = {}

    def ask_parities(self, blocks):

        # Validate arguments.
        assert isinstance(blocks, list)
        assert self._reconciliation_started

        # Collect the parities of all the requested shuffle ranges.
        parities = []
        for block in blocks:

            # Compute the parity.
            shuffle = block.get_shuffle()
            shuffle_start_index = block.get_start_index()
            shuffle_end_index = block.get_end_index()
            parity = shuffle.calculate_parity(self._correct_key, shuffle_start_index,
                                              shuffle_end_index)
            parities.append(parity)

        return parities
