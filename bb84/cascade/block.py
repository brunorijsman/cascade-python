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

    @staticmethod
    def create_blocks_covering_shuffle(shuffle, block_size):
        """
        Create a list of blocks of a given size that cover a given shuffled key.

        Params:
            shuffle (Shuffle): The shuffled key to be covered by the blocks.
            block_size (int): The size of each block. Each block in the list, except for the last
            one, will be exactly this size. The last block may be smaller.

        Returns:
            A list of blocks that cover the shuffled key.
        """

        # Validate arguments.
        assert isinstance(block_size, int)
        assert block_size > 0
        assert isinstance(shuffle, Shuffle)

        # Generate the blocks.
        blocks = []
        remaining_bits = shuffle.size
        start_index = 0
        while remaining_bits > 0:
            actual_block_size = min(block_size, remaining_bits)
            end_index = start_index + actual_block_size
            block = Block(shuffle, start_index, end_index)
            blocks.append(block)
            start_index += actual_block_size
            remaining_bits -= actual_block_size
        return blocks

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
