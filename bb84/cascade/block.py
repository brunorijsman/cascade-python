from bb84.cascade.shuffle import Shuffle

class Block:
    """
    A block is a contiguous subset of bits in a potentially shuffled key.
    """

    _key_index_to_blocks = {}

    def __init__(self, shuffle, start_index, end_index):
        """
        Create a block, which is a contiguous subset of bits in a potentially shuffled key.

        Args:
            shuffle (Shuffle): the shuffled key from which to create the block. The shuffle must
                not be empty.
            start_index (int): The shuffle index, inclusive, at which the block starts. Must be in
                range [0, shuffle.size).
            end_index (int): The shuffle index, exclusive, at which the block end. Must be in range
                [0, shuffle.size]. The range must encompass at least 1 bit, i.e.
                end_index > start_index.
        """

        # Validate arguments.
        assert isinstance(shuffle, Shuffle)
        assert shuffle.size > 0
        assert isinstance(start_index, int)
        assert 0 <= start_index < shuffle.size
        assert isinstance(end_index, int)
        assert 0 <= end_index <= shuffle.size
        assert end_index > start_index

        # The subset of the shuffle underlying this block.
        self._shuffle = shuffle
        self._start_index = start_index
        self._end_index = end_index

        # To detect attempts to split more than once.
        self._has_been_split = False

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

        Args:
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
    def size(self):
        """
        Get the size of the block in bits.

        Returns:
            The size of the block in bits.
        """
        return self._end_index - self._start_index

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
        Split this block into two sub-blocks of equal size (plus or minus one). If the block has
        an odd size, the left sub-block will be one bit larger than th right sub-block.
        This block must be at least 2 bits in size and must not have been split before.

        Returns:
            (left_child_block, right_child_block)
        """

        # Validate arguments.
        assert self._end_index - self._start_index > 1
        assert not self._has_been_split

        # Split the block down the middle.
        self._has_been_split = True
        middle_index = self._start_index + (self._end_index - self._start_index + 1) // 2
        left_sub_block = Block(self._shuffle, self._start_index, middle_index)
        right_sub_block = Block(self._shuffle, middle_index, self._end_index)
        return (left_sub_block, right_sub_block)

    def correct_one_bit(self, ask_correct_parity_function):
        """
        Try to correct a single bit error in this block by recursively dividing the block into
        sub-blocks and comparing the current parity of each of those sub-blocks with the coorect
        parity of the same sub-block.

        Args:
            ask_correct_parity_function: A function which takes a block as a parameter and returns
                the correct parity for the block. In other words, we assume that the block contains
                some errors due to noise and/or due to an eavesdropper, and we want the know the
                parity of the block without the errors. In real life this involves asking the party
                who sent us the block; in simulation we can get it more easily because we ourselves
                introduced the errors on purpose.

        TODO:
            * Implement and document and test Cascase

        Returns:

            True if a single error was corrected, False otherwise.
        """

        # Validate arguments.
        assert callable(ask_correct_parity_function)

        # We only attempt to correct a bit error if there is an odd number of errors, i.e. if
        # the current parity if different from the correct parity. If the current and correct
        # parity are the same, it doesn't mean there are no errors, it only means there is an even
        # number (potentially zero) number of errors. In that case we don't attempt to correct and
        # instead we "hope" that the error will be caught in another shuffle of the key.
        correct_parity = ask_correct_parity_function(self)
        if self._current_parity == correct_parity:
            return False

        # If this block contains a single bit, we have finished the recursion and found an error.
        if self.size == 1:

            # Fix the error by flipping the one and only bit in this block.
            self._shuffle.flip_bit(self._start_index)

            # TODO: Cascade

            # We fixed an error.
            return True

        # Split the block into two sub-blocks. Since the whole block contains an odd number of
        # errors, either the first sub-block contains an odd number of errors and the second
        # sub-block contains an even number of errors, or vice versa. Recursively check each of
        # the two sub-blocks. Whichever one has the odd number of errors will recurse more deeply
        # until we find a single bit error and fix it.
        (left_sub_block, right_sub_block) = self.split()
        if left_sub_block.correct_one_bit(ask_correct_parity_function):

            # The left sub-block had an odd number of errors. We know for a fact that the right
            # sub-block has an even number of errors, so we don't need to recurse any deeper into
            # the right sub-block. Not recursing avoid an unnecesary and potentially expensive call
            # to ask_correct_parity_function.
            pass

        else:

            # The left sub-block had an even number of errors. So that means that the right
            # sub-block must contain an odd number of errors. Recurse deeper into the right
            # sub-block.
            assert right_sub_block.correct_one_bit(ask_correct_parity_function)

        return True

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

        Args:
            key_index (int): The key index that we are looking for.

        Returns:
            The list of block that contain a given key index.
        """
        assert isinstance(key_index, int)
        assert key_index >= 0
        return Block._key_index_to_blocks.get(key_index, [])
