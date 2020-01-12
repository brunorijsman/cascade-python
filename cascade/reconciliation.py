import copy
import heapq
import math
import time

from cascade.algorithm import get_algorithm_by_name
from cascade.block import Block
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

        # Store the arguments.
        self._classical_channel = classical_channel
        self._algorithm = get_algorithm_by_name(algorithm_name)
        assert self._algorithm is not None
        self._estimated_bit_error_rate = estimated_bit_error_rate
        self._noisy_key = noisy_key
        self._reconciled_key = None

        # Map key indexes to blocks.
        self._key_index_to_cascader_blocks = {}

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

    def _potentially_register_as_cascader(self, block):

        # If block is already registered as a cascader, do nothing.
        if block.is_cascader:
            return

        # Only register top-level blocks as cascaders, unless sub_block_reuse is enabled.
        if self._algorithm.sub_block_reuse or block.is_top_block:
            self._register_as_cascader(block)

    def _register_as_cascader(self, block):

        # For every key bit covered by the block, append the block to the list of cascader blocks
        # that depend on that partical key bit.
        for key_index in block.get_key_indexes():
            if key_index in self._key_index_to_cascader_blocks:
                self._key_index_to_cascader_blocks[key_index].append(block)
            else:
                self._key_index_to_cascader_blocks[key_index] = [block]

        # Avoid doing it all again if the block is registered again.
        block.is_cascader = True



    def _get_cascaded_blocks_containing_key_index(self, key_index):
        return self._key_index_to_cascader_blocks.get(key_index, [])

    def _schedule_ask_correct_parity(self, block):
        self._pending_ask_correct_parity.append(block)

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
    def _bits_in_block_ask_parity(block):
        shuffle_identifier = block.get_shuffle().get_identifier()
        shuffle_start_index = block.get_start_index()
        shuffle_end_index = block.get_end_index()
        return Reconciliation._bits_in_int(shuffle_identifier) + \
               Reconciliation._bits_in_int(shuffle_start_index) + \
               Reconciliation._bits_in_int(shuffle_end_index)

    def _service_pending_ask_correct_parity(self):

        if not self._pending_ask_correct_parity:
            return

        # Prepare the question for Alice, i.e. the list of shuffle ranges over which we want Alice
        # to compute the correct parity.
        ask_parity_blocks = []
        for block in self._pending_ask_correct_parity:
            ask_parity_blocks.append(block)
            self.stats.ask_parity_bits += self._bits_in_block_ask_parity(block)

        # "Send a message" to Alice to ask her to compute the correct parities for the list that
        # we prepared. For now, this is a synchronous blocking operations (i.e. we block here
        # until we get the answer from Alice).
        self.stats.ask_parity_messages += 1
        self.stats.ask_parity_blocks += len(ask_parity_blocks)
        correct_parities = self._classical_channel.ask_parities(ask_parity_blocks)

        # Process the answer from Alice. IMPORTANT: Alice is required to send the list of parities
        # in the exact same order as the ranges in the question; this allows us to zip.
        for (correct_parity, block) in zip(correct_parities, self._pending_ask_correct_parity):
            self.stats.reply_parity_bits += 1
            block.set_correct_parity(correct_parity)
            self._schedule_try_correct(block)

        # Clear the list of pending questions.
        self._pending_ask_correct_parity = []

    def _schedule_try_correct(self, block):
        # Push the error block onto the heap. It is pushed as a tuple (block.size, block) to allow
        # us to correct the error blocks in order of shortest blocks first.
        heapq.heappush(self._pending_try_correct, (block.get_size(), block))

    def _have_pending_try_correct(self):
        return self._pending_try_correct != []

    def _service_pending_try_correct(self, cascade):
        errors_corrected = 0
        while self._pending_try_correct:
            (_, block) = heapq.heappop(self._pending_try_correct)
            errors_corrected += self._try_correct(block, cascade)
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

        self.stats.normal_iterations += 1

        # Determine the block size to be used for this iteration, using the rules for this
        # particular algorithm of the Cascade algorithm.
        block_size = self._algorithm.block_size_function(self._estimated_bit_error_rate,
                                                         self._reconciled_key.get_size(),
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

            # Register this block as a cascader.
            self._potentially_register_as_cascader(block)

            # We won't be able to do anything with the top-level covering blocks until we know what
            # the correct parity it.
            self._schedule_ask_correct_parity(block)

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

        # If we are not cascading during BICONF, clear the key indexes to blocks map to avoid
        # wasting time keeping it up to date as correct blocks during the BICONF phase.
        if not self._algorithm.biconf_cascade:
            self._key_index_to_cascader_blocks = {}

        # Do the required number of BICONF iterations, as determined by the protocol.
        iterations_to_go = self._algorithm.biconf_iterations
        while iterations_to_go > 0:
            errors_corrected = self._one_biconf_iteration()
            if self._algorithm.biconf_error_free_streak and errors_corrected > 0:
                iterations_to_go = self._algorithm.biconf_iterations
            else:
                iterations_to_go -= 1

    def _one_biconf_iteration(self):

        self.stats.biconf_iterations += 1

        cascade = self._algorithm.biconf_cascade

        # Randomly select half of the bits in the key. This is exactly the same as doing a new
        # random shuffle of the key and selecting the first half of newly shuffled key.
        key_size = self._reconciled_key.get_size()
        shuffle = Shuffle(key_size, Shuffle.SHUFFLE_RANDOM)
        mid_index = key_size // 2
        chosen_block = Block(self._reconciled_key, shuffle, 0, mid_index)
        if cascade:
            self._potentially_register_as_cascader(chosen_block)

        # Ask Alice what the correct parity of the chosen block is.
        self._schedule_ask_correct_parity(chosen_block)

        # If the algorithm wants it, also ask Alice what the correct parity of the complementary
        # block is.
        if self._algorithm.biconf_correct_complement:
            complement_block = Block(self._reconciled_key, shuffle, mid_index, key_size)
            if cascade:
                self._potentially_register_as_cascader(complement_block)
            self._schedule_ask_correct_parity(complement_block)

        # Service all pending correction attempts (potentially including Cascaded ones) and ask
        # parity messages.
        errors_corrected = self._service_all_pending_work(cascade)
        return errors_corrected

    def _try_correct(self, block, cascade):

        # If we don't know or can infer what the correct parity is, schedule asking Alice.
        if block.get_or_infer_correct_parity() is None:
            self._schedule_ask_correct_parity(block)
            return 0

        ###@@@
        self._potentially_register_as_cascader(block)

        # If there is an even number of errors in this block, we don't attempt to fix any errors
        # in this block. But if the block has a right sibling, try to correct that one instead.
        if block.get_error_parity() == Block.ERRORS_EVEN:
            right_sibling_block = block.get_right_sibling()
            if right_sibling_block is not None:
                return self._try_correct(right_sibling_block, cascade)
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
        (left_sub_block, _right_sub_block) = block.split()
        return self._try_correct(left_sub_block, cascade)

    def _flip_key_bit_corresponding_to_single_bit_block(self, block, cascade):

        flipped_shuffle_index = block.get_start_index()
        block.flip_bit(flipped_shuffle_index)

        # For every block that covers the key bit that was corrected...
        flipped_key_index = block.get_key_index(flipped_shuffle_index)


        block.flip_parity()

        for cascaded_block in self._get_cascaded_blocks_containing_key_index(flipped_key_index):

            if cascaded_block == block:
                continue

            cascaded_block.flip_parity()
            if cascade and cascaded_block.get_error_parity() != Block.ERRORS_EVEN:
                self._schedule_try_correct(cascaded_block)
