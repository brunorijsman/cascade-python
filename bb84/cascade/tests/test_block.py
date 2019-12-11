import pytest
from bb84.cascade.block import Block
from bb84.cascade.key import Key
from bb84.cascade.session import Session
from bb84.cascade.shuffle import Shuffle

def test_create_validate_args():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)
    session = Session()
    key = Key.create_random_key(8)
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    # Validate session argument.
    with pytest.raises(AssertionError):
        Block("not-a-session", key, shuffle, 0, 1)
    # Validate key argument.
    with pytest.raises(AssertionError):
        Block(session, "not-a-key", shuffle, 0, 1)
    # Validate shuffle argument.
    with pytest.raises(AssertionError):
        Block(session, key, "not-a-shuffle", 0, 1)
    # Validate start_shuffle_index argument.
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, -1, 1)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 8, 1)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, "not-an-int", 1)
    # Validate end_shuffle_index argument.
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, -1)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, 9)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, 2)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, "not-an-int")
    # Empty key.
    key = Key()
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 2, 2)

def test_create_block():

    Key.set_random_seed(2221)
    Shuffle.set_random_seed(2222)
    session = Session()

    # Block covers entire shuffle.
    key = Key.create_random_key(8)
    assert key.__repr__() == "Key: 10111010"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2 1->3 2->5 3->6 4->4 5->0 6->7 7->1"
    block = Block(session, key, shuffle, 3, 6)
    assert block.__repr__() == "Block: 3->6=1 4->4=1 5->0=1"
    block = Block(session, key, shuffle, 0, 8)
    assert block.__repr__() == "Block: 0->2=1 1->3=1 2->5=0 3->6=1 4->4=1 5->0=1 6->7=0 7->1=0"

    # Block covers part of the shuffle.
    block = Block(session, key, shuffle, 1, 3)
    assert block.__repr__() == "Block: 1->3=1 2->5=0"

    # Single bit block.
    block = Block(session, key, shuffle, 2, 3)
    assert block.__repr__() == "Block: 2->5=0"

