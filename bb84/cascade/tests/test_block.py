import pytest
from bb84.cascade.block import Block
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

def test_create_validate_args():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)
    key = Key.create_random_key(8)
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    with pytest.raises(AssertionError):
        Block("hello", shuffle, 0, 1)
    with pytest.raises(AssertionError):
        Block(key, "hello", 0, 1)
    with pytest.raises(AssertionError):
        Block(key, shuffle, -1, 1)
    with pytest.raises(AssertionError):
        Block(key, shuffle, 8, 1)
    with pytest.raises(AssertionError):
        Block(key, shuffle, "hello", 1)
    with pytest.raises(AssertionError):
        Block(key, shuffle, 3, -1)
    with pytest.raises(AssertionError):
        Block(key, shuffle, 3, 9)
    with pytest.raises(AssertionError):
        Block(key, shuffle, 3, 2)

def test_create_block():

    Key.set_random_seed(2221)
    Shuffle.set_random_seed(2222)

    # Special case: block covers entire shuffle
    key = Key.create_random_key(8)
    assert key.__repr__() == "Key: 10111010"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2 1->3 2->5 3->6 4->4 5->0 6->7 7->1"
    block = Block(key, shuffle, 3, 6)
    assert block.__repr__() == "Block: 3->6=1 4->4=1 5->0=1"
    block = Block(key, shuffle, 0, 8)
    assert block.__repr__() == "Block: 0->2=1 1->3=1 2->5=0 3->6=1 4->4=1 5->0=1 6->7=0 7->1=0"

    # Special case: single bit block
    block = Block(key, shuffle, 2, 3)
    assert block.__repr__() == "Block: 2->5=0"

    # Special case: empty block
    with pytest.raises(AssertionError):
        block = Block(key, shuffle, 2, 2)

