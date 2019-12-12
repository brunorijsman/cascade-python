import heapq
# Can't do "from bb84.cascade.block import Block" because of circular import
# pylint:disable=cyclic-import
import bb84.cascade.block

class Session:
    """
    A Cascade session. Represents the state of a single information reconciliation exchange in
    progress between a client and a server. This state is stored in an object to allow multiple
    information reconciliation sessions to happen concurrently and still keep their state separate.
    """

    def __init__(self):
        """
        Create a Cascade session.
        """

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
        # Validate args.
        assert isinstance(block, bb84.cascade.block.Block)

        # Push the error block onto the heap. It is pushed as a tuple (block.size, block) to allow
        # us to correct the error blocks in order of shortest blocks first.
        # TODO test case
        heapq.heappush(self._error_blocks, (block.size, block))

    def correct_registered_error_blocks(self):
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
                assert block.correct_one_bit() is not None

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

    def correct_key(self, key, _estimated_quantum_bit_error_rate, _parameters):
        """
        Run the Cascade algorithm to correct the provided key.

        Args:
            key (Key): The key to be corrected.
            estimated_quantum_bit_error_rate: The estimated quantum bit error rate.
            parameters (Parameters): The parameters that describe the variation of the Cascade
                algorithm.

        Returns:
            The corrected key. There is still a small but non-zero chance that the corrected key
            still contains errors.
        """
        # TODO: pylint:disable=no-self-use
        return key
