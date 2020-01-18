from cascade.classical_channel import ClassicalChannel

class MockClassicalChannel(ClassicalChannel):
    """
    A mock concrete implementation of the ClassicalChannel base class, which is used for the
    experiments.
    """

    def __init__(self, correct_key):
        self._correct_key = correct_key
        self._id_to_shuffle = {}
        self._reconciliation_started = False

    def start_reconciliation(self):
        self._reconciliation_started = True

    def end_reconciliation(self):
        self._reconciliation_started = False
        self._id_to_shuffle = {}

    def ask_parities(self, blocks):
        parities = []
        for block in blocks:
            shuffle = block.get_shuffle()
            start_index = block.get_start_index()
            end_index = block.get_end_index()
            parity = shuffle.calculate_parity(self._correct_key, start_index, end_index)
            parities.append(parity)
        return parities
