from cascade.block import Block
from cascade.key import Key
from cascade.shuffle import Shuffle

def test_create_block():

    # Block covers entire shuffle.
    Key.set_random_seed(2221)
    Shuffle.set_random_seed(2222)
    key = Key.create_random_key(8)
    assert key.__repr__() == "Key: 10111010"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->6 3->4 4->3 5->2 6->5 7->7"
    block = Block(key, shuffle, 3, 6, None)
    assert block.__repr__() == "Block: 3->4=1 4->3=1 5->2=1"
    block = Block(key, shuffle, 0, 8, None)
    assert block.__repr__() == "Block: 0->0=1 1->1=0 2->6=1 3->4=1 4->3=1 5->2=1 6->5=0 7->7=0"

    # Block covers part of the shuffle.
    block = Block(key, shuffle, 1, 3, None)
    assert block.__repr__() == "Block: 1->1=0 2->6=1"

    # Single bit block.
    block = Block(key, shuffle, 2, 3, None)
    assert block.__repr__() == "Block: 2->6=1"

def test_create_covering_blocks():

    # Prepare key and shuffle.
    Key.set_random_seed(3331)
    Shuffle.set_random_seed(3332)
    key = Key.create_random_key(16)
    assert key.__repr__() == "Key: 0011011001100110"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == ("Shuffle: 0->4 1->14 2->5 3->15 4->0 5->1 6->7 7->11 "
                                  "8->6 9->12 10->13 11->3 12->9 13->8 14->2 15->10")

    # Multiple blocks, last block is partially filled.
    blocks = Block.create_covering_blocks(key, shuffle, 5)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->14=1 2->5=1 3->15=0 4->0=0"
    assert blocks[1].__repr__() == "Block: 5->1=0 6->7=0 7->11=0 8->6=1 9->12=0"
    assert blocks[2].__repr__() == "Block: 10->13=1 11->3=1 12->9=1 13->8=0 14->2=1"
    assert blocks[3].__repr__() == "Block: 15->10=1"

    # Multiple blocks, last block is fully filled.
    blocks = Block.create_covering_blocks(key, shuffle, 4)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->14=1 2->5=1 3->15=0"
    assert blocks[1].__repr__() == "Block: 4->0=0 5->1=0 6->7=0 7->11=0"
    assert blocks[2].__repr__() == "Block: 8->6=1 9->12=0 10->13=1 11->3=1"
    assert blocks[3].__repr__() == "Block: 12->9=1 13->8=0 14->2=1 15->10=1"

    # Single block, partially filled.
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->3 3->2"
    blocks = Block.create_covering_blocks(key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->0=1 1->1=1 2->3=1 3->2=1"

    # Single block, fully filled.
    blocks = Block.create_covering_blocks(key, shuffle, 4)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->0=1 1->1=1 2->3=1 3->2=1"

def test_repr():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->3 1->2 2->1 3->0"
    blocks = Block.create_covering_blocks(key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->3=1 1->2=1 2->1=1 3->0=1"

def test_str():
    Key.set_random_seed(55511)
    Shuffle.set_random_seed(55522)
    key = Key.create_random_key(4)
    assert key.__str__() == "1010"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->1 1->2 2->3 3->0"
    blocks = Block.create_covering_blocks(key, shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__str__() == "0101"

def test_lt():
    Key.set_random_seed(55533)
    Shuffle.set_random_seed(55544)
    key = Key.create_random_key(6)
    assert key.__str__() == "001101"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->3 1->2 2->4 3->5 4->1 5->0"
    blocks = Block.create_covering_blocks(key, shuffle, 3)
    assert len(blocks) == 2
    assert (blocks[0] < blocks[1]) or (blocks[1] < blocks[0])
    # pylint:disable=comparison-with-itself
    assert not blocks[0] < blocks[0]

def test_get_start_index():
    Key.set_random_seed(55555)
    Shuffle.set_random_seed(55566)
    key = Key.create_random_key(6)
    assert key.__str__() == "001100"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->2 1->1 2->0 3->5 4->3 5->4"
    blocks = Block.create_covering_blocks(key, shuffle, 3)
    assert len(blocks) == 2
    assert blocks[0].get_start_index() == 0
    assert blocks[1].get_start_index() == 3

def test_get_end_index():
    Key.set_random_seed(55577)
    Shuffle.set_random_seed(55588)
    key = Key.create_random_key(6)
    assert key.__str__() == "100000"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->4 1->0 2->5 3->2 4->3 5->1"
    blocks = Block.create_covering_blocks(key, shuffle, 3)
    assert len(blocks) == 2
    assert blocks[0].get_end_index() == 3
    assert blocks[1].get_end_index() == 6

def test_get_shuffle():
    Key.set_random_seed(55591)
    Shuffle.set_random_seed(55592)
    key = Key.create_random_key(6)
    assert key.__str__() == "001000"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->5 1->3 2->4 3->0 4->1 5->2"
    blocks = Block.create_covering_blocks(key, shuffle, 3)
    assert len(blocks) == 2
    assert blocks[0].get_shuffle() == shuffle
    assert blocks[1].get_shuffle() == shuffle

def test_get_size():
    Key.set_random_seed(5551)
    Shuffle.set_random_seed(5552)
    key = Key.create_random_key(65)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_covering_blocks(key, shuffle, 30)
    assert len(blocks) == 3
    assert blocks[0].get_size() == 30
    assert blocks[1].get_size() == 30
    assert blocks[2].get_size() == 5

def test_get_key_indexes():
    Key.set_random_seed(55593)
    Shuffle.set_random_seed(55594)
    key = Key.create_random_key(6)
    assert key.__str__() == "010011"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->4 1->5 2->2 3->3 4->0 5->1"
    blocks = Block.create_covering_blocks(key, shuffle, 3)
    assert len(blocks) == 2
    assert blocks[0].get_key_indexes() == [4, 5, 2]
    assert blocks[1].get_key_indexes() == [3, 0, 1]

def test_get_current_parity():

    # Even parity block.
    Key.set_random_seed(6661)
    Shuffle.set_random_seed(6662)
    key = Key.create_random_key(10)
    assert key.__str__() == "0111101111"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->1 1->6 2->7 3->8 4->4 5->2 6->0 7->9 8->3 9->5"
    blocks = Block.create_covering_blocks(key, shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "1111110110"
    assert block.get_current_parity() == 0

    # Odd parity block.
    key = Key.create_random_key(12)
    assert key.__str__() == "010100111101"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->7 1->9 2->11 3->2 4->8 5->1 6->6 7->5 8->0 9->10 10->3 11->4"
    blocks = Block.create_covering_blocks(key, shuffle, 12)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "111011100010"
    assert block.get_current_parity() == 1

    # Split block into sub-blocks.
    left_sub_block = block.create_left_sub_block()
    right_sub_block = block.create_right_sub_block()

    # Odd parity sub-block.
    assert left_sub_block.__str__() == "111011"
    assert left_sub_block.get_current_parity() == 1

    # Even parity sub-block.
    assert right_sub_block.__str__() == "100010"
    assert right_sub_block.get_current_parity() == 0

def test_get_and_set_correct_parity():
    Key.set_random_seed(6663)
    Shuffle.set_random_seed(6664)
    key = Key.create_random_key(10)
    assert key.__str__() == "1010111100"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->8 1->5 2->7 3->0 4->2 5->4 6->1 7->3 8->9 9->6"
    blocks = Block.create_covering_blocks(key, shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "0111110001"
    assert block.get_correct_parity() is None
    block.set_correct_parity(0)
    assert block.get_correct_parity() == 0
    block.set_correct_parity(1)
    assert block.get_correct_parity() == 1

def test_is_top_block():
    Key.set_random_seed(6665)
    Shuffle.set_random_seed(6666)
    key = Key.create_random_key(10)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_covering_blocks(key, shuffle, 10)
    assert len(blocks) == 1
    top_block = blocks[0]
    assert top_block.is_top_block()
    left_sub_block = top_block.create_left_sub_block()
    assert not left_sub_block.is_top_block()
    right_sub_block = top_block.create_left_sub_block()
    assert not right_sub_block.is_top_block()
    left_left_sub_block = left_sub_block.create_left_sub_block()
    assert not left_left_sub_block.is_top_block()

def test_get_parent_block():
    Key.set_random_seed(6665)
    Shuffle.set_random_seed(6666)
    key = Key.create_random_key(10)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_covering_blocks(key, shuffle, 10)
    assert len(blocks) == 1
    top_block = blocks[0]
    assert top_block.get_parent_block() is None
    left_sub_block = top_block.create_left_sub_block()
    assert left_sub_block.get_parent_block() == top_block
    right_sub_block = top_block.create_left_sub_block()
    assert right_sub_block.get_parent_block() == top_block
    left_left_sub_block = left_sub_block.create_left_sub_block()
    assert left_left_sub_block.get_parent_block() == left_sub_block

def test_get_and_create_left_sub_block():
    Key.set_random_seed(6667)
    Shuffle.set_random_seed(6668)
    key = Key.create_random_key(12)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_covering_blocks(key, shuffle, 8)
    assert len(blocks) == 2
    top_block = blocks[0]
    assert top_block.get_left_sub_block() is None
    left_sub_block = top_block.create_left_sub_block()
    assert top_block.get_left_sub_block() is left_sub_block
    left_left_sub_block = left_sub_block.create_left_sub_block()
    assert left_sub_block.get_left_sub_block() is left_left_sub_block

def test_get_and_create_right_sub_block():
    Key.set_random_seed(6667)
    Shuffle.set_random_seed(6668)
    key = Key.create_random_key(12)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_covering_blocks(key, shuffle, 8)
    assert len(blocks) == 2
    top_block = blocks[0]
    assert top_block.get_right_sub_block() is None
    right_sub_block = top_block.create_right_sub_block()
    assert top_block.get_right_sub_block() is right_sub_block
    right_right_sub_block = right_sub_block.create_right_sub_block()
    assert right_sub_block.get_right_sub_block() is right_right_sub_block

def test_get_error_parity():

    # Create the original (sent) key.
    Key.set_random_seed(8881)
    Shuffle.set_random_seed(8882)
    correct_key = Key.create_random_key(16)
    assert correct_key.__repr__() == "Key: 1011111100101110"

    # Create the noisy (received) key, which has 3 errors relative to the original key.
    noisy_key = correct_key.copy(0.1875, Key.ERROR_METHOD_EXACT)
    assert correct_key.__repr__() == "Key: 1011111100101110"
    assert noisy_key.__repr__() == "Key: 1111111110101100"
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

def test_get_key_index():
    Key.set_random_seed(77711)
    Shuffle.set_random_seed(77712)
    key = Key.create_random_key(6)
    assert key.__str__() == "110101"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->0 1->5 2->1 3->4 4->2 5->3"
    blocks = Block.create_covering_blocks(key, shuffle, 3)
    block = blocks[0]
    assert block.get_key_index(1) == 5

def test_flip_bit():
    Key.set_random_seed(77713)
    Shuffle.set_random_seed(77714)
    key = Key.create_random_key(6)
    assert key.__str__() == "111100"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->1 1->2 2->4 3->5 4->0 5->3"
    blocks = Block.create_covering_blocks(key, shuffle, 3)
    block = blocks[1]
    assert block.__str__() == "011"
    block.flip_bit(4)
    assert key.__str__() == "011100"
    assert block.__str__() == "001"

def test_flip_parity():
    Key.set_random_seed(77715)
    Shuffle.set_random_seed(77716)
    key = Key.create_random_key(6)
    assert key.__str__() == "001010"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->2 1->5 2->0 3->4 4->1 5->3"
    blocks = Block.create_covering_blocks(key, shuffle, 3)
    block = blocks[1]
    assert block.__str__() == "100"
    assert block.get_error_parity() == Block.ERRORS_UNKNOWN
    block.set_correct_parity(0)
    assert block.get_error_parity() == Block.ERRORS_ODD
    block.flip_bit(4)
    assert key.__str__() == "011010"
    assert block.__str__() == "110"
    assert block.get_error_parity() == Block.ERRORS_ODD
    block.flip_parity()
    assert block.get_error_parity() == Block.ERRORS_EVEN
