import heapq
# Can't do "from bb84.cascade.block import Block" because of circular import, so just to an
# "import bb84.cascade.block" instead.
# pylint:disable=cyclic-import
import bb84.cascade.block
from bb84.cascade.parameters import Parameters, ORIGINAL_PARAMETERS
from bb84.cascade.shuffle import Shuffle

class Session:
    """
    A Cascade session. Represents the state of a single information reconciliation exchange in
    progress between a client and a server. This state is stored in an object to allow multiple
    information reconciliation sessions to happen concurrently and still keep their state separate.
    """

    def __init__(self, parameters=ORIGINAL_PARAMETERS):
        """
        Create a Cascade session.

        Args:
            parameters (Parameters): The parameters that describe the variation of the Cascade
                algorithm.
        """

        # Validate arguments.
        assert isinstance(parameters, Parameters)

        # Store the parameters.
        self._parameters = parameters

        # Map key indexes to blocks.
        self._key_index_to_blocks = {}

        # A collection of error blocks, pending to be corrected later. These are stored as a
        # priority queue with items (block.size, block) so that we can correct the pending blocks
        # in order of shortest block first.
        self._error_blocks = []

    def register_block(self, block):
        """
        Register the existence of a new block.

        Args:
            block (Block): The block to be registered. It must not have been registered using this
            function ever before.
        """

        # Validate args.
        assert isinstance(block, bb84.cascade.block.Block)

        # For every key bit covered by the block, append the block to the list of blocks that depend
        # on that partical key bit.
        for key_index in block.key_indexes:
            if key_index in self._key_index_to_blocks:
                assert block not in self._key_index_to_blocks[key_index]
                self._key_index_to_blocks[key_index].append(block)
            else:
                self._key_index_to_blocks[key_index] = [block]

    def get_blocks_containing_key_index(self, key_index):
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

    def register_error_block(self, block):
        """
        Register a block as having an odd number of errors. The blocks that are registered as error
        blocks can later be corrected by calling correct_registered_error_blocks.

        Args:
            block (Block): The block to be registered as an error block. It is legal to register
            the same block multiple times using this function.
        """
        # TODO add unit test

        # Validate args.
        assert isinstance(block, bb84.cascade.block.Block)

        # If sub_block_reuse is disabled, then only register top-level blocks for cascading.
        if not self._parameters.sub_block_reuse:
            if not block.is_top_block:
                return

        # Push the error block onto the heap. It is pushed as a tuple (block.size, block) to allow
        # us to correct the error blocks in order of shortest blocks first.
        heapq.heappush(self._error_blocks, (block.size, block))

    def correct_registered_error_blocks(self, ask_correct_parity_function):
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
            if block.error_parity == bb84.cascade.block.Block.ERRORS_ODD:
                assert block.correct_one_bit(ask_correct_parity_function) is not None

    def get_registered_error_blocks(self):
        """
        Get a list of registered error blocks. This is used in unit tests.

        Returns:
            A list of registered error blocks.
        """
        # TODO: Add tests case
        error_blocks_as_list = []
        for (_, error_block) in self._error_blocks:
            error_blocks_as_list.append(error_block)
        return error_blocks_as_list

    def correct_key(self, key, estimated_quantum_bit_error_rate, ask_correct_parity_function):
        """
        Run the Cascade algorithm to correct the provided key.

        Args:
            key (Key): The key to be corrected. This key is modified into the corrected key as a
            result fo calling this function. (It is also returned.)

            estimated_quantum_bit_error_rate: The estimated quantum bit error rate.

            ask_correct_parity_function: A function which takes start_shuffle_index (inclusive) and
                end_shuffle_index (exclusive) as a parameters and returns the correct parity:

                def ask_correct_parity(shuffle_identifier, start_shuffle_index, end_shuffle_index):
                    returns correct_parity

        Returns:
            The corrected key. There is still a small but non-zero chance that the corrected key
            still contains errors.
        """

        # Do as many Cascade iterations (aka Cascade passes) as demanded by this particular
        # variation of the Cascade algorithm.
        for iteration in range(1, self._parameters.nr_iterations+1):

            # Determine the block size to be used for this iteration, using the rules for this
            # particular variation of the Cascade algorithm.
            block_size = self._parameters.block_size_function(estimated_quantum_bit_error_rate,
                                                              iteration)

            # In the first iteration, we don't shuffle the key. In all subsequent iterations we
            # shuffle the key, using a different random shuffling in each iteration.
            if iteration == 1:
                shuffle = Shuffle(key.size, Shuffle.SHUFFLE_KEEP_SAME)
            else:
                shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)

            # Split the shuffled key into blocks, using the block size that we chose.
            blocks = bb84.cascade.block.Block.create_covering_blocks(self, key, shuffle,
                                                                     block_size)

            # Visit each block.
            for block in blocks:

                # Potentially correct one error in the block. This is a no-operation if the block
                # happens to have an even (potentially zero) number of errors.
                _corrected_shuffle_index = block.correct_one_bit(ask_correct_parity_function)

                # Cascade effect: if we fixed an error, then one bit flipped, and one or more blocks
                # from previous iterations could now have an odd number of errors. Re-visit those
                # blocks and correct one error in them.
                self.correct_registered_error_blocks(ask_correct_parity_function)

        # Return the probably, but not surely, corrected key.
        return key
