from bb84.cascade.block import Block
from bb84.cascade.key import Key
from bb84.cascade.mock_classical_channel import MockClassicalChannel
from bb84.cascade.algorithm import ORIGINAL_ALGORITHM
from bb84.cascade.reconciliation import Reconciliation
from bb84.cascade.shuffle import Shuffle

def create_reconciliation(algorithm, seed, key_size, error_rate):
    Key.set_random_seed(seed)
    Shuffle.set_random_seed(seed+1)
    correct_key = Key.create_random_key(key_size)
    noisy_key = correct_key.copy(error_rate=error_rate)
    mock_classical_channel = MockClassicalChannel(correct_key)
    reconciliation = Reconciliation(algorithm, mock_classical_channel, noisy_key, error_rate)
    return reconciliation

def test_error_parity():

    # Create the original (sent) key.
    Key.set_random_seed(8881)
    Shuffle.set_random_seed(8882)
    correct_key = Key.create_random_key(16)
    assert correct_key.__repr__() == "Key: 1011111100101110"

    # Create the noisy (received) key, which has 3 errors relative to the original key.
    # pylint:disable=bad-whitespace
    noisy_key = correct_key.copy(3)
    assert correct_key.__repr__() == "Key: 1011111100101110"
    assert noisy_key.__repr__()   == "Key: 1111111110101100"
                                 # Errors:  ^      ^     ^
                                 #                   111111
                                 #         0123456789012345

    # Create a random shuffling.
    shuffle = Shuffle(noisy_key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == ("Shuffle: 0->8 1->12 2->6 3->7 4->4 5->10 6->11 7->2 8->1 9->9 "
                                  "10->15 11->0 12->13 13->3 14->5 15->14")

    # Create a block that covers the entire shuffled noisy key.
    # The block has errors at the following shuffle indexes: 2->6 8->1 14->5
    rx_blocks = Block.create_covering_blocks(noisy_key, shuffle, noisy_key.get_size())
    assert len(rx_blocks) == 1
    rx_block = rx_blocks[0]
    assert rx_block.__repr__() == ("Block: 0->8=1 1->12=1 2->6=1 3->7=1 4->4=1 5->10=1 6->11=0 "
                                   "7->2=1 8->1=1 9->9=0 10->15=0 11->0=1 12->13=1 13->3=1 14->5=1 "
                                   "15->14=0")
    assert rx_block.__str__() == "1111110110011110"   # 12 ones -> even parity
                        # Errors:  ^   ^^             # 3 errors -> odd number of errors
                        #                   111111
                        #         0123456789012345
    assert rx_block.get_current_parity() == 0

    # At this point, we have not yet corrected any error in the block.
    assert rx_block.get_error_parity() == Block.ERRORS_UNKNOWN

    # Set the actual correct parity.
    rx_block.set_correct_parity(1)
    assert rx_block.get_correct_parity() == 1

    # Now, we know we have an odd number of errors.
    assert rx_block.get_error_parity() == Block.ERRORS_ODD

    # Manually, flip one of the incorrect bits (we pick bit number 1)
    rx_block.flip_bit(1)
    assert rx_block.__str__() == "1011110110011110"

    # Flipping a bit in a block does not automatically update the parities. Do this explicitly.
    rx_block.flip_parity()

    # The current parity should also have flipped from 0 to 1
    assert rx_block.get_current_parity() == 1

    # The correct parity should still be 1
    assert rx_block.get_correct_parity() == 1

def test_get_blocks_containing_key_index():

    # Create a reconciliation object.
    reconciliation = create_reconciliation(ORIGINAL_ALGORITHM, 9991, 8, 0.1)

    # Make sure we have the noisy key that we expect to have based on the seed.
    noisy_key = reconciliation.get_noisy_key()
    assert noisy_key.__str__() == "01011001"   # Bits 1, 3, 4, and 7 are set

    # Choose a shuffling.
    shuffle1 = Shuffle(noisy_key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle1.__str__() == "0->5 1->6 2->0 3->7 4->3 5->1 6->2 7->4"

    # Create a block that covers the middle four bits (bits 2, 3, 4, 5) of the shuffled key,
    # which are bits 0, 7, 3, and 1 of the unshuffled key.
    block1 = Block(noisy_key, shuffle1, 2, 6, None)
    assert block1.__str__() == "0111"

    # Update the key bit index to block mapping.
    # pylint:disable=protected-access
    reconciliation._register_block_key_indexes(block1)

    # Verify that the correct key bit index to block mappings have been registered.
    assert reconciliation._get_blocks_containing_key_index(0) == [block1]
    assert reconciliation._get_blocks_containing_key_index(1) == [block1]
    assert reconciliation._get_blocks_containing_key_index(2) == []
    assert reconciliation._get_blocks_containing_key_index(3) == [block1]
    assert reconciliation._get_blocks_containing_key_index(4) == []
    assert reconciliation._get_blocks_containing_key_index(5) == []
    assert reconciliation._get_blocks_containing_key_index(6) == []
    assert reconciliation._get_blocks_containing_key_index(7) == [block1]

    # Choose another shuffling.
    shuffle2 = Shuffle(noisy_key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle2.__str__() == "0->0 1->6 2->7 3->1 4->3 5->2 6->5 7->4"

    # Create another block that covers the last four bits (bits 4, 5, 6, 7) of the second shuffled
    # key, which are bits 3, 2, 5, and 4 of the unshuffled key.
    block2 = Block(noisy_key, shuffle2, 4, 8, None)
    assert block2.__str__() == "1001"

    # Update the key bit index to block mapping for the second block.
    reconciliation._register_block_key_indexes(block2)

    # Verify that the correct key bit index to block mappings have been registered.
    assert reconciliation._get_blocks_containing_key_index(0) == [block1]
    assert reconciliation._get_blocks_containing_key_index(1) == [block1]
    assert reconciliation._get_blocks_containing_key_index(2) == [block2]
    assert reconciliation._get_blocks_containing_key_index(3) == [block1, block2]
    assert reconciliation._get_blocks_containing_key_index(4) == [block2]
    assert reconciliation._get_blocks_containing_key_index(5) == [block2]
    assert reconciliation._get_blocks_containing_key_index(6) == []
    assert reconciliation._get_blocks_containing_key_index(7) == [block1]

    # Create sub-blocks for block2
    left_sub_block = block2.create_left_sub_block()
    assert left_sub_block.__str__() == "10"
    right_sub_block = block2.create_right_sub_block()
    assert right_sub_block.__str__() == "01"

    # Update the key bit index to block mapping for the sub blocks.
    reconciliation._register_block_key_indexes(left_sub_block)
    reconciliation._register_block_key_indexes(right_sub_block)

    # Verify that the correct key bit index to block mappings have been registered.
    assert reconciliation._get_blocks_containing_key_index(0) == [block1]
    assert reconciliation._get_blocks_containing_key_index(1) == [block1]
    assert reconciliation._get_blocks_containing_key_index(2) == [block2, left_sub_block]
    assert reconciliation._get_blocks_containing_key_index(3) == [block1, block2, left_sub_block]
    assert reconciliation._get_blocks_containing_key_index(4) == [block2, right_sub_block]
    assert reconciliation._get_blocks_containing_key_index(5) == [block2, right_sub_block]
    assert reconciliation._get_blocks_containing_key_index(6) == []
    assert reconciliation._get_blocks_containing_key_index(7) == [block1]

# TODO: Fix this after bulking

# def test_correct_one_bit_scenario_three_errors_fix_first_dont_fix_second():

#     # Create a reconciliation object.
#     Key.set_random_seed(12345)
#     Shuffle.set_random_seed(67890)
#     correct_key = Key.create_random_key(16)
#     error_count = 3
#     noisy_key = correct_key.copy(error_count=error_count)
#     mock_classical_channel = MockClassicalChannel(correct_key)
#     error_rate = 3.0 / 16.0
#     reconciliation = Reconciliation(ORIGINAL_ALGORITHM, mock_classical_channel, noisy_key,
#                                     error_rate)

#     # Create the original (sent) key.
#     assert correct_key.__repr__() == "Key: 1011011010110010"

#     # Create the noisy (received) key, which has 3 errors relative to the original key.
#     # pylint:disable=bad-whitespace
#     assert correct_key.__repr__() == "Key: 1011011010110010"
#     assert noisy_key.__repr__()   == "Key: 1011011001110110"
#                                  # Errors:         ^^   ^
#                                  #                   111111
#                                  #         0123456789012345

#     # Create a random shuffling.
#     # pylint:disable=protected-access
#     shuffle = Shuffle(noisy_key.get_size(), Shuffle.SHUFFLE_RANDOM)
#     assert shuffle.__repr__() == ("Shuffle: 0->7 1->13 2->6 3->14 4->12 5->5 6->1 7->15 8->11 "
#                                   "9->10 10->4 11->0 12->3 13->8 14->9 15->2")
#     reconciliation._classical_channel.start_reconciliation()

#     # Create a block that covers the entire shuffled noisy key.
#     # The block has errors at the following shuffle indexes: 1, 3, and 11
#     rx_blocks = Block.create_covering_blocks(noisy_key, shuffle, noisy_key.get_size())
#     assert len(rx_blocks) == 1
#     rx_block = rx_blocks[0]
#     reconciliation._register_block_key_indexes(rx_block)
#     assert rx_block.__repr__() == ("Block: 0->7=0 1->13=1 2->6=1 3->14=1 4->12=0 5->5=1 6->1=0 "
#                                    "7->15=0 8->11=1 9->10=1 10->4=0 11->0=1 12->3=1 13->8=0 "
#                                    "14->9=1 15->2=1")
#     # Errors in shuffle bits: 13->8 14->9 1->13
#     assert rx_block.__str__() == "0111010011011011"
#                         # Errors:  ^           ^^
#                         #                   111111
#                         #         0123456789012345
#     assert rx_block.get_current_parity() == 0

#     # Pretent Alice told us what the correct parity is.
#     rx_block.set_correct_parity(1)

#     # Correct the first bit error. The recursion should go as follows:
#     #
#     #     v             vv
#     #    01110100| 11011011         Odd | Even => Recurse left
#     #
#     #    v
#     #   0111 | 0100                 Odd | Even => Recurse left
#     #
#     #   v
#     #  01 | 11                      Odd | Even => Recurse left
#     #
#     #     v
#     # 0 | 1                         Even | Odd => Recurse right => Corrects shuffled key index 1
#     #
#     assert reconciliation._try_correct_block(rx_block, False)
#     assert rx_block.__str__() == "0011010011011011"
#                         # Errors:              ^^
#                         #                   111111
#                         #         0123456789012345
#     assert rx_block.get_current_parity() == 1

#     # Since we are not doing multiple iterations in this test cases, the queue or error blocks
#     # should be empty.
#     assert reconciliation._pending_try_correct_blocks == []

#     # Since we have fixed one error, the top block will have an even number of errors for sure.
#     assert shuffle.calculate_parity(correct_key, 0, correct_key.get_size()) == \
#         rx_block.get_current_parity()

#     # Hence, attempting to fix another error on the top block will fail for sure.
#     assert not reconciliation._try_correct_block(rx_block, False)

# def run_reconciliation(algorithm, seed, key_size, error_rate, expected_bit_errors=0):
#     Key.set_random_seed(seed)
#     Shuffle.set_random_seed(seed+1)
#     correct_key = Key.create_random_key(key_size)
#     noisy_key = correct_key.copy(error_rate=error_rate)
#     mock_classical_channel = MockClassicalChannel(correct_key)
#     reconciliation = Reconciliation(algorithm, mock_classical_channel, noisy_key, error_rate)
#     reconciled_key = reconciliation.reconcile()
#     bit_errors = correct_key.difference(reconciled_key)
#     assert bit_errors == expected_bit_errors

# def test_correct_key_default_algorithm():
#     for key_size in [32, 64, 100, 1000, 10000]:
#         for bit_error_rate in [0.00, 0.01, 0.1, 0.2]:
#             run_reconciliation(ORIGINAL_ALGORITHM, 1111, key_size, bit_error_rate, 0)

# # For profiling
# # TODO: Move this to a separate profile.py and include in coverage test
# if __name__ == "__main__":
#     run_reconciliation(ORIGINAL_ALGORITHM, 1111, 10000, 0.01, 0)
