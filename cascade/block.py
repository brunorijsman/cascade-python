class Block:
    """
    A block is a contiguous subset of bits in a potentially shuffled key.
    """

    ERRORS_EVEN = 0
    """The block contains an odd number of errors."""
    ERRORS_ODD = 1
    """The block contains an even number of errors."""
    ERRORS_UNKNOWN = None
    """We don't know whether the block contains an even or an odd number of errors."""

    def __init__(self, key, shuffle, start_index, end_index):
        """
        Create a block, which is a contiguous subset of bits in a shuffled key.

        Args:
            key (Key): The key for which to create one single block that covers a subset of the key.
            shuffle (Shuffle): The shuffle to apply to the key before creating the block.
            start_index (int): The shuffle index, inclusive, at which the block starts. Must be in
                range [0, shuffle._size).
            end_index (int): The shuffle index, exclusive, at which the block end. Must be in range
                [0, shuffle._size]. The range must encompass at least 1 bit, i.e.
                end_index > start_index.
        """

        # Store block attributes.
        self._key = key
        self._shuffle = shuffle
        self._start_index = start_index
        self._end_index = end_index

        self.is_top_block = False    ###@@@ Temporary while refactoring
        self.is_cascaded = False     ###@@@ Temporary while refactoring

        # The following information is only used in sub-blocks that are created by calling split.
        self._sibling_block = None
        self._is_left_half = False
        self._is_right_half = False

        # Calculate the current parity for this block.
        self._current_parity = shuffle.calculate_parity(key, start_index, end_index)

        # We don't yet know the correct parity for this block, nor for the parent block.
        self._parent_correct_parity = None
        self._correct_parity = None

    @staticmethod
    def create_covering_blocks(key, shuffle, block_size):
        """
        Create a list of blocks of a given size that cover a given shuffled key.

        Args:
            key (Key): The key for which to create a list of block that collectively cover the
                entire key.
            shuffle (Shuffle): The shuffle to apply to the key before creating the blocks.
            block_size (int): The size of each block. Each block in the list, except for the last
                one, will be exactly this size. The last block may be smaller.

        Returns:
            A list of blocks that cover the shuffled key.
        """

        # Generate the blocks.
        blocks = []
        remaining_bits = shuffle.get_size()
        start_index = 0
        while remaining_bits > 0:
            actual_block_size = min(block_size, remaining_bits)
            end_index = start_index + actual_block_size
            block = Block(key, shuffle, start_index, end_index)
            block.is_top_block = True    ###@@@ Temporary
            blocks.append(block)
            start_index += actual_block_size
            remaining_bits -= actual_block_size
        return blocks

    def split(self):

        # Determine where to split the block.
        middle_index = self._start_index + (self._end_index - self._start_index + 1) // 2

        # Create the left and the right sub-block.
        left_sub_block = Block(self._key, self._shuffle, self._start_index, middle_index)
        right_sub_block = Block(self._key, self._shuffle, middle_index, self._end_index)

        # Tie the two sub-blocks together as siblings.
        # pylint:disable=protected-access
        left_sub_block._parent_correct_parity = self._correct_parity
        left_sub_block._sibling_block = right_sub_block
        left_sub_block._is_left_half = True
        right_sub_block._parent_correct_parity = self._correct_parity
        right_sub_block._sibling_block = left_sub_block
        right_sub_block._is_right_half = True

        # Return the left and right sub-block.
        return (left_sub_block, right_sub_block)

    def __repr__(self):
        """
        Get the unambiguous string representation of the block.

        Returns:
            The unambiguous string representation of the block.
        """
        string = "Block:"
        for shuffle_index in range(self._start_index, self._end_index):
            key_index = self._shuffle.get_key_index(shuffle_index)
            key_bit = self._shuffle.get_bit(self._key, shuffle_index)
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
            string += str(self._shuffle.get_bit(self._key, shuffle_index))
        return string

    def __lt__(self, other):
        # TODO: Add unit test code
        """
        Is this block "less than" the other block? This is needed to insert the blocks in a priority
        queue; for equal block sizes the priority queue want to order by increasing block size. We
        don't care about the order of blocks within a given block size, so we simply order based on
        the id().

        Returns:
            True if self < other, False otherwise.
        """
        return id(self) < id(other)

    def get_start_index(self):
        return self._start_index

    def get_end_index(self):
        return self._end_index

    def get_shuffle(self):
        """
        Get the shuffle for this block.

        Returns:
            The shuffle for this block.
        """
        return self._shuffle

    def get_size(self):
        """
        Get the size of the block in bits.

        Returns:
            The size of the block in bits.
        """
        return self._end_index - self._start_index

    ###@@@ Do we need this?
    def get_key_indexes(self):
        """
        Get a list of key indexes for this block.

        Returns:
            The key indexes for this block (the ordering of the list is undefined; in particular
            don't assume that the key indexes are in increasing order.)
        """
        # TODO: Add unit test
        key_indexes = []
        for shuffle_index in range(self._start_index, self._end_index):
            key_index = self._shuffle.get_key_index(shuffle_index)
            key_indexes.append(key_index)
        return key_indexes

    def get_current_parity(self):
        """
        Get the current parity of the block.

        Returns:
            The current parity (0 or 1) of the block.
        """
        return self._current_parity

    def get_or_infer_correct_parity(self):

        # If we know the correct parity, return it.
        if self._correct_parity is not None:
            return self._correct_parity

        # We don't know the correct parity... try to infer it based on what we know (if anything)
        # about the correct parity of the sibling block and the parent block.

        # Can't infer if we don't have a sibling.
        if self._sibling_block is None:
            return None

        # Can't infer if we don't know the correct parity for the sibling.
        # pylint:disable=protected-access
        if self._sibling_block._correct_parity is None:
            return None

        # Can't infer if we don't know the correct parity for the parent.
        if self._parent_correct_parity is None:
            if self._sibling_block._parent_correct_parity is None:
                return False
            parent_correct_parity = self._sibling_block._parent_correct_parity
        else:
            if self._sibling_block._parent_correct_parity is not None:
                assert self._sibling_block._parent_correct_parity == self._parent_correct_parity
            parent_correct_parity = self._parent_correct_parity

        # We know the parent and the sibling correct parity, so we can infer the correct parity
        # for this block.
        if parent_correct_parity == self._sibling_block._correct_parity:
            self._correct_parity = 0
        else:
            self._correct_parity = 1
        return self._correct_parity

    def get_right_sibling(self):
        if self._sibling_block is None:
            return None
        if not self._is_left_half:
            return None
        right_sibling_block = self._sibling_block
        # pylint:disable=protected-access
        assert right_sibling_block._is_right_half   # TODO: remove
        return right_sibling_block

    def get_correct_parity(self):
        """
        Get the correct parity of the block, if we know it.

        Returns:
            The current parity (0 or 1) of the block, or None if we don't know it.
        """
        return self._correct_parity

    def get_parent_correct_parity(self):
        """
        Get the correct parity of the parent block, if we know it.

        Returns:
            The current parity (0 or 1) of the parent block, or None if we don't know it.
        """
        return self._parent_correct_parity

    def set_correct_parity(self, correct_parity):
        """
        Set the correct parity of the block.

        Params:
            correct_parity (int): The current parity (0 or 1).
        """
        self._correct_parity = correct_parity

    def get_error_parity(self):
        """
        Does this block have an odd or an even number of errors?

        Returns:
            * ERRORS_ODD = The block contains an odd number of errors.
            * ERRORS_EVEN = The block contains an even number of errors.
            * ERRORS_UNKNOWN = We don't yet know whether the block contains an odd or even number of
              errors because we have not yet asked what the parity of the original key (witout
              noise) is.
        """
        if self._correct_parity is None:
            return Block.ERRORS_UNKNOWN
        assert self._current_parity is not None   # Always known; is set in constructor
        if self._current_parity == self._correct_parity:
            return Block.ERRORS_EVEN
        return Block.ERRORS_ODD

    def get_key_index(self, shuffle_index):
        return self._shuffle.get_key_index(shuffle_index)

    def flip_bit(self, flipped_shuffle_index):
        self._shuffle.flip_bit(self._key, flipped_shuffle_index)

    def flip_parity(self):
        """
        Flip the current parity of this block. This is needed when a single bit in the block is
        flipped as a result of a single bit error correction.
        """
        # TODO: Add stand-alone unit test case
        self._current_parity = 1 - self._current_parity
