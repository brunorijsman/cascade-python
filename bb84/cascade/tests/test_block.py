import pytest
from bb84.cascade.block import Block
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

def test_create_validate_args():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)
    key = Key.create_random_key(8)
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    with pytest.raises(AssertionError):
        Block("hello", 0, 1)
    with pytest.raises(AssertionError):
        Block(shuffle, -1, 1)
    with pytest.raises(AssertionError):
        Block(shuffle, 8, 1)
    with pytest.raises(AssertionError):
        Block(shuffle, "hello", 1)
    with pytest.raises(AssertionError):
        Block(shuffle, 3, -1)
    with pytest.raises(AssertionError):
        Block(shuffle, 3, 9)
    with pytest.raises(AssertionError):
        Block(shuffle, 3, 2)

def test_create_block():

    Key.set_random_seed(2221)
    Shuffle.set_random_seed(2222)

    # Special case: block covers entire shuffle
    key = Key.create_random_key(8)
    assert key.__repr__() == "Key: 10111010"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2=1 1->3=1 2->5=0 3->6=1 4->4=1 5->0=1 6->7=0 7->1=0"
    block = Block(shuffle, 3, 6)
    assert block.__repr__() == "Block: 3->6=1 4->4=1 5->0=1"
    block = Block(shuffle, 0, 8)
    assert block.__repr__() == "Block: 0->2=1 1->3=1 2->5=0 3->6=1 4->4=1 5->0=1 6->7=0 7->1=0"

    # Special case: single bit block
    block = Block(shuffle, 2, 3)
    assert block.__repr__() == "Block: 2->5=0"

    # Special case: empty block
    with pytest.raises(AssertionError):
        block = Block(shuffle, 2, 2)

def test_create_blocks_covering_shuffle():

    Key.set_random_seed(3331)
    Shuffle.set_random_seed(3332)
    key = Key.create_random_key(16)
    assert key.__repr__() == "Key: 0011011001100110"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == ("Shuffle: 0->4=0 1->10=1 2->6=1 3->5=1 4->15=0 5->12=0 6->7=0 "
                                  "7->9=1 8->0=0 9->14=1 10->11=0 11->8=0 12->3=1 13->2=1 "
                                  "14->13=1 15->1=0")

    # Multiple blocks, last block is partially filled
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->10=1 2->6=1 3->5=1 4->15=0"
    assert blocks[1].__repr__() == "Block: 5->12=0 6->7=0 7->9=1 8->0=0 9->14=1"
    assert blocks[2].__repr__() == "Block: 10->11=0 11->8=0 12->3=1 13->2=1 14->13=1"
    assert blocks[3].__repr__() == "Block: 15->1=0"

    # Multiple blocks, last block is fully filled
    blocks = Block.create_blocks_covering_shuffle(shuffle, 4)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->4=0 1->10=1 2->6=1 3->5=1"
    assert blocks[1].__repr__() == "Block: 4->15=0 5->12=0 6->7=0 7->9=1"
    assert blocks[2].__repr__() == "Block: 8->0=0 9->14=1 10->11=0 11->8=0"
    assert blocks[3].__repr__() == "Block: 12->3=1 13->2=1 14->13=1 15->1=0"

    # Single block, partially filled
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2=1 1->3=1 2->1=1 3->0=1"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

    # Single block, fully filled
    blocks = Block.create_blocks_covering_shuffle(shuffle, 4)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

    # No blocks (empty shuffle)
    key = Key.create_random_key(0)
    assert key.__repr__() == "Key: "
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle:"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 0

def test_repr():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    key = Key.create_random_key(4)
    assert key.__repr__() == "Key: 1111"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2=1 1->3=1 2->1=1 3->0=1"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=1 1->3=1 2->1=1 3->0=1"

def test_str():
    Key.set_random_seed(55511)
    Shuffle.set_random_seed(55522)
    key = Key.create_random_key(4)
    assert key.__str__() == "1010"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "1001"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__str__() == "1001"

def test_size():
    Key.set_random_seed(5551)
    Shuffle.set_random_seed(5552)
    key = Key.create_random_key(65)
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_blocks_covering_shuffle(shuffle, 30)
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
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "1101111101"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "1101111101"
    assert block.current_parity == 0

    # Odd parity block.
    key = Key.create_random_key(12)
    assert key.__str__() == "010100111101"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "110101100110"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 12)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "110101100110"
    assert block.current_parity == 1

    # Split block into sub-blocks.
    (left_sub_block, right_sub_block) = block.split()

    # Even parity sub-block.
    assert left_sub_block.__str__() == "110101"
    assert left_sub_block.current_parity == 0

    # Odd parity sub-block.
    assert right_sub_block.__str__() == "100110"
    assert right_sub_block.current_parity == 1

