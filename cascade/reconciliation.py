import copy
import heapq
import math
import time
from cascade.block import Block
from cascade.classical_channel import ClassicalChannel
from cascade.key import Key
from cascade.algorithm import get_algorithm_by_name
from cascade.shuffle import Shuffle
from cascade.stats import Stats

class Reconciliation:
    """
    A single information reconciliation exchange between a client (Bob) and a server (Alice).
    """

    def __init__(self, algorithm_name, classical_channel, noisy_key, estimated_bit_error_rate):
        """
        Create a Cascade reconciliation.

        Args:
            algorithm_name (str): The name of the Cascade algorithm.
            classical_channel (subclass of ClassicalChannel): The classical channel over which
                Bob communicates with Alice.
            noisy_key (Key): The noisy key as Bob received it from Alice that needs to be
                reconciliated.
            estimated_bit_error_rate (float): The estimated bit error rate in the noisy key.
        """

        # Validate arguments.
        assert isinstance(algorithm_name, str)
        assert issubclass(type(classical_channel), ClassicalChannel)
        assert isinstance(noisy_key, Key)
        assert isinstance(estimated_bit_error_rate, float)
        algorithm = get_algorithm_by_name(algorithm_name)
        assert algorithm is not None

        # Store the arguments.
        self._classical_channel = classical_channel
        self._algorithm = algorithm
        self._estimated_bit_error_rate = estimated_bit_error_rate
        self._noisy_key = noisy_key
        self._reconciled_key = None

        # Map key indexes to blocks.
        self._key_index_to_blocks = {}

        # Keep track of statistics.
        self.stats = Stats()

        # A set of blocks that are suspected to contain an error, pending to be corrected later.
        # These are stored as a priority queue with items (block.size, block) so that we can correct
        # the pending blocks in order of shortest block first.
        self._pending_try_correct = []

        # A set of blocks for which we have to ask Alice for the correct parity. To minimize the
        # number of message that Bob sends to Alice (i.e. the number of channel uses), we queue up
        # these pending parity questions until we can make no more progress correcting errors. Then
        # we send a single message to Alice to ask all queued parity questions, and proceed once we
        # get the answers.
        self._pending_ask_correct_parity = []

    def get_noisy_key(self):
        """
        Get the noisy key, as Bob received it from Alice, that needs to be reconciled.

        Returns:
            The noisy key.
        """
        return self._noisy_key

    def get_reconciled_key(self):
        """
        Get the reconciled key, i.e. the key from which the reconciliation process attempted to
        remove the errors. There is still a small but non-zero chance that the reconciled key
        still contains errors.

        Returns:
            The reconciled key. None if the reconciliation process was not yet run.
        """
        return self._reconciled_key

    def reconcile(self):
        """
        Run the Cascade algorithm to reconciliate our ("Bob's") noisy key with the server's
        ("Alice's") correct key.

        Returns:
            The reconciled key. There is still a small but non-zero chance that the corrected key
            still contains errors.
        """

        # Start measuring process and real time.
        start_process_time = time.process_time()
        start_real_time = time.perf_counter()

        # Make a deep copy of the key, so that we continue to have access to the original noisy key.
        self._reconciled_key = copy.deepcopy(self._noisy_key)

        # Inform Alice that we are starting a new reconciliation.
        self._classical_channel.start_reconciliation()

        # Do as many normal Cascade iterations as demanded by this particular Cascade algorithm.
        self._all_normal_cascade_iterations()

        # Do as many normal BICONF iterations as demanded by this particular Cascade algorithm.
        self._all_biconf_iterations()

        # Inform Alice that we have finished the reconciliation.
        self._classical_channel.end_reconciliation()

        # Compute elapsed time.
        self.stats.elapsed_process_time = time.process_time() - start_process_time
        self.stats.elapsed_real_time = time.perf_counter() - start_real_time

        # Compute efficiencies.
        self.stats.unrealistic_efficiency = self._compute_efficiency(self.stats.ask_parity_blocks)
        realistic_reconciliation_bits = self.stats.ask_parity_bits + self.stats.reply_parity_bits
        self.stats.realistic_efficiency = self._compute_efficiency(realistic_reconciliation_bits)

        # Return the probably, but not surely, corrected key.
        return self._reconciled_key

    def _register_block_key_indexes(self, block):
        # For every key bit covered by the block, append the block to the list of blocks that depend
        # on that partical key bit.
        for key_index in block.get_key_indexes():
            if key_index in self._key_index_to_blocks:
                assert block not in self._key_index_to_blocks[key_index]   # TODO: Get rid of this
                self._key_index_to_blocks[key_index].append(block)
            else:
                self._key_index_to_blocks[key_index] = [block]

    def _get_blocks_containing_key_index(self, key_index):
        return self._key_index_to_blocks.get(key_index, [])

    def _correct_parity_is_known_or_can_be_inferred(self, block):

        # Is the parity of the block already known?
        if block.get_correct_parity() is not None:
            return True

        # Try to do a very limited type of inference, using only the parity of the parent block and
        # the sibling block.

        # Cannot infer if there is no parent block.
        parent_block = block.get_parent_block()
        if parent_block is None:
            return False

        # Cannot infer if there is no sibling block (yet).
        if parent_block.get_left_sub_block() == block:
            sibling_block = parent_block.get_right_sub_block()
        else:
            assert parent_block.get_right_sub_block() == block
            sibling_block = parent_block.get_left_sub_block()
        if sibling_block is None:
            return False

        # Cannot infer if the correct parity of the parent or sibling block are unknown.
        correct_parent_parity = parent_block.get_correct_parity()
        if correct_parent_parity is None:
            return False
        assert correct_parent_parity in [0, 1]
        correct_sibling_parity = sibling_block.get_correct_parity()
        if correct_sibling_parity is None:
            return False
        assert correct_sibling_parity in [0, 1]

        # We have everything we need. Infer the correct parity.
        if correct_parent_parity == 1:
            correct_block_parity = 1 - correct_sibling_parity
        else:
            correct_block_parity = correct_sibling_parity
        block.set_correct_parity(correct_block_parity)
        self.stats.infer_parity_blocks += 1
        return True

    def _schedule_ask_correct_parity(self, block, correct_right_sibling):
        # Adding an item to the end (not the start!) of a list is an efficient O(1) operation.
        entry = (block, correct_right_sibling)
        self._pending_ask_correct_parity.append(entry)

    def _have_pending_ask_correct_parity(self):
        return self._pending_ask_correct_parity != []

    @staticmethod
    def _bits_in_int(int_value):
        bits = 0
        while int_value != 0:
            bits += 1
            int_value //= 2
        if bits == 0:
            bits = 1
        return bits

    @staticmethod
    def _bits_in_shuffle_range(shuffle_range):
        (shuffle_identifier, shuffle_start_index, shuffle_end_index) = shuffle_range
        return Reconciliation._bits_in_int(shuffle_identifier) + \
               Reconciliation._bits_in_int(shuffle_start_index) + \
               Reconciliation._bits_in_int(shuffle_end_index)

    def _service_pending_ask_correct_parity(self):

        if not self._pending_ask_correct_parity:
            return

        # Prepare the question for Alice, i.e. the list of shuffle ranges over which we want Alice
        # to compute the correct parity.
        shuffle_ranges = []
        for entry in self._pending_ask_correct_parity:
            (block, _correct_right_sibling) = entry
            shuffle_range = block.get_shuffle_range()
            shuffle_ranges.append(shuffle_range)
            self.stats.ask_parity_bits += self._bits_in_shuffle_range(shuffle_range)

        # "Send a message" to Alice to ask her to compute the correct parities for the list that
        # we prepared. For now, this is a synchronous blocking operations (i.e. we block here
        # until we get the answer from Alice).
        self.stats.ask_parity_messages += 1
        self.stats.ask_parity_blocks += len(shuffle_ranges)
        correct_parities = self._classical_channel.ask_parities(shuffle_ranges)

        # Process the answer from Alice. IMPORTANT: Alice is required to send the list of parities
        # in the exact same order as the ranges in the question; this allows us to zip.
        for (correct_parity, entry) in zip(correct_parities, self._pending_ask_correct_parity):
            self.stats.reply_parity_bits += 1
            (block, correct_right_sibling) = entry
            block.set_correct_parity(correct_parity)
            self._schedule_try_correct(block, correct_right_sibling)

        # Clear the list of pending questions.
        self._pending_ask_correct_parity = []

    def _schedule_try_correct(self, block, correct_right_sibling):

        # Validate args.
        assert isinstance(block, Block)

        # Push the error block onto the heap. It is pushed as a tuple (block.size, block) to allow
        # us to correct the error blocks in order of shortest blocks first.
        entry = (block, correct_right_sibling)
        heapq.heappush(self._pending_try_correct, (block.get_size(), entry))

    def _have_pending_try_correct(self):
        return self._pending_try_correct != []

    def _service_pending_try_correct(self, cascade):
        errors_corrected = 0
        while self._pending_try_correct:
            (_, entry) = heapq.heappop(self._pending_try_correct)
            (block, correct_right_sibling) = entry
            errors_corrected += self._try_correct(block, correct_right_sibling, cascade)
        return errors_corrected

    def _compute_efficiency(self, reconciliation_bits):
        eps = self._estimated_bit_error_rate
        try:
            shannon_efficiency = -eps * math.log2(eps) - (1 - eps) * math.log2(1 - eps)
            key_size = self._noisy_key.get_size()
            efficiency = reconciliation_bits / (key_size * shannon_efficiency)
        except (ValueError, ZeroDivisionError):
            # TODO: Change this to NaN or None and do not plot in graph
            efficiency = 1.0
        return efficiency

    def _all_normal_cascade_iterations(self):
        for iteration_nr in range(1, self._algorithm.cascade_iterations+1):
            self._one_normal_cascade_iteration(iteration_nr)

    def _one_normal_cascade_iteration(self, iteration_nr):

        # Determine the block size to be used for this iteration, using the rules for this
        # particular algorithm of the Cascade algorithm.
        block_size = self._algorithm.block_size_function(self._estimated_bit_error_rate,
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

        # Service all pending correction attempts (including Cascaded ones) and ask parity
        # messages.
        self._service_all_pending_work(True)

    def _service_all_pending_work(self, cascade):

        # Keep track of how many errors were actually corrected in this call.
        errors_corrected = 0

        # Keep going while there is more work to do.
        while self._have_pending_try_correct() or self._have_pending_ask_correct_parity():

            # Attempt to correct all of blocks that are currently pending as needing a correction
            # attempt. If we don't know the correct parity of the block, we won't be able to finish
            # the attempted correction yet. In that case the block will end up on the "pending ask
            # parity" list.
            errors_corrected += self._service_pending_try_correct(cascade)

            # Now, ask Alice for the correct parity of the blocks that ended up on the "ask parity
            # list" in the above loop. When we get the answer from Alice, we may discover that the
            # block as an odd number of errors, in which case we add it back to the "pending error
            # block" priority queue.
            self._service_pending_ask_correct_parity()

        return errors_corrected

    def _all_biconf_iterations(self):

        # Do nothing if BICONF is disabled.
        if not self._algorithm.biconf_iterations:
            return

        # If asked to do so, keep going until we have seen the required number of "error free"
        # iterations.
        # TODO: Count BICONF iterations separately from normal iterations in stats
        iterations_to_go = self._algorithm.biconf_iterations
        while iterations_to_go > 0:
            errors_corrected = self._one_biconf_iteration()
            if self._algorithm.biconf_error_free_streak and errors_corrected > 0:
                iterations_to_go = self._algorithm.biconf_iterations
            else:
                iterations_to_go -= 1

    def _one_biconf_iteration(self):

        # Randomly select half of the bits in the key. This is exactly the same as doing a new
        # random shuffle of the key and selecting the first half of newly shuffled key.
        key_size = self._reconciled_key.get_size()
        shuffle = Shuffle(key_size, Shuffle.SHUFFLE_RANDOM)
        mid_index = key_size // 2
        chosen_block = Block(self._reconciled_key, shuffle, 0, mid_index, None)

        # Ask Alice what the correct parity of the chosen block is.
        self._schedule_ask_correct_parity(chosen_block, False)

        # If the algorithm wants it, also ask Alice what the correct parity of the complementary
        # block is.
        if self._algorithm.biconf_correct_complement:
            complement_block = Block(self._reconciled_key, shuffle, mid_index, key_size, None)
            self._schedule_ask_correct_parity(complement_block, False)

        # Service all pending correction attempts (potentially including Cascaded ones) and ask
        # parity messages.
        errors_corrected = self._service_all_pending_work(self._algorithm.biconf_cascade)
        return errors_corrected

    def _try_correct(self, block, correct_right_sibling, cascade):

        # If we don't know the correct parity of the block, we cannot make progress on this block
        # until Alice has told us what the correct parity is.
        if not self._correct_parity_is_known_or_can_be_inferred(block):
            self._schedule_ask_correct_parity(block, correct_right_sibling)
            return 0

        # If there is an even number of errors in this block, we don't attempt to fix any errors
        # in this block. But if asked to do so, we will attempt to fix an error in the right
        # sibling block.
        error_parity = block.get_error_parity()
        assert error_parity != Block.ERRORS_UNKNOWN
        if block.get_error_parity() == Block.ERRORS_EVEN:
            if correct_right_sibling:
                return self._try_correct_right_sibling_block(block, cascade)
            return 0

        # If this block contains a single bit, we have finished the recursion and found an error.
        # Correct the error by flipping the key bit that corresponds to this block.
        if block.get_size() == 1:
            self._flip_key_bit_corresponding_to_single_bit_block(block, cascade)
            return 1

        # If we get here, it means that there is an odd number of errors in this block and that
        # the block is bigger than 1 bit.

        # Recurse to try to correct an error in the left sub-block first, and if there is no error
        # there, in the right sub-block alternatively.
        left_sub_block = block.get_left_sub_block()
        if  left_sub_block is None:
            left_sub_block = block.create_left_sub_block()
            self._register_block_key_indexes(left_sub_block)
        return self._try_correct(left_sub_block, True, cascade)

    def _try_correct_right_sibling_block(self, block, cascade):

        assert not block.is_top_block()

        parent_block = block.get_parent_block()
        right_sibling_block = parent_block.get_right_sub_block()
        if right_sibling_block is None:
            right_sibling_block = parent_block.create_right_sub_block()
            self._register_block_key_indexes(right_sibling_block)
        return self._try_correct(right_sibling_block, False, cascade)

    def _flip_key_bit_corresponding_to_single_bit_block(self, block, cascade):

        assert block.get_size() == 1
        flipped_shuffle_index = block.get_start_index()
        block.flip_bit(flipped_shuffle_index)

        # For every block that covers the key bit that was corrected...
        flipped_key_index = block.get_key_index(flipped_shuffle_index)

        for affected_block in self._get_blocks_containing_key_index(flipped_key_index):

            # Flip the parity of that block.
            affected_block.flip_parity()

            # If asked to do cascading, do so for blocks with an odd number of errors.
            if cascade and affected_block.get_error_parity() != Block.ERRORS_EVEN:
                # If sub_block_reuse is disabled, then only cascade top-level blocks.
                if self._algorithm.sub_block_reuse or affected_block.is_top_block():
                    self._schedule_try_correct(affected_block, False)
