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
        Block("not-a-session", key, shuffle, 0, 1, None)
    # Validate key argument.
    with pytest.raises(AssertionError):
        Block(session, "not-a-key", shuffle, 0, 1, None)
    # Validate shuffle argument.
    with pytest.raises(AssertionError):
        Block(session, key, "not-a-shuffle", 0, 1, None)
    # Validate start_shuffle_index argument.
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, -1, 1, None)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 8, 1, None)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, "not-an-int", 1, None)
    # Validate end_shuffle_index argument.
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, -1, None)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, 9, None)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, 2, None)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, "not-an-int", None)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 3, 5, "not-none-and-not-a-block")
    # Empty key.
    key = Key()
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    with pytest.raises(AssertionError):
        Block(session, key, shuffle, 2, 2, None)

def test_create_block():

    Key.set_random_seed(2221)
    Shuffle.set_random_seed(2222)
    session = Session()

    # Block covers entire shuffle.
    key = Key.create_random_key(8)
    assert key.__repr__() == "Key: 10111010"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->6 3->4 4->3 5->2 6->5 7->7"
    block = Block(session, key, shuffle, 3, 6, None)
    assert block.__repr__() == "Block: 3->4=1 4->3=1 5->2=1"
    block = Block(session, key, shuffle, 0, 8, None)
    assert block.__repr__() == "Block: 0->0=1 1->1=0 2->6=1 3->4=1 4->3=1 5->2=1 6->5=0 7->7=0"

    # Block covers part of the shuffle.
    block = Block(session, key, shuffle, 1, 3, None)
    assert block.__repr__() == "Block: 1->1=0 2->6=1"

    # Single bit block.
    block = Block(session, key, shuffle, 2, 3, None)
    assert block.__repr__() == "Block: 2->6=1"