def test_split():

    Key.set_random_seed(7771)
    Shuffle.set_random_seed(7772)

    # Split block with even number of bits into sub-blocks.
    key = Key.create_random_key(10)
    assert key.__str__() == "0100110001"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0001001101"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "0001001101"
    (left_sub_block, right_sub_block) = block.split()
    assert left_sub_block.__str__() == "00010"
    assert right_sub_block.__str__() == "01101"

    # Split right sub-block with odd number of bits into sub-sub-blocks.
    (left_sub_sub_block, right_sub_sub_block) = right_sub_block.split()
    assert left_sub_sub_block.__str__() == "011"
    assert right_sub_sub_block.__str__() == "01"

    # Split left sub-sub-block with odd number of bits into sub-sub-sub-blocks.
    (left_sub_sub_sub_block, right_sub_sub_sub_block) = left_sub_sub_block.split()
    assert left_sub_sub_sub_block.__str__() == "01"
    assert right_sub_sub_sub_block.__str__() == "1"

    # A block that was already split is not allowed to be split again.
    with pytest.raises(AssertionError):
        block.split()

    # Not allowed to split a block of size 1.
    with pytest.raises(AssertionError):
        right_sub_sub_sub_block.split()

def test_clear_key_index_to_block_map():

    Key.set_random_seed(12345)
    Shuffle.set_random_seed(67890)

    # Forget about blocks that were added in other test cases.
    Block.clear_key_index_to_block_map()

    # Set key index to block map to known state.
    key = Key.create_random_key(5)
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    block = Block(shuffle, 0, 3)
    assert block.__repr__() == ("Block: 0->3=1 1->2=1 2->1=0")
    assert Block.get_blocks_containing_key_index(0) == []
    assert Block.get_blocks_containing_key_index(1) == [block]
    assert Block.get_blocks_containing_key_index(2) == [block]
    assert Block.get_blocks_containing_key_index(3) == [block]
    assert Block.get_blocks_containing_key_index(4) == []
    assert Block.get_blocks_containing_key_index(5) == []

    # Clear key index to block map.
    Block.clear_key_index_to_block_map()
    for key_index in range(0, 6):
        assert Block.get_blocks_containing_key_index(key_index) == []

def test_get_blocks_containing_key_index():

    Key.set_random_seed(9991)
    Shuffle.set_random_seed(9992)
    Block.clear_key_index_to_block_map()

    # A block that contains only key bits 1, 3, and 4
    key1 = Key.create_random_key(5)
    assert key1.__repr__() == "Key: 00011"
    shuffle1 = Shuffle(key1, Shuffle.SHUFFLE_RANDOM)
    assert shuffle1.__repr__() == ("Shuffle: 0->1=0 1->4=1 2->3=1 3->0=0 4->2=0")
    block1 = Block(shuffle1, 0, 3)
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
    shuffle2 = Shuffle(key2, Shuffle.SHUFFLE_RANDOM)
    assert shuffle2.__repr__() == ("Shuffle: 0->4=0 1->1=0 2->5=1 3->2=1 4->0=0 5->3=0")
    block2 = Block(shuffle2, 3, 6)
    assert block2.__repr__() == ("Block: 3->2=1 4->0=0 5->3=0")
    assert Block.get_blocks_containing_key_index(0) == [block2]
    assert Block.get_blocks_containing_key_index(1) == [block1]
    assert Block.get_blocks_containing_key_index(2) == [block2]
    assert Block.get_blocks_containing_key_index(3) == [block1, block2]
    assert Block.get_blocks_containing_key_index(4) == [block1]
    assert Block.get_blocks_containing_key_index(5) == []

    # Create sub-blocks for block2
    (left_sub_block, right_sub_block) = block2.split()
    assert left_sub_block.__repr__() == ("Block: 3->2=1 4->0=0")
    assert right_sub_block.__repr__() == ("Block: 5->3=0")
    assert Block.get_blocks_containing_key_index(0) == [block2, left_sub_block]
    assert Block.get_blocks_containing_key_index(1) == [block1]
    assert Block.get_blocks_containing_key_index(2) == [block2, left_sub_block]
    assert Block.get_blocks_containing_key_index(3) == [block1, block2, right_sub_block]
    assert Block.get_blocks_containing_key_index(4) == [block1]
    assert Block.get_blocks_containing_key_index(5) == []

def test_correct_one_bit():

    Key.set_random_seed(12345)
    Shuffle.set_random_seed(67890)
    Block.clear_key_index_to_block_map()

    # Prepare the original (sent) key
    original_key = Key.create_random_key(16)
    assert original_key.__repr__() == "Key: 1011010001110010"

    # Prepare the noisy (received) key, which is the same as the original key except with 3 errors
    noisy_key = original_key.copy(3)
    assert noisy_key.__repr__() == "Key: 1011011010110010"

    print(f"{original_key} {noisy_key}")


    # TODO verify prority queue of blocks with 
    pass
