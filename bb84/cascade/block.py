from bb84.cascade.shuffle import Shuffle

class Block:
    """
    A block is a contiguous subset of bits in a potentially shuffled key.
    """

    _key_index_to_blocks = {}

    def __init__(self, shuffle, start_index, end_index, parent=None):
        """
        Create a block, which is a contiguous subset of bits in a potentially shuffled key.

        Params:
            shuffle (Shuffle): the shuffled key from which to create the block. The shuffle must
            not be empty.
            start_index (int): The shuffle index, inclusive, at which the block starts. Must be in
            range [0, shuffle.size).
            end_index (int): The shuffle index, exclusive, at which the block end. Must be in range
            [0, shuffle.size]. The range must encompass at least 1 bit, i.e.
            end_index > start_index.
            parent (Block): The parent block of this block.
        """

        # Validate arguments.
        assert isinstance(shuffle, Shuffle)
        assert shuffle.size > 0
        assert isinstance(start_index, int)
        assert 0 <= start_index < shuffle.size
        assert isinstance(end_index, int)
        assert 0 <= end_index <= shuffle.size
        assert end_index > start_index
        assert parent is None or isinstance(parent, Block)

        # The subset of the shuffle underlying this block.
        self._shuffle = shuffle
        self._start_index = start_index
        self._end_index = end_index

        # Keep track of family tree.
        self._parent = parent
        self._left_child = None
        self._right_child = None

        # Calculate the actual parity of this block.
        self._current_parity = 0
        for index in range(start_index, end_index):
            if shuffle.get_bit(index) == 1:
                self._current_parity = 1 - self._current_parity

        # Update key bit to block map.
        for shuffle_index in range(self._start_index, self._end_index):
            key_index = self._shuffle.get_key_index(shuffle_index)
            if key_index in Block._key_index_to_blocks:
                Block._key_index_to_blocks[key_index].append(self)
            else:
                Block._key_index_to_blocks[key_index] = [self]

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

    @property
    def current_parity(self):
        """
        Get the current parity of the block.

        Returns:
            The current parity (0 or 1) of the block.
        """
        return self._current_parity

    def split(self):
        """
        Split this block into two child blocks of equal size (plus or minus one). If the block has
        an odd size, the left child block will be one bit larger than th right child block.
        This block must be at least 2 bits in size and most not already have been split before.

        Returns:
            (left_child_block, right_child_block)
        """

        # Validate arguments.
        assert self._end_index - self._start_index > 1
        assert self._left_child is None
        assert self._right_child is None

        # Split the block down the middle.
        middle_index = self._start_index + (self._end_index - self._start_index + 1) // 2
        self._left_child = Block(self._shuffle, self._start_index, middle_index, self)
        self._right_child = Block(self._shuffle, middle_index, self._end_index, self)
        return (self._left_child, self._right_child)

    @staticmethod
    def clear_key_index_to_block_map():
        """
        Clear key index to block map.
        """
        Block._key_index_to_blocks = {}

    @staticmethod
    def get_blocks_containing_key_index(key_index):
        """
        Get a list of block that contain a given key index.

        Params:
            key_index (int): The key index that we are looking for.

        Returns:
            The list of block that contain a given key index.
        """
        assert isinstance(key_index, int)
        assert key_index >= 0
        return Block._key_index_to_blocks.get(key_index, [])