def test_create_covering_blocks():

    Key.set_random_seed(3331)
    Shuffle.set_random_seed(3332)
    session = Session()

    # Prepare key and shuffle.
    key = Key.create_random_key(16)
    assert key.__repr__() == "Key: 0011011001100110"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == ("Shuffle: 0->4 1->14 2->5 3->15 4->0 5->1 6->7 7->11 "
                                  "8->6 9->12 10->13 11->3 12->9 13->8 14->2 15->10")

    # Multiple blocks, last block is partially filled.
    blocks = Block.create_covering_blocks(session, key, shuffle, 5)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->14=1 2->5=1 3->15=0 4->0=0"
    assert blocks[1].__repr__() == "Block: 5->1=0 6->7=0 7->11=0 8->6=1 9->12=0"
    assert blocks[2].__repr__() == "Block: 10->13=1 11->3=1 12->9=1 13->8=0 14->2=1"
    assert blocks[3].__repr__() == "Block: 15->10=1"

    # Multiple blocks, last block is fully filled.
    blocks = Block.create_covering_blocks(session, key, shuffle, 4)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->14=1 2->5=1 3->15=0"
    assert blocks[1].__repr__() == "Block: 4->0=0 5->1=0 6->7=0 7->11=0"
    assert blocks[2].__repr__() == "Block: 8->6=1 9->12=0 10->13=1 11->3=1"
    assert blocks[3].__repr__() == "Block: 12->9=1 13->8=0 14->2=1 15->10=1"

    # Single block, partially filled.
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->3 3->2"
    blocks = Block.create_covering_blocks(session, key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->0=1 1->1=1 2->3=1 3->2=1"

    # Single block, fully filled.
    blocks = Block.create_covering_blocks(session, key, shuffle, 4)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->0=1 1->1=1 2->3=1 3->2=1"

def test_repr():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    session = Session()
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->3 1->2 2->1 3->0"
    blocks = Block.create_covering_blocks(session, key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->3=1 1->2=1 2->1=1 3->0=1"

def test_str():
    Key.set_random_seed(55511)
    Shuffle.set_random_seed(55522)
    session = Session()
    key = Key.create_random_key(4)
    assert key.__str__() == "1010"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->1 1->2 2->3 3->0"
    blocks = Block.create_covering_blocks(session, key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__str__() == "0101"

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
    assert shuffle.__str__() == "0->1 1->6 2->7 3->8 4->4 5->2 6->0 7->9 8->3 9->5"
    blocks = Block.create_covering_blocks(session, key, shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "1111110110"
    assert block.current_parity == 0

    # Odd parity block.
    key = Key.create_random_key(12)
    assert key.__str__() == "010100111101"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->7 1->9 2->11 3->2 4->8 5->1 6->6 7->5 8->0 9->10 10->3 11->4"
    blocks = Block.create_covering_blocks(session, key, shuffle, 12)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "111011100010"
    assert block.current_parity == 1

    # Split block into sub-blocks.
    left_sub_block = block.get_left_sub_block()
    right_sub_block = block.get_right_sub_block()

    # Odd parity sub-block.
    assert left_sub_block.__str__() == "111011"
    assert left_sub_block.current_parity == 1

    # Even parity sub-block.
    assert right_sub_block.__str__() == "100010"
    assert right_sub_block.current_parity == 0

def test_get_sub_blocks():

    Key.set_random_seed(7771)
    Shuffle.set_random_seed(7772)
    session = Session()

    # Prepare a 10-bit block.
    key = Key.create_random_key(10)
    assert key.__str__() == "0100110001"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->9 1->5 2->1 3->7 4->4 5->3 6->8 7->6 8->2 9->0"
    blocks = Block.create_covering_blocks(session, key, shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "1110100000"

    # Get the left sub-block.
    left_sub_block = block.get_left_sub_block()
    assert left_sub_block.__str__() == "11101"

    # Get the left sub-block again (under the hood, a different code path is used for the 2nd get.)
    left_sub_block = block.get_left_sub_block()
    assert left_sub_block.__str__() == "11101"

    # Get the right sub-block.
    right_sub_block = block.get_right_sub_block()
    assert right_sub_block.__str__() == "00000"

    # Get the right sub-block again (under the hood, a different code path is used for the 2nd get.)
    right_sub_block = block.get_right_sub_block()
    assert right_sub_block.__str__() == "00000"

    # Split right sub-block with odd number of bits into sub-sub-blocks.
    left_sub_sub_block = right_sub_block.get_left_sub_block()
    right_sub_sub_block = right_sub_block.get_right_sub_block()
    assert left_sub_sub_block.__str__() == "000"
    assert right_sub_sub_block.__str__() == "00"

    # Split left sub-sub-block with odd number of bits into sub-sub-sub-blocks.
    left_sub_sub_sub_block = left_sub_sub_block.get_left_sub_block()
    right_sub_sub_sub_block = left_sub_sub_block.get_right_sub_block()
    assert left_sub_sub_sub_block.__str__() == "00"
    assert right_sub_sub_sub_block.__str__() == "0"

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
    assert shuffle.__repr__() == ("Shuffle: 0->8 1->12 2->6 3->7 4->4 5->10 6->11 7->2 8->1 9->9 "
                                  "10->15 11->0 12->13 13->3 14->5 15->14")

    # Create a block that covers the entire shuffled noisy key.
    # The block has errors at the following shuffle indexes: 2->6 8->1 14->5
    rx_blocks = Block.create_covering_blocks(session, rx_key, shuffle, rx_key.size)
    assert len(rx_blocks) == 1
    rx_block = rx_blocks[0]
    assert rx_block.__repr__() == ("Block: 0->8=1 1->12=1 2->6=1 3->7=1 4->4=1 5->10=1 6->11=0 "
                                   "7->2=1 8->1=1 9->9=0 10->15=0 11->0=1 12->13=1 13->3=1 14->5=1 "
                                   "15->14=0")
    assert rx_block.__str__() == "1111110110011110"   # 12 ones -> even parity
                        # Errors:  ^   ^^             # 3 errors -> odd number of errors
                        #                   111111
                        #         0123456789012345
    assert rx_block.current_parity == 0

    # Function which returns the correct parity for a range of shuffled bits.
    ask_correct_parity_function = lambda _shuffle_identifier, start_index, end_index: \
        shuffle.calculate_parity(tx_key, start_index, end_index)

    # At this point, we have not yet corrected any error in the block.
    assert rx_block.error_parity == Block.ERRORS_UNKNOWN

    # Correct one error.
    corrected_shuffle_index = rx_block.correct_one_bit(ask_correct_parity_function)
    assert corrected_shuffle_index == 0
    assert rx_block.__str__() == "0111110110011110"   # 11 ones -> odd parity
                        # Errors:      ^^             # 2 errors -> even number of errors
                        #                   111111
                        #         0123456789012345
    assert rx_block.current_parity == 1

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

    # A block that contains only key bits 0, 2, and 4
    key1 = Key.create_random_key(5)
    assert key1.__repr__() == "Key: 00011"
    shuffle1 = Shuffle(key1.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle1.__repr__() == ("Shuffle: 0->2 1->4 2->0 3->1 4->3")
    block1 = Block(session, key1, shuffle1, 0, 3, None)
    assert block1.__repr__() == ("Block: 0->2=0 1->4=1 2->0=0")
    assert session.get_blocks_containing_key_index(0) == [block1]  # Because of 2->0
    assert session.get_blocks_containing_key_index(1) == []
    assert session.get_blocks_containing_key_index(2) == [block1]  # Because of 0->2
    assert session.get_blocks_containing_key_index(3) == []
    assert session.get_blocks_containing_key_index(4) == [block1]  # Because of 1->4
    assert session.get_blocks_containing_key_index(5) == []

    # A block that contains only key bits 1, 2, 3, and 5
    key2 = Key.create_random_key(6)
    assert key2.__repr__() == "Key: 001001"
    shuffle2 = Shuffle(key2.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle2.__repr__() == ("Shuffle: 0->4 1->0 2->2 3->1 4->5 5->3")
    block2 = Block(session, key2, shuffle2, 2, 6, None)
    assert block2.__repr__() == ("Block: 2->2=1 3->1=0 4->5=1 5->3=0")
    assert session.get_blocks_containing_key_index(0) == [block1]
    assert session.get_blocks_containing_key_index(1) == [block2]
    assert session.get_blocks_containing_key_index(2) == [block1, block2]
    assert session.get_blocks_containing_key_index(3) == [block2]
    assert session.get_blocks_containing_key_index(4) == [block1]
    assert session.get_blocks_containing_key_index(5) == [block2]

    # Create sub-blocks for block2
    left_sub_block = block2.get_left_sub_block()
    right_sub_block = block2.get_right_sub_block()
    assert left_sub_block.__repr__() == ("Block: 2->2=1 3->1=0")
    assert right_sub_block.__repr__() == ("Block: 4->5=1 5->3=0")
    assert session.get_blocks_containing_key_index(0) == [block1]
    assert session.get_blocks_containing_key_index(1) == [block2, left_sub_block]
    assert session.get_blocks_containing_key_index(2) == [block1, block2, left_sub_block]
    assert session.get_blocks_containing_key_index(3) == [block2, right_sub_block]
    assert session.get_blocks_containing_key_index(4) == [block1]
    assert session.get_blocks_containing_key_index(5) == [block2, right_sub_block]

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
    assert shuffle.__repr__() == ("Shuffle: 0->7 1->13 2->6 3->14 4->12 5->5 6->1 7->15 8->11 "
                                  "9->10 10->4 11->0 12->3 13->8 14->9 15->2")

    # Create a block that covers the entire shuffled noisy key.
    # The block has errors at the following shuffle indexes: 1, 3, and 11
    rx_blocks = Block.create_covering_blocks(session, rx_key, shuffle, rx_key.size)
    assert len(rx_blocks) == 1
    rx_block = rx_blocks[0]
    assert rx_block.__repr__() == ("Block: 0->7=0 1->13=1 2->6=1 3->14=1 4->12=0 5->5=1 6->1=0 "
                                   "7->15=0 8->11=1 9->10=1 10->4=0 11->0=1 12->3=1 13->8=0 "
                                   "14->9=1 15->2=1")
    # Errors in shuffle bits: 13->8 14->9 1->13
    assert rx_block.__str__() == "0111010011011011"
                        # Errors:  ^           ^^
                        #                   111111
                        #         0123456789012345
    assert rx_block.current_parity == 0

    # Function which returns the correct parity for a range of shuffled bits.
    ask_correct_parity_function = lambda _shuffle_identifier, start_index, end_index: \
        shuffle.calculate_parity(tx_key, start_index, end_index)

    # Correct the first bit error. The recursion should go as follows:
    #
    #     v             vv
    #    01110100| 11011011         Odd | Even => Recurse left
    #
    #    v
    #   0111 | 0100                 Odd | Even => Recurse left
    #
    #   v
    #  01 | 11                      Odd | Even => Recurse left
    #
    #     v
    # 0 | 1                         Even | Odd => Recurse right => Corrects shuffled key index 1
    #
    corrected_shuffle_index = rx_block.correct_one_bit(ask_correct_parity_function)
    assert corrected_shuffle_index == 1
    assert rx_block.__str__() == "0011010011011011"
                        # Errors:              ^^
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
