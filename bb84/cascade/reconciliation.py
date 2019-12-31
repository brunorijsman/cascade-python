import copy
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

    def __init__(self, parameters, classical_channel, noisy_key, estimated_quantum_bit_error_rate,
                 stats=None):
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
        self._noisy_key = noisy_key
        self._reconciled_key = None

        # Map key indexes to blocks.
        self._key_index_to_blocks = {}

        # Keep track of statistics. Use the provided stats block, or if none was provided, create
        # new stats block.
        if stats is None:
            self.stats = Stats()
        else:
            self.stats = stats

        # A set of blocks that are suspected to contain an error, pending to be corrected later.
        # These are stored as a priority queue with items (block.size, block) so that we can correct
        # the pending blocks in order of shortest block first.
        self._pending_try_correct = []

        # A set of blocks for which we have to ask Alice for the correct parity. To minimize the
        # number of message that Bob sends to Alice (i.e. the number of channel uses), we queue up
        # these pending parity questions until we can make no more progress correcting error. Then
        # we send a single message to Alice to ask all queued parity questions, and proceed once we
        # get the answers.
        self._pending_ask_correct_parity = []

    def get_noisy_key(self):
        return self._noisy_key

    def get_reconciled_key(self):
        return self._reconciled_key

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


    def _determine_error_parity_and_schedule_next_step(self, block, correct_right_sibling):
        ###@@@
        pass

    def _schedule_ask_correct_parity(self, block, correct_right_sibling):
        """
        Register a block as needing to ask Alice what the correct parity is.

        Args:
            block (Block): The block to be registered.
        """
        # Validate args.
        assert isinstance(block, Block)

        # Adding an item to the end (not the start!) of a list is an efficient O(1) operation.
        entry = (block, correct_right_sibling)
        self._pending_ask_correct_parity.append(entry)

    def _have_pending_ask_correct_parity(self):
        """
        Are there any more blocks pending as needing to ask Alice what the correct parity is?

        Returns:
            True if there are any pending error blocks, False if not.
        """
        return self._pending_ask_correct_parity != []

    def _service_pending_ask_correct_parity(self):
        """
        Send a single message to Alice, asking for the parities of all pending "ask parity" blocks.
        When Alice answers (currently this is a blocking synchronous question) we update the
        correct parity for the block (0 or 1), the error parity of the block (odd of even), and
        if the error parity turns out to be odd, we add to the priority queue for pending error
        blocks that we need to attempt to correct.
        """

        if not self._pending_ask_correct_parity:
            return

        # Prepare the question for Alice, i.e. the list of shuffle ranges over which we want Alice
        # to compute the correct parity.
        shuffle_ranges = []
        for entry in self._pending_ask_correct_parity:
            (block, _correct_right_sibling) = entry
            shuffle_range = block.get_shuffle_range()
            shuffle_ranges.append(shuffle_range)

        # "Send a message" to Alice to ask her to compute the correct parities for the list that
        # we prepared. For now, this is a synchronous blocking operations (i.e. we block here
        # until we get the answer from Alice).
        correct_parities = self._classical_channel.ask_parities(shuffle_ranges)

        # Process the answer from Alice. IMPORTANT: Alice is required to send the list of parities
        # in the exact same order as the ranges in the question; this allows us to zip.
        for (correct_parity, entry) in zip(correct_parities, self._pending_ask_correct_parity):
            (block, correct_right_sibling) = entry
            block.set_correct_parity(correct_parity)
            self._schedule_try_correct(block, correct_right_sibling)

        # Clear the list of pending questions.
        self._pending_ask_correct_parity = []

    def _schedule_try_correct(self, block, correct_right_sibling):
        """
        Register a block as needing an attempted error correct. Either because we know for a fact
        that it has an odd number of errors. Or because we don't yet know its correct parity, so
        it might turn out to have an odd number of errors.

        Args:
            block (Block): The block to be registered as an error block. It is legal to register
            the same block multiple times using this function.
        """
        # Validate args.
        assert isinstance(block, Block)

        # Push the error block onto the heap. It is pushed as a tuple (block.size, block) to allow
        # us to correct the error blocks in order of shortest blocks first.
        entry = (block, correct_right_sibling)
        heapq.heappush(self._pending_try_correct, (block.get_size(), entry))

    def _have_pending_try_correct(self):
        """
        Are there any more blocks pending that potentially have an odd number of errors?

        Returns:
            True if there are any pending error blocks, False if not.
        """
        return self._pending_try_correct != []

    def _service_pending_try_correct(self):
        """
        For each registered error blocks, attempt to correct a single error in the block. The blocks
        are processed in order of shortest block first.
        """
        # Process each error block, in order of shortest block first.
        while self._pending_try_correct:
            (_, entry) = heapq.heappop(self._pending_try_correct)
            (block, correct_right_sibling) = entry
            self._try_correct(block, correct_right_sibling)

    def reconcile(self):
        """
        Run the Cascade algorithm to reconciliate our ("Bob's") noisy key with the server's
        ("Alice's") correct key.

        Returns:
            The corrected key. There is still a small but non-zero chance that the corrected key
            still contains errors.
        """

        self._reconciled_key = copy.deepcopy(self._noisy_key)

        # Inform Alice that we are starting a new reconciliation.
        self._classical_channel.start_reconciliation()

        # Do as many Cascade iterations (aka Cascade passes) as demanded by this particular
        # variation of the Cascade algorithm.
        for iteration_nr in range(1, self._parameters.nr_iterations+1):
            self._reconcile_iteration(iteration_nr)

        # Inform Alice that we have finished the reconciliation.
        self._classical_channel.end_reconciliation()

        # Return the probably, but not surely, corrected key.
        return self._reconciled_key

    def _reconcile_iteration(self, iteration_nr):

        # Determine the block size to be used for this iteration, using the rules for this
        # particular variation of the Cascade algorithm.
        block_size = self._parameters.block_size_function(self._estimated_quantum_bit_error_rate,
                                                          iteration_nr)

        # In the first iteration, we don't shuffle the key. In all subsequent iterations we
        # shuffle the key, using a different random shuffling in each iteration.
        if iteration_nr == 1:
            shuffle = Shuffle(self._reconciled_key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
        else:
            shuffle = Shuffle(self._reconciled_key.get_size(), Shuffle.SHUFFLE_RANDOM)

        # Split the shuffled key into blocks, using the block size that we chose.
        blocks = Block.create_covering_blocks(self._reconciled_key, shuffle, block_size)

        # For each top-level covering block...
        for block in blocks:

            # Update the key index to block map.
            self._register_block_key_indexes(block)

            # We won't be able to do anything with the top-level covering blocks until we know what
            # the correct parity it.
            self._schedule_ask_correct_parity(block, False)

        # Keep going while there is more work to do.
        while self._have_pending_try_correct() or self._have_pending_ask_correct_parity():

            # Attempt to correct all of blocks that are currently pending as needing a correction
            # attempt. If we don't know the correct parity of the block, we won't be able to finish
            # the attempted correction yet. In that case the block will end up on the "pending ask
            # parity" list.
            self._service_pending_try_correct()

            # Now, ask Alice for the correct parity of the blocks that ended up on the "ask parity
            # list" in the above loop. When we get the answer from Alice, we may discover that the
            # block as an odd number of errors, in which case we add it back to the "pending error
            # block" priority queue.
            self._service_pending_ask_correct_parity()

    def _try_correct(self, block, correct_right_sibling):
        """
        Try to correct a single bit error in a block by recursively dividing the block into
        sub-blocks and comparing the current parity of each of those sub-blocks with the correct
        parity of the same sub-block.

        Params:
            block (Block): The block in which we attempt to correct one bit error.
            correct_sibbling (bool): If block contains an even number of errors, then try to correct
                an error in the right sibling instead of this block.

        Returns:
            True if an error was corrected, False if not.
        """

        # If we don't know the correct parity of the block, we cannot make progress on this block
        # until Alice has told us what the correct parity is.
        if block.get_correct_parity() is None:
            self._schedule_ask_correct_parity(block, correct_right_sibling)
            return False

        # If there is an even number of errors in this block, we don't attempt to fix any errors
        # in this block. But if asked to do so, we will attempt to fix an error in the right
        # sibling block.
        error_parity = block.get_error_parity()
        assert error_parity != Block.ERRORS_UNKNOWN
        if block.get_error_parity() == Block.ERRORS_EVEN:
            if correct_right_sibling:
                return self._try_correct_right_sibling_block(block)
            return False

        # If this block contains a single bit, we have finished the recursion and found an error.
        # Correct the error by flipping the key bit that corresponds to this block.
        if block.get_size() == 1:
            self._flip_key_bit_corresponding_to_single_bit_block(block)
            return True

        # If we get here, it means that there is an odd number of errors in this block and that
        # the block is bigger than 1 bit.

        # Recurse to try to correct an error in the left sub-block first, and if there is no error
        # there, in the right sub-block alternatively.
        left_sub_block = block.get_left_sub_block()
        if  left_sub_block is None:
            left_sub_block = block.create_left_sub_block()
            self._register_block_key_indexes(left_sub_block)
        return self._try_correct(left_sub_block, True)

    def _try_correct_right_sibling_block(self, block):

        assert not block.is_top_block()

        parent_block = block.get_parent_block()
        right_sibling_block = parent_block.get_right_sub_block()
        if right_sibling_block is None:
            right_sibling_block = parent_block.create_right_sub_block()
            self._register_block_key_indexes(right_sibling_block)
        return self._try_correct(right_sibling_block, False)

    def _flip_key_bit_corresponding_to_single_bit_block(self, block):

        assert block.get_size() == 1
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
            # TODO: Better comment here
            if affected_block.get_error_parity() != Block.ERRORS_EVEN:

                # If sub_block_reuse is disabled, then only register top-level blocks for
                # cascading.
                if self._parameters.sub_block_reuse or affected_block.is_top_block():
                    self._schedule_try_correct(affected_block, False)