def test_create_covering_blocks():

    Key.set_random_seed(3331)
    Shuffle.set_random_seed(3332)
    session = Session()

    # Prepare key and shuffle.
    key = Key.create_random_key(16)
    assert key.__repr__() == "Key: 0011011001100110"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == ("Shuffle: 0->4 1->10 2->6 3->5 4->15 5->12 6->7 7->9 "
                                  "8->0 9->14 10->11 11->8 12->3 13->2 14->13 15->1")

    # Multiple blocks, last block is partially filled.
    blocks = Block.create_covering_blocks(session, key, shuffle, 5)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->10=1 2->6=1 3->5=1 4->15=0"
    assert blocks[1].__repr__() == "Block: 5->12=0 6->7=0 7->9=1 8->0=0 9->14=1"
    assert blocks[2].__repr__() == "Block: 10->11=0 11->8=0 12->3=1 13->2=1 14->13=1"
    assert blocks[3].__repr__() == "Block: 15->1=0"

    # Multiple blocks, last block is fully filled.
    blocks = Block.create_covering_blocks(session, key, shuffle, 4)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->10=1 2->6=1 3->5=1"
    assert blocks[1].__repr__() == "Block: 4->15=0 5->12=0 6->7=0 7->9=1"
    assert blocks[2].__repr__() == "Block: 8->0=0 9->14=1 10->11=0 11->8=0"
    assert blocks[3].__repr__() == "Block: 12->3=1 13->2=1 14->13=1 15->1=0"

    # Single block, partially filled.
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2 1->3 2->1 3->0"
    blocks = Block.create_covering_blocks(session, key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

    # Single block, fully filled.
    blocks = Block.create_covering_blocks(session, key, shuffle, 4)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

def test_repr():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    session = Session()
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2 1->3 2->1 3->0"
    blocks = Block.create_covering_blocks(session, key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

def test_str():
    Key.set_random_seed(55511)
    Shuffle.set_random_seed(55522)
    session = Session()
    key = Key.create_random_key(4)
    assert key.__str__() == "1010"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->0 1->1 2->3 3->2"
    blocks = Block.create_covering_blocks(session, key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__str__() == "1001"

def test_size():
    Key.set_random_seed(5551)
    Shuffle.set_random_seed(5552)
    session = Session()
    key = Key.create_random_key(65)
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_covering_blocks(session, key, shuffle, 30)
    assert len(blocks) == 3
    assert blocks[0].size == 30
    assert blocks[1].size == 30
    assert blocks[2].size == 5

def test_current_parity():

    Key.set_random_seed(6661)
    Shuffle.set_random_seed(6662)
    session = Session()

    # Even parity block.
    key = Key.create_random_key(10)
    assert key.__str__() == "0111101111"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->8 1->1 2->0 3->2 4->3 5->4 6->7 7->9 8->5 9->6"
    blocks = Block.create_covering_blocks(session, key, shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "1101111101"
    assert block.current_parity == 0

    # Odd parity block.
    key = Key.create_random_key(12)
    assert key.__str__() == "010100111101"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->1 1->8 2->10 3->9 4->0 5->6 6->7 7->5 8->2 9->3 10->11 11->4"
    blocks = Block.create_covering_blocks(session, key, shuffle, 12)
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
    session = Session()

    # Prepare a 10-bit block.
    key = Key.create_random_key(10)
    assert key.__str__() == "0100110001"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->3 1->2 2->6 3->1 4->7 5->0 6->4 7->9 8->8 9->5"
    blocks = Block.create_covering_blocks(session, key, shuffle, 10)
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

def test_error_parity():

    Key.set_random_seed(8881)
    Shuffle.set_random_seed(8882)
    session = Session()

    # Create the original (sent) key.
    tx_key = Key.create_random_key(16)
    assert tx_key.__repr__() == "Key: 1011111100101110"

    # Create the noisy (received) key, which has 3 errors relative to the original key.
    rx_key = tx_key.copy(3)
    assert tx_key.__repr__() == "Key: 1011111100101110"
    assert rx_key.__repr__() == "Key: 1111111110101100"
                            # Errors:  ^      ^     ^
                            #                   111111
                            #         0123456789012345

    # Create a random shuffling.
    shuffle = Shuffle(rx_key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == ("Shuffle: 0->8 1->10 2->3 3->6 4->7 5->2 6->4 7->0 8->5 9->1 "
                                  "10->11 11->13 12->9 13->14 14->12 15->15")

    # Create a block that covers the entire shuffled noisy key.
    # The block has errors at the following shuffle indexes: 0, 10, and 13
    rx_blocks = Block.create_covering_blocks(session, rx_key, shuffle, rx_key.size)
    assert len(rx_blocks) == 1
    rx_block = rx_blocks[0]
    assert rx_block.__repr__() == ("Block: 0->8=1 1->10=1 2->3=1 3->6=1 4->7=1 5->2=1 6->4=1 "
                                   "7->0=1 8->5=1 9->1=1 10->11=0 11->13=1 12->9=0 13->14=0 "
                                   "14->12=1 15->15=0")
    assert rx_block.__str__() == "1111111111010010"
                        # Errors: ^         ^  ^
                        #                   111111
                        #         0123456789012345
    assert rx_block.current_parity == 0

    # Function which returns the correct parity for a range of shuffled bits.
    ask_correct_parity_function = (
        lambda start_index, end_index: shuffle.calculate_parity(tx_key, start_index, end_index)
    )

    # At this point, we have not yet corrected any error in the block.
    assert rx_block.error_parity == Block.ERRORS_UNKNOWN

    # Correct one error.
    corrected_shuffle_index = rx_block.correct_one_bit(ask_correct_parity_function)
    assert corrected_shuffle_index == 0
    assert rx_block.__str__() == "0111111111010010"
                        # Errors:           ^  ^
                        #                   111111
                        #         0123456789012345

    # At this point, we should have an even numbers in the block.
    assert rx_block.error_parity == Block.ERRORS_EVEN

    # Flip the parity of the block. This would not happen in real life, because it causes the stored
    # parity to become inconsistent with the actual bits in the block. But we do it here anyway to
    # allows us to test odd error parity.
    rx_block.flip_parity()
    assert rx_block.error_parity == Block.ERRORS_ODD

def test_get_blocks_containing_key_index():

    Key.set_random_seed(9991)
    Shuffle.set_random_seed(9992)
    session = Session()

    # A block that contains only key bits 1, 3, and 4
    key1 = Key.create_random_key(5)
    assert key1.__repr__() == "Key: 00011"
    shuffle1 = Shuffle(key1.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle1.__repr__() == ("Shuffle: 0->1 1->4 2->3 3->0 4->2")
    block1 = Block(session, key1, shuffle1, 0, 3)
    assert block1.__repr__() == ("Block: 0->1=0 1->4=1 2->3=1")
    assert session.get_blocks_containing_key_index(0) == []
    assert session.get_blocks_containing_key_index(1) == [block1]
    assert session.get_blocks_containing_key_index(2) == []
    assert session.get_blocks_containing_key_index(3) == [block1]
    assert session.get_blocks_containing_key_index(4) == [block1]
    assert session.get_blocks_containing_key_index(5) == []

    # A block that contains only key bits 0, 2, and 3
    key2 = Key.create_random_key(6)
    assert key2.__repr__() == "Key: 001001"
    shuffle2 = Shuffle(key2.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle2.__repr__() == ("Shuffle: 0->4 1->1 2->5 3->2 4->0 5->3")
    block2 = Block(session, key2, shuffle2, 3, 6)
    assert block2.__repr__() == ("Block: 3->2=1 4->0=0 5->3=0")
    assert session.get_blocks_containing_key_index(0) == [block2]
    assert session.get_blocks_containing_key_index(1) == [block1]
    assert session.get_blocks_containing_key_index(2) == [block2]
    assert session.get_blocks_containing_key_index(3) == [block1, block2]
    assert session.get_blocks_containing_key_index(4) == [block1]
    assert session.get_blocks_containing_key_index(5) == []

    # Create sub-blocks for block2
    left_sub_block = block2.get_left_sub_block()
    right_sub_block = block2.get_right_sub_block()
    assert left_sub_block.__repr__() == ("Block: 3->2=1 4->0=0")
    assert right_sub_block.__repr__() == ("Block: 5->3=0")
    assert session.get_blocks_containing_key_index(0) == [block2, left_sub_block]
    assert session.get_blocks_containing_key_index(1) == [block1]
    assert session.get_blocks_containing_key_index(2) == [block2, left_sub_block]
    assert session.get_blocks_containing_key_index(3) == [block1, block2, right_sub_block]
    assert session.get_blocks_containing_key_index(4) == [block1]
    assert session.get_blocks_containing_key_index(5) == []

def test_correct_one_bit_scenario_three_errors_fix_first_dont_fix_second():

    Key.set_random_seed(12345)
    Shuffle.set_random_seed(67890)
    session = Session()

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
    rx_blocks = Block.create_covering_blocks(session, rx_key, shuffle, rx_key.size)
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

    # Since we are not doing multiple iterations in this test cases, the queue or error blocks
    # should be empty.
    assert session.get_registered_error_blocks() == []

    # Since we have fixed one error, the top block will have an even number of errors for sure.
    assert shuffle.calculate_parity(tx_key, 0, tx_key.size) == rx_block.current_parity

    # Hence, attempting to fix another error on the top block will fail for sure.
    assert rx_block.correct_one_bit(ask_correct_parity_function) is None
