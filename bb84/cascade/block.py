from bb84.cascade.key import Key
from bb84.cascade.session import Session
from bb84.cascade.shuffle import Shuffle

class Block:
    """
    A block is a contiguous subset of bits in a potentially shuffled key.
    """

    ERRORS_ODD = 0
    """The block contains an even number of errors."""
    ERRORS_EVEN = 1
    """The block contains an odd number of errors."""
    ERRORS_UNKNOWN = 3
    """We don't know whether the block contains an even or an odd number of errors."""

    def __init__(self, session, key, shuffle, start_index, end_index):
        """
        Create a block, which is a contiguous subset of bits in a shuffled key.

        Args:
            session (Session): The Cascade session in whose context this block is created.
            key (Key): The key for which to create one single block that covers a subset of the key.
            shuffle (Shuffle): The shuffle to apply to the key before creating the block.
            start_index (int): The shuffle index, inclusive, at which the block starts. Must be in
                range [0, shuffle.size).
            end_index (int): The shuffle index, exclusive, at which the block end. Must be in range
                [0, shuffle.size]. The range must encompass at least 1 bit, i.e.
                end_index > start_index.
        """

        # Validate arguments.
        assert isinstance(session, Session)
        assert isinstance(key, Key)
        assert isinstance(shuffle, Shuffle)
        assert shuffle.size == key.size
        assert isinstance(start_index, int)
        assert 0 <= start_index < shuffle.size
        assert isinstance(end_index, int)
        assert 0 <= end_index <= shuffle.size
        assert end_index > start_index

        # Store block attributes.
        self._session = session
        self._key = key
        self._shuffle = shuffle
        self._start_index = start_index
        self._end_index = end_index

        # Keep track of left and right sub-block to avoid creating them more then once.
        self._left_sub_block = None
        self._right_sub_block = None

        # Calculate the current parity for this block.
        self._current_parity = shuffle.calculate_parity(key, start_index, end_index)

        # We don't yet know the correct parity for this block.
        self._correct_parity = None

        # Register this block in the session.
        self._session.register_block(self)

    @staticmethod
    def create_covering_blocks(session, key, shuffle, block_size):
        """
        Create a list of blocks of a given size that cover a given shuffled key.

        Args:
            session (Session): The Cascade session in whose context this block is created.
            key (Key): The key for which to create a list of block that collectively cover the
                entire key.
            shuffle (Shuffle): The shuffle to apply to the key before creating the blocks.
            block_size (int): The size of each block. Each block in the list, except for the last
                one, will be exactly this size. The last block may be smaller.

        Returns:
            A list of blocks that cover the shuffled key.
        """

        # Validate arguments.
        assert isinstance(session, Session)
        assert isinstance(key, Key)
        assert isinstance(shuffle, Shuffle)
        assert shuffle.size == key.size
        assert isinstance(block_size, int)
        assert block_size > 0

        # Generate the blocks.
        blocks = []
        remaining_bits = shuffle.size
        start_index = 0
        while remaining_bits > 0:
            actual_block_size = min(block_size, remaining_bits)
            end_index = start_index + actual_block_size
            block = Block(session, key, shuffle, start_index, end_index)
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

    @property
    def size(self):
        """
        Get the size of the block in bits.

        Returns:
            The size of the block in bits.
        """
        return self._end_index - self._start_index

    @property
    def key_indexes(self):
        """
        Get a list of key indexes for this block.

        Returns:
            The key indexes for this block (the ordering of the list is undefined; in particular
            don't assume that the key indexes are in increasing order.)
        """
        # TODO: @@@ Add unit test
        key_indexes = []
        for shuffle_index in range(self._start_index, self._end_index):
            key_index = self._shuffle.get_key_index(shuffle_index)
            key_indexes.append(key_index)
        return key_indexes

    @property
    def current_parity(self):
        """
        Get the current parity of the block.

        Returns:
            The current parity (0 or 1) of the block.
        """
        return self._current_parity

    def get_left_sub_block(self):
        """
        Return the left sub-block of this block. If the block has an odd size, the left sub-block
        will be one bit larger than the right sub-block. If the size of this block is less than 2
        then it is not allowed to ask for any sub-block.

        Returns:
            The left sub-block.
        """

        # Validate arguments.
        assert self._end_index - self._start_index > 1

        # If we already created the left sub-block, return it.
        if self._left_sub_block:
            return self._left_sub_block

        # Create the left sub-block.
        middle_index = self._start_index + (self._end_index - self._start_index + 1) // 2
        self._left_sub_block = Block(self._session, self._key, self._shuffle, self._start_index,
                                     middle_index)
        return self._left_sub_block

    def get_right_sub_block(self):
        """
        Return the right sub-block of this block. If the block has an odd size, the left sub-block
        will be one bit larger than the right sub-block. If the size of this block is less than 2
        then it is not allowed to ask for any sub-block.

        Returns:
            The right sub-block.
        """

        # Validate arguments.
        assert self._end_index - self._start_index > 1

        # If we already created the right sub-block, return it.
        if self._right_sub_block:
            return self._right_sub_block

        # Create the right sub-block.
        middle_index = self._start_index + (self._end_index - self._start_index + 1) // 2
        self._right_sub_block = Block(self._session, self._key, self._shuffle, middle_index,
                                      self._end_index)
        return self._right_sub_block

    @property
    def error_parity(self):
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
        if self._current_parity == self._correct_parity:
            return Block.ERRORS_EVEN
        return Block.ERRORS_ODD

    def correct_one_bit(self, ask_correct_parity_function):
        """
        Try to correct a single bit error in this block by recursively dividing the block into
        sub-blocks and comparing the current parity of each of those sub-blocks with the coorect
        parity of the same sub-block.

        Args:
            ask_correct_parity_function: A function which takes start_shuffle_index (inclusive) and
                end_shuffle_index (exclusive) as a parameters and returns the correct parity:

                def ask_correct_parity(start_shuffle_index, end_shuffle_index):
                    returns correct_parity

                We assume that the block being corrected contains some errors due to noise and/or
                due to an eavesdropper. In order to locate exactly one bit error and correct it,
                we want the need the parity of the corresponding error-free (noiseless) block and
                specific sub-blocks.

                In real life this involves asking the party who sent us the block to give us the
                correct parity. In simulation scenarios we can get the correct parity more easily
                because the simulation knows both the sent (noiseless) and received (noisy) keys.

        Returns:

            The shuffle_index of the correct bit, or None if no bit was corrected.
        """

        # Validate arguments.
        assert callable(ask_correct_parity_function)

        # Ask and remember the correct parity for this block (unless we already know it).
        if self._correct_parity is None:
            self._correct_parity = ask_correct_parity_function(self._start_index, self._end_index)

        # We only attempt to correct a bit error if there is an odd number of errors, i.e. if
        # the current parity if different from the correct parity. If the current and correct
        # parity are the same, it doesn't mean there are no errors, it only means there is an even
        # number (potentially zero) number of errors. In that case we don't attempt to correct and
        # instead we "hope" that the error will be caught in another shuffle of the key.
        if self.error_parity != Block.ERRORS_ODD:
            return None

        # If this block contains a single bit, we have finished the recursion and found an error.
        if self.size == 1:

            # Fix the error by flipping the one and only bit in this block.
            flipped_shuffle_index = self._start_index
            self._shuffle.flip_bit(self._key, flipped_shuffle_index)

            # For every block that covers the key bit that was corrected...
            flipped_key_index = self._shuffle.get_key_index(flipped_shuffle_index)
            for block in self._session.get_blocks_containing_key_index(flipped_key_index):

                # Flip the parity of that block.
                block.flip_parity()

                # Perform the "Cascade effect" that is at the heart of the Cascade algorithm:
                # If the block now has an odd number of errors, register it as an error block so we
                # can go and correct it later on. The blocks from this iteration don't end up being
                # registered here - since we corrected an odd error they always have an even number
                # of errors at this point in the loop. Instead, it's blocks from previous iterations
                # in the Cascade algorithm that end up being registered here.
                if block.error_parity == Block.ERRORS_ODD:
                    self._session.register_error_block(block)

            # We corrected one error. Return the shuffle index of the corrected bit.
            return flipped_shuffle_index

        # Split the block into two sub-blocks. Since the whole block contains an odd number of
        # errors, either the first sub-block contains an odd number of errors and the second
        # sub-block contains an even number of errors, or vice versa. Recursively check each of
        # the two sub-blocks. Whichever one has the odd number of errors will recurse more deeply
        # until we find a single bit error and fix it.
        left_sub_block = self.get_left_sub_block()
        corrected_shuffle_index = left_sub_block.correct_one_bit(ask_correct_parity_function)
        if corrected_shuffle_index is None:

            # The left sub-block had an even number of errors. So that means that the right
            # sub-block must contain an odd number of errors. Recurse deeper into the right
            # sub-block.
            right_sub_block = self.get_right_sub_block()
            corrected_shuffle_index = right_sub_block.correct_one_bit(ask_correct_parity_function)

        else:

            # The left sub-block had an odd number of errors. We know for a fact that the right
            # sub-block has an even number of errors, so we don't need to recurse any deeper into
            # the right sub-block. Not recursing avoid an unnecessary and potentially expensive call
            # to ask_correct_parity_function.
            pass

        # Since the entire block had an odd number of errors, we must have corrected one error in
        # either the left sub-block or the right sub-block.
        assert corrected_shuffle_index is not None
        return corrected_shuffle_index

    def flip_parity(self):
        """
        Flip the current parity of this block. This is needed when a single bit in the block is
        flipped as a result of a single bit error correction.
        """
        # TODO: Add stand-alone unit test case
        # TODO: Cascade priority queue (do this in flip_parity)
        self._current_parity = 1 - self._current_parity
