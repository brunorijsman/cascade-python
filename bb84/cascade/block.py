from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

class Block:
    """
    A block is a contiguous subset of bits in a potentially shuffled key.
    """

    _key_index_to_blocks = {}

    def __init__(self, key, shuffle, start_index, end_index):
        """
        Create a block, which is a contiguous subset of bits in a potentially shuffled key.

        Args:
            key (Key): The key for which to create one single block that covers a subset of the key.
            shuffle (Shuffle): The shuffle to apply to the key before creating the block.
            start_index (int): The shuffle index, inclusive, at which the block starts. Must be in
                range [0, shuffle.size).
            end_index (int): The shuffle index, exclusive, at which the block end. Must be in range
                [0, shuffle.size]. The range must encompass at least 1 bit, i.e.
                end_index > start_index.
        """

        # Validate arguments.
        assert isinstance(key, Key)
        assert isinstance(shuffle, Shuffle)
        assert shuffle.size == key.size
        assert isinstance(start_index, int)
        assert 0 <= start_index < shuffle.size
        assert isinstance(end_index, int)
        assert 0 <= end_index <= shuffle.size
        assert end_index > start_index

        # Store block attributes.
        self._key = key
        self._shuffle = shuffle
        self._start_index = start_index
        self._end_index = end_index

        # To detect attempts to split more than once.
        self._has_been_split = False

        # Calculate the current parity of this block.
        self._current_parity = shuffle.calculate_parity(key, start_index, end_index)

        # Update key bit to block map.
        for shuffle_index in range(self._start_index, self._end_index):
            key_index = self._shuffle.get_key_index(shuffle_index)
            if key_index in Block._key_index_to_blocks:
                Block._key_index_to_blocks[key_index].append(self)
            else:
                Block._key_index_to_blocks[key_index] = [self]

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

        # Validate arguments.
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
            block = Block(key, shuffle, start_index, end_index)
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
        left_sub_block = Block(self._key, self._shuffle, self._start_index, middle_index)
        right_sub_block = Block(self._key, self._shuffle, middle_index, self._end_index)
        return (left_sub_block, right_sub_block)

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

        # We only attempt to correct a bit error if there is an odd number of errors, i.e. if
        # the current parity if different from the correct parity. If the current and correct
        # parity are the same, it doesn't mean there are no errors, it only means there is an even
        # number (potentially zero) number of errors. In that case we don't attempt to correct and
        # instead we "hope" that the error will be caught in another shuffle of the key.
        correct_parity = ask_correct_parity_function(self._start_index, self._end_index)
        if self._current_parity == correct_parity:
            return None

        # If this block contains a single bit, we have finished the recursion and found an error.
        if self.size == 1:

            # Fix the error by flipping the one and only bit in this block.
            flipped_shuffle_index = self._start_index
            self._shuffle.flip_bit(self._key, flipped_shuffle_index)

            # Flip the parity of all blocks that contain flipped key bit (including this block).
            flipped_key_index = self._shuffle.get_key_index(flipped_shuffle_index)
            for block in Block._key_index_to_blocks[flipped_key_index]:
                block.flip_parity()

            # We fixed an error. Return the shuffle index of the corrected bit.
            return flipped_shuffle_index

        # Split the block into two sub-blocks. Since the whole block contains an odd number of
        # errors, either the first sub-block contains an odd number of errors and the second
        # sub-block contains an even number of errors, or vice versa. Recursively check each of
        # the two sub-blocks. Whichever one has the odd number of errors will recurse more deeply
        # until we find a single bit error and fix it.
        (left_sub_block, right_sub_block) = self.split()
        corrected_shuffle_index = left_sub_block.correct_one_bit(ask_correct_parity_function)
        if corrected_shuffle_index is None:

            # The left sub-block had an even number of errors. So that means that the right
            # sub-block must contain an odd number of errors. Recurse deeper into the right
            # sub-block.
            corrected_shuffle_index = right_sub_block.correct_one_bit(ask_correct_parity_function)

        else:

            # The left sub-block had an odd number of errors. We know for a fact that the right
            # sub-block has an even number of errors, so we don't need to recurse any deeper into
            # the right sub-block. Not recursing avoid an unnecesary and potentially expensive call
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

    @staticmethod
    def clear_history():
        """
        Clear all history about previously created blocks:
         * The key index to blocks map, which is used to find cascading blocks.
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