def test_create_covering_blocks():

    Key.set_random_seed(3331)
    Shuffle.set_random_seed(3332)
    key = Key.create_random_key(16)
    assert key.__repr__() == "Key: 0011011001100110"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == ("Shuffle: 0->4 1->10 2->6 3->5 4->15 5->12 6->7 7->9 "
                                  "8->0 9->14 10->11 11->8 12->3 13->2 14->13 15->1")

    # Multiple blocks, last block is partially filled
    blocks = Block.create_covering_blocks(key, shuffle, 5)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->10=1 2->6=1 3->5=1 4->15=0"
    assert blocks[1].__repr__() == "Block: 5->12=0 6->7=0 7->9=1 8->0=0 9->14=1"
    assert blocks[2].__repr__() == "Block: 10->11=0 11->8=0 12->3=1 13->2=1 14->13=1"
    assert blocks[3].__repr__() == "Block: 15->1=0"

    # Multiple blocks, last block is fully filled
    blocks = Block.create_covering_blocks(key, shuffle, 4)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->10=1 2->6=1 3->5=1"
    assert blocks[1].__repr__() == "Block: 4->15=0 5->12=0 6->7=0 7->9=1"
    assert blocks[2].__repr__() == "Block: 8->0=0 9->14=1 10->11=0 11->8=0"
    assert blocks[3].__repr__() == "Block: 12->3=1 13->2=1 14->13=1 15->1=0"

    # Single block, partially filled
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2 1->3 2->1 3->0"
    blocks = Block.create_covering_blocks(key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

    # Single block, fully filled
    blocks = Block.create_covering_blocks(key, shuffle, 4)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

def test_repr():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2 1->3 2->1 3->0"
    blocks = Block.create_covering_blocks(key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

def test_str():
    Key.set_random_seed(55511)
    Shuffle.set_random_seed(55522)
    key = Key.create_random_key(4)
    assert key.__str__() == "1010"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->0 1->1 2->3 3->2"
    blocks = Block.create_covering_blocks(key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__str__() == "1001"

def test_size():
    Key.set_random_seed(5551)
    Shuffle.set_random_seed(5552)
    key = Key.create_random_key(65)
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_covering_blocks(key, shuffle, 30)
    assert len(blocks) == 3
    assert blocks[0].size == 30
    assert blocks[1].size == 30
    assert blocks[2].size == 5

def test_current_parity():

    Key.set_random_seed(6661)
    Shuffle.set_random_seed(6662)

    # Even parity block.
    key = Key.create_random_key(10)
    assert key.__str__() == "0111101111"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->8 1->1 2->0 3->2 4->3 5->4 6->7 7->9 8->5 9->6"
    blocks = Block.create_covering_blocks(key, shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "1101111101"
    assert block.current_parity == 0

    # Odd parity block.
    key = Key.create_random_key(12)
    assert key.__str__() == "010100111101"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->1 1->8 2->10 3->9 4->0 5->6 6->7 7->5 8->2 9->3 10->11 11->4"
    blocks = Block.create_covering_blocks(key, shuffle, 12)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "110101100110"
    assert block.current_parity == 1

    # Split block into sub-blocks.
    left_sub_block = block.get_left_sub_block()
    right_sub_block = block.get_right_sub_block()

    # Even parity sub-block.
    assert left_sub_block.__str__() == "110101"
    assert left_sub_block.current_parity == 0

    # Odd parity sub-block.
    assert right_sub_block.__str__() == "100110"
    assert right_sub_block.current_parity == 1

def test_get_sub_blocks():

    Key.set_random_seed(7771)
    Shuffle.set_random_seed(7772)

    # Prepare a 10-bit block.
    key = Key.create_random_key(10)
    assert key.__str__() == "0100110001"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->3 1->2 2->6 3->1 4->7 5->0 6->4 7->9 8->8 9->5"
    blocks = Block.create_covering_blocks(key, shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "0001001101"

    # Get the left sub-block.
    left_sub_block = block.get_left_sub_block()
    assert left_sub_block.__str__() == "00010"

    # Get the left sub-block again (under the hood, a different code path is used for the 2nd get.)
    left_sub_block = block.get_left_sub_block()
    assert left_sub_block.__str__() == "00010"

    # Get the right sub-block.
    right_sub_block = block.get_right_sub_block()
    assert right_sub_block.__str__() == "01101"

    # Get the sight sub-block again (under the hood, a different code path is used for the 2nd get.)
    right_sub_block = block.get_right_sub_block()
    assert right_sub_block.__str__() == "01101"

    # Split right sub-block with odd number of bits into sub-sub-blocks.
    left_sub_sub_block = right_sub_block.get_left_sub_block()
    right_sub_sub_block = right_sub_block.get_right_sub_block()
    assert left_sub_sub_block.__str__() == "011"
    assert right_sub_sub_block.__str__() == "01"

    # Split left sub-sub-block with odd number of bits into sub-sub-sub-blocks.
    left_sub_sub_sub_block = left_sub_sub_block.get_left_sub_block()
    right_sub_sub_sub_block = left_sub_sub_block.get_right_sub_block()
    assert left_sub_sub_sub_block.__str__() == "01"
    assert right_sub_sub_sub_block.__str__() == "1"

    # Not allowed to split a block of size 1.
    with pytest.raises(AssertionError):
        right_sub_sub_sub_block.get_left_sub_block()
    with pytest.raises(AssertionError):
        right_sub_sub_sub_block.get_right_sub_block()

def test_clear_history():

    Block.clear_history()
    Key.set_random_seed(12345)
    Shuffle.set_random_seed(67890)

    # Set key index to block map to known state.
    key = Key.create_random_key(5)
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    block = Block(key, shuffle, 0, 3)
    assert block.__repr__() == ("Block: 0->3=1 1->2=1 2->1=0")
    assert Block.get_blocks_containing_key_index(0) == []
    assert Block.get_blocks_containing_key_index(1) == [block]
    assert Block.get_blocks_containing_key_index(2) == [block]
    assert Block.get_blocks_containing_key_index(3) == [block]
    assert Block.get_blocks_containing_key_index(4) == []
    assert Block.get_blocks_containing_key_index(5) == []

    # Clear key index to block map.
    Block.clear_history()
    for key_index in range(0, 6):
        assert Block.get_blocks_containing_key_index(key_index) == []

def test_get_blocks_containing_key_index():

    Block.clear_history()
    Key.set_random_seed(9991)
    Shuffle.set_random_seed(9992)

    # A block that contains only key bits 1, 3, and 4
    key1 = Key.create_random_key(5)
    assert key1.__repr__() == "Key: 00011"
    shuffle1 = Shuffle(key1.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle1.__repr__() == ("Shuffle: 0->1 1->4 2->3 3->0 4->2")
    block1 = Block(key1, shuffle1, 0, 3)
    assert block1.__repr__() == ("Block: 0->1=0 1->4=1 2->3=1")
    assert Block.get_blocks_containing_key_index(0) == []
    assert Block.get_blocks_containing_key_index(1) == [block1]
    assert Block.get_blocks_containing_key_index(2) == []
    assert Block.get_blocks_containing_key_index(3) == [block1]
    assert Block.get_blocks_containing_key_index(4) == [block1]
    assert Block.get_blocks_containing_key_index(5) == []

    # A block that contains only key bits 0, 2, and 3
    key2 = Key.create_random_key(6)
    assert key2.__repr__() == "Key: 001001"
    shuffle2 = Shuffle(key2.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle2.__repr__() == ("Shuffle: 0->4 1->1 2->5 3->2 4->0 5->3")
    block2 = Block(key2, shuffle2, 3, 6)
    assert block2.__repr__() == ("Block: 3->2=1 4->0=0 5->3=0")
    assert Block.get_blocks_containing_key_index(0) == [block2]
    assert Block.get_blocks_containing_key_index(1) == [block1]
    assert Block.get_blocks_containing_key_index(2) == [block2]
    assert Block.get_blocks_containing_key_index(3) == [block1, block2]
    assert Block.get_blocks_containing_key_index(4) == [block1]
    assert Block.get_blocks_containing_key_index(5) == []

    # Create sub-blocks for block2
    left_sub_block = block2.get_left_sub_block()
    right_sub_block = block2.get_right_sub_block()
    assert left_sub_block.__repr__() == ("Block: 3->2=1 4->0=0")
    assert right_sub_block.__repr__() == ("Block: 5->3=0")
    assert Block.get_blocks_containing_key_index(0) == [block2, left_sub_block]
    assert Block.get_blocks_containing_key_index(1) == [block1]
    assert Block.get_blocks_containing_key_index(2) == [block2, left_sub_block]
    assert Block.get_blocks_containing_key_index(3) == [block1, block2, right_sub_block]
    assert Block.get_blocks_containing_key_index(4) == [block1]
    assert Block.get_blocks_containing_key_index(5) == []

def test_correct_one_bit_scenario_three_errors_fix_first_dont_fix_second():

    Block.clear_history()
    Key.set_random_seed(12345)
    Shuffle.set_random_seed(67890)

    # Create the original (sent) key.
    tx_key = Key.create_random_key(16)
    assert tx_key.__repr__() == "Key: 1011011010110010"

    # Create the noisy (received) key, which has 3 errors relative to the original key.
    rx_key = tx_key.copy(3)
    assert tx_key.__repr__() == "Key: 1011011010110010"
    assert rx_key.__repr__() == "Key: 1011011001110110"
                            # Errors:         ^^   ^
                            #                   111111
                            #         0123456789012345

    # Create a random shuffling.
    shuffle = Shuffle(rx_key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == ("Shuffle: 0->5 1->13 2->0 3->9 4->14 5->4 6->15 7->2 8->10 "
                                  "9->6 10->12 11->8 12->11 13->7 14->1 15->3")

    # Create a block that covers the entire shuffled noisy key.
    # The block has errors at the following shuffle indexes: 1, 3, and 11
    rx_blocks = Block.create_covering_blocks(rx_key, shuffle, rx_key.size)
    assert len(rx_blocks) == 1
    rx_block = rx_blocks[0]
    assert rx_block.__repr__() == ("Block: 0->5=1 1->13=1 2->0=1 3->9=1 4->14=1 5->4=0 6->15=0 "
                                   "7->2=1 8->10=1 9->6=1 10->12=0 11->8=0 12->11=1 13->7=0 "
                                   "14->1=0 15->3=1")
    assert rx_block.__str__() == "1111100111001001"
                        # Errors:  ^ ^       ^
                        #                   111111
                        #         0123456789012345
    assert rx_block.current_parity == 0

    # Function which returns the correct parity for a range of shuffled bits.
    ask_correct_parity_function = (
        lambda start_index, end_index: shuffle.calculate_parity(tx_key, start_index, end_index)
    )

    # Correct the first bit error. The recursion should go as follows:
    #
    #  v v          v
    # 11111001 | 11001001         Even | Odd => Recurse right
    #
    #              v
    #           1100 | 1001       Odd | Even => Recurse left
    #
    #                v
    #          11 | 00            Even | Odd => Recurse right
    #
    #                 v
    #             0 | 0           Even | Odd => Recurse right => Corrects shuffled inde 11
    #
    corrected_shuffle_index = rx_block.correct_one_bit(ask_correct_parity_function)
    assert corrected_shuffle_index == 11
    assert rx_block.__str__() == "1111100111011001"
                        # Errors:  ^ ^
                        #                   111111
                        #         0123456789012345
    assert rx_block.current_parity == 1

    # The list of blocks containing key index #8 = shuffled key index #11 should contain every block
    # that we recursed into, as shown in the above diagram.
    # pylint:disable=bad-whitespace
    blocks = Block.get_blocks_containing_key_index(8)
    assert len(blocks) == 5
    assert blocks[0].__str__() == "1111100111011001"
    assert blocks[1].__str__() ==         "11011001"
    assert blocks[2].__str__() ==         "1101"
    assert blocks[3].__str__() ==           "01"
    assert blocks[4].__str__() ==            "1"
           # Corrected bit, shuffle index 11: ^

    # Check that all parities were updated when the first error was corrected.
    assert blocks[0].current_parity == 1
    assert blocks[1].current_parity == 1
    assert blocks[2].current_parity == 1
    assert blocks[3].current_parity == 1
    assert blocks[4].current_parity == 1

    # The list of blocks containing key index #0 = shuffled key index #2 should contain the
    # following blocks:
    #  * The top block 1111100111011001 because it contains shuffled key index #2
    #  * The left half of the top block 11111001 because the recursion created that block to
    #    determine whether or not we should recurse down the left half (we ended up not doing so).
    #  * No other blocks because we ended up recursing down the right half of the top block, and
    #    none of those recursed blocks contain shuffled key index #2.
    blocks = Block.get_blocks_containing_key_index(2)
    assert len(blocks) == 2
    assert blocks[0].__str__() == "1111100111011001"
    assert blocks[1].__str__() == "11111001"
                  # Shuffle index 2: ^

    # Check the list of blocks containing key index #3 = shuffled key index #15.
    blocks = Block.get_blocks_containing_key_index(3)
    assert len(blocks) == 2
    assert blocks[0].__str__() == "1111100111011001"
    assert blocks[1].__str__() ==         "11011001"
                              # Shuffle index 15: ^

    # TODO verify prority queue of blocks. Note: not doing cascade in this test case.

    # Attempt to correct the second bit error (spoiler: it is not going to work for this shuffle).
    # The recursion should go as follows:
    #
    #  v v
    # 11111001 | 11001001         Even | Even => Recurse right
    #
    #           1101 | 1001       Even | Even => Recurse right
    #
    #                 10 | 01     Even | Even => Recurse right
    #
    #                     0 | 1   Even | Even => Recurse right => Did not find an error to correct
    #
    corrected_shuffle_index = rx_block.correct_one_bit(ask_correct_parity_function)
    assert corrected_shuffle_index is None
