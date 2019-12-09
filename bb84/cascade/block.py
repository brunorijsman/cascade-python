from bb84.cascade.shuffle import Shuffle

class Block:

    def __init__(self, shuffle, start_index, end_index):
        """
        Create a block that represents a subset of a shuffled key.

        Params:
            shuffle (Shuffled): the shuffled key from which to create the block.
            start_index (int): The shuffle index, inclusive, at which the block starts. Must be in
                range [0, shuffle.size).
            end_index (int): The shuffle index, exclusive, at which the block end. Must be in range
                [0, shuffle.size] and end_index >= start_index.
        """

        # Validate arguments.
        assert isinstance(shuffle, Shuffle)
        assert isinstance(start_index, int)
        assert 0 <= start_index < shuffle.size
        assert isinstance(end_index, int)
        assert 0 <= end_index <= shuffle.size
        assert end_index >= start_index

        # The subset of the shuffle underlying this block.
        self._shuffle = shuffle
        self._start_index = start_index
        self._end_index = end_index

    def __repr__(self):
        """
        Get the unambiguous string representation of the block.

        Returns:
            The unambiguous string representation of the block.
        """
        string = "Block:"
        for shuffle_index in range(self._start_index, self._end_index):
            key_index = self._shuffle.get_key_index(shuffle_index)
            key_bit = self._shuffle.get_bit(shuffle_index)
            string += f" {shuffle_index}->{key_index}={key_bit}"
        return string

    def __str__(self):
        """
        Get the human-readable string representation of the block.

        Returns:
            The human-readable string representation of the block.
        """
        string = ""
        for shuffle_index in range(self._start_index, self._end_index):
            string += str(self._shuffle.get_bit(shuffle_index))
        return string
