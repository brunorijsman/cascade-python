import heapq
from bb84.cascade.block import Block
from bb84.cascade.classical_channel import ClassicalChannel
from bb84.cascade.key import Key
from bb84.cascade.parameters import Parameters
from bb84.cascade.shuffle import Shuffle
from bb84.cascade.stats import Stats

class Reconciliation:
    """
    A single information reconciliation exchange between a client (Bob) and a server (Alice).
    """

    def __init__(self, parameters, classical_channel, noisy_key, estimated_quantum_bit_error_rate):
        """
        Create a Cascade reconciliation.

        Args:
            parameters (Parameters): The parameters that describe the variation of the Cascade
                algorithm.
            classical_channel (subclass of ClassicalChannel): The classical channel over which
                Bob communicates with Alice.
        """

        # Validate arguments.
        assert isinstance(parameters, Parameters)
        assert issubclass(type(classical_channel), ClassicalChannel)
        assert isinstance(noisy_key, Key)
        assert isinstance(estimated_quantum_bit_error_rate, float)

        # Store the arguments.
        self._classical_channel = classical_channel
        self._parameters = parameters
        self._estimated_quantum_bit_error_rate = estimated_quantum_bit_error_rate

        # At the start, this contains the noisy key. As the Cascade algorithm progresses, this key
        # is updated ("reconciliated"). At the end of the Cascade algorithm it likely (but not
        # surely) contains the correct key.
        self._key = noisy_key

        # Map key indexes to blocks.
        self._key_index_to_blocks = {}

        # Keep track of statistics.
        self.stats = Stats()

        # A set of blocks that are suspected to contain an error, pending to be corrected later.
        # These are stored as a priority queue with items (block.size, block) so that we can correct
        # the pending blocks in order of shortest block first.
        self._error_blocks = []

    def get_key(self):
        return self._key

    def _register_block_key_indexes(self, block):
        """
        Register the key indexes that are covered by this block. Later on, given a key index, we
        will be able to find all blocks covering that key index efficiently.

        Args:
            block (Block): The block to be registered. It must not have been registered using this
            function ever before.
        """

        # Validate args.
        assert isinstance(block, Block)

        # For every key bit covered by the block, append the block to the list of blocks that depend
        # on that partical key bit.
        for key_index in block.get_key_indexes():
            if key_index in self._key_index_to_blocks:
                assert block not in self._key_index_to_blocks[key_index]   # TODO: Get rid of this
                self._key_index_to_blocks[key_index].append(block)
            else:
                self._key_index_to_blocks[key_index] = [block]

    def _get_blocks_containing_key_index(self, key_index):
        """
        Get a list of block that contain a given key index.

        Args:
            key_index (int): The key index that we are looking for.

        Returns:
            The list of block that contain a given key index.
        """
        assert isinstance(key_index, int)
        assert key_index >= 0
        return self._key_index_to_blocks.get(key_index, [])

    def _register_error_block(self, block):
        """
        Register a block as having an odd number of errors. The blocks that are registered as error
        blocks can later be corrected by calling correct_registered_error_blocks.

        Args:
            block (Block): The block to be registered as an error block. It is legal to register
            the same block multiple times using this function.
        """
        # TODO add unit test

        # Validate args.
        assert isinstance(block, Block)

        # If sub_block_reuse is disabled, then only register top-level blocks for cascading.
        # TODO: Move this to caller!
        if not self._parameters.sub_block_reuse:
            if not block.is_top_block():
                return

        # Push the error block onto the heap. It is pushed as a tuple (block.size, block) to allow
        # us to correct the error blocks in order of shortest blocks first.
        heapq.heappush(self._error_blocks, (block.get_size(), block))

    def _correct_registered_error_blocks(self):
        """
        For each registered error blocks, attempt to correct a single error in the block. The blocks
        are processed in order of shortest block first.
        """
        # Process each error block, in order of shortest block first.
        while self._error_blocks:
            (_, block) = heapq.heappop(self._error_blocks)
            # We only attempt to correct one error if the block contains an odd number of error.
            # Although we only call register_error_block for blocks with an odd number of errors,
            # it is perfectly possible for the block to have an even number of errors by the time
            # we get the this point for a number of reasons:
            # (1) The block could be registered as an error block multiple time. In that case the
            #     blocks ends up in the queue twice. When the first queue entry is corrected the
            #     block turns from an odd number of errors to an even number of errors. Thus, when
            #     the second entry on the queue is processed it will have an even number of errors.
            # (2) After a super-block has been registered as an error block (odd number of errors)
            #     an error in some sub-block is corrected. This causes the parity of the super-block
            #     to flip, and hence the number of errors to chang from odd to even.
            # We don't attempt to fix (1) by checking whether the block is already in the priority
            # queue, and we don't attempt to fix (2) by removing the super-block from the priority
            # queue when its parity flips. Those fixes would be much more expensive than what we do
            # here: we simply ignore blocks on the queue that have an even number of errors at the
            # time that they are popped from the priority queue.
            if block.get_error_parity() == Block.ERRORS_ODD:
                assert self._correct_one_bit_in_block(block) is not None

    def reconcile(self):
        """
        Run the Cascade algorithm to reconciliate our ("Bob's") noisy key with the server's
        ("Alice's") correct key.

        Returns:
            The corrected key. There is still a small but non-zero chance that the corrected key
            still contains errors.
        """

        # Inform Alice that we are starting a new reconciliation.
        self._classical_channel.start_reconciliation()

        # Do as many Cascade iterations (aka Cascade passes) as demanded by this particular
        # variation of the Cascade algorithm.
        for iteration in range(1, self._parameters.nr_iterations+1):

            # Determine the block size to be used for this iteration, using the rules for this
            # particular variation of the Cascade algorithm.
            block_size = self._parameters.block_size_function(
                self._estimated_quantum_bit_error_rate, iteration)

            # In the first iteration, we don't shuffle the key. In all subsequent iterations we
            # shuffle the key, using a different random shuffling in each iteration.
            if iteration == 1:
                shuffle = Shuffle(self._key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
            else:
                shuffle = Shuffle(self._key.get_size(), Shuffle.SHUFFLE_RANDOM)

            # Split the shuffled key into blocks, using the block size that we chose.
            blocks = Block.create_covering_blocks(self._key, shuffle, block_size)

            # Register all blocks in the key index to block map (we need to do this before we start
            # correcting any bit errors)
            for block in blocks:
                self._register_block_key_indexes(block)

            # Visit each block.
            for block in blocks:

                # Potentially correct one error in the block. This is a no-operation if the block
                # happens to have an even (potentially zero) number of errors.
                _corrected_shuffle_index = self._correct_one_bit_in_block(block)

                # Cascade effect: if we fixed an error, then one bit flipped, and one or more blocks
                # from previous iterations could now have an odd number of errors. Re-visit those
                # blocks and correct one error in them.
                self._correct_registered_error_blocks()

        # Inform Alice that we have finished the reconciliation.
        self._classical_channel.end_reconciliation()

        # Return the probably, but not surely, corrected key.
        return self._key

    def _correct_one_bit_in_block(self, block):
        """
        Try to correct a single bit error in a block by recursively dividing the block into
        sub-blocks and comparing the current parity of each of those sub-blocks with the correct
        parity of the same sub-block.

        Params:
            block (Block): The block in which we attempt to correct one bit error.

        Returns:
            The shuffle_index of the correct bit, or None if no bit was corrected.
        """


        # If we don't already know the correct parity for this block, ask Alice what it is.
        if block.get_correct_parity() is None:
            # TODO: This will get cleaned up after we parallelize (i.e. gather multiple parity
            # questions into one message).
            shuffle_range = block.get_shuffle_range()
            shuffle_ranges = [shuffle_range]
            correct_parity = self._classical_channel.ask_parities(shuffle_ranges)[0]
            block.set_correct_parity(correct_parity)

        # We only attempt to correct a bit error if there is an odd number of errors, i.e. if
        # the current parity if different from the correct parity. If the current and correct
        # parity are the same, it doesn't mean there are no errors, it only means there is an even
        # number (potentially zero) number of errors. In that case we don't attempt to correct and
        # instead we "hope" that the error will be caught in another shuffle of the key.
        if block.get_error_parity() != Block.ERRORS_ODD:
            return None

        # If this block contains a single bit, we have finished the recursion and found an error.
        if block.get_size() == 1:

            # Fix the error by flipping the one and only bit in this block.
            flipped_shuffle_index = block.get_start_index()
            block.flip_bit(flipped_shuffle_index)

            # For every block that covers the key bit that was corrected...
            flipped_key_index = block.get_key_index(flipped_shuffle_index)
            for affected_block in self._get_blocks_containing_key_index(flipped_key_index):

                # Flip the parity of that block.
                affected_block.flip_parity()

                # Perform the "Cascade effect" that is at the heart of the Cascade algorithm:
                # If the block now has an odd number of errors, register it as an error block so we
                # can go and correct it later on. The blocks from this iteration don't end up being
                # registered here - since we corrected an odd error they always have an even number
                # of errors at this point in the loop. Instead, it's blocks from previous iterations
                # in the Cascade algorithm that end up being registered here.
                if affected_block.get_error_parity() == Block.ERRORS_ODD:
                    self._register_error_block(affected_block)

            # We corrected one error. Return the shuffle index of the corrected bit.
            return flipped_shuffle_index

        # If we get here, it means that the block was bigger than 1 bit.

        # Split the block into two sub-blocks. Since the whole block contains an odd number of
        # errors, either the first sub-block contains an odd number of errors and the second
        # sub-block contains an even number of errors, or vice versa. Recursively check each of
        # the two sub-blocks. Whichever one has the odd number of errors will recurse more deeply
        # until we find a single bit error and fix it.
        # TODO: More granular comments.
        left_sub_block = block.get_left_sub_block()
        if  left_sub_block is None:
            left_sub_block = block.create_left_sub_block()
            self._register_block_key_indexes(left_sub_block)
        corrected_shuffle_index = self._correct_one_bit_in_block(left_sub_block)
        if corrected_shuffle_index is None:

            # The left sub-block had an even number of errors. So that means that the right
            # sub-block must contain an odd number of errors. Recurse deeper into the right
            # sub-block.
            right_sub_block = block.get_right_sub_block()
            if right_sub_block is None:
                right_sub_block = block.create_right_sub_block()
                self._register_block_key_indexes(right_sub_block)
            corrected_shuffle_index = self._correct_one_bit_in_block(right_sub_block)

        else:

            # The left sub-block had an odd number of errors. We know for a fact that the right
            # sub-block has an even number of errors, so we don't need to recurse any deeper into
            # the right sub-block.
            pass

        # Since the entire block had an odd number of errors, we must have corrected one error in
        # either the left sub-block or the right sub-block.
        assert corrected_shuffle_index is not None
        return corrected_shuffle_index
