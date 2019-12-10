import pytest
from bb84.cascade.block import Block
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

def test_create_validate_args():
    key = Key.create_random_key(8, seed=123)
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=456)
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

    # Special case: block covers entire shuffle
    key = Key.create_random_key(8, seed=123)
    assert key.__repr__() == "Key: 01011001"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=456)
    assert shuffle.__repr__() == "Shuffle: 0->0=0 1->4=1 2->1=1 3->7=1 4->3=1 5->2=0 6->6=0 7->5=0"
    block = Block(shuffle, 3, 6)
    assert block.__repr__() == "Block: 3->7=1 4->3=1 5->2=0"
    block = Block(shuffle, 0, 8)
    assert block.__repr__() == "Block: 0->0=0 1->4=1 2->1=1 3->7=1 4->3=1 5->2=0 6->6=0 7->5=0"

    # Special case: single bit block
    block = Block(shuffle, 2, 3)
    assert block.__repr__() == "Block: 2->1=1"

    # Special case: empty block
    with pytest.raises(AssertionError):
        block = Block(shuffle, 2, 2)

def test_create_blocks_covering_shuffle():

    key = Key.create_random_key(16, seed=234)
    assert key.__repr__() == "Key: 1101101111011101"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=345)
    assert shuffle.__repr__() == ("Shuffle: 0->6=1 1->7=1 2->9=1 3->3=1 4->14=0 5->11=1 "
                                  "6->8=1 7->5=0 8->2=0 9->15=1 10->10=0 11->4=1 12->1=1 "
                                  "13->13=1 14->0=1 15->12=1")

    # Multiple blocks, last block is partially filled
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->6=1 1->7=1 2->9=1 3->3=1 4->14=0"
    assert blocks[1].__repr__() == "Block: 5->11=1 6->8=1 7->5=0 8->2=0 9->15=1"
    assert blocks[2].__repr__() == "Block: 10->10=0 11->4=1 12->1=1 13->13=1 14->0=1"
    assert blocks[3].__repr__() == "Block: 15->12=1"

    # Multiple blocks, last block is fully filled
    blocks = Block.create_blocks_covering_shuffle(shuffle, 4)
    assert len(blocks) == 4
    assert blocks[0].__repr__() == "Block: 0->6=1 1->7=1 2->9=1 3->3=1"
    assert blocks[1].__repr__() == "Block: 4->14=0 5->11=1 6->8=1 7->5=0"
    assert blocks[2].__repr__() == "Block: 8->2=0 9->15=1 10->10=0 11->4=1"
    assert blocks[3].__repr__() == "Block: 12->1=1 13->13=1 14->0=1 15->12=1"

    # Single block, partially filled
    key = Key.create_random_key(4, seed=234)
    assert key.__repr__() == "Key: 1101"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=345)
    assert shuffle.__repr__() == "Shuffle: 0->2=0 1->1=1 2->0=1 3->3=1"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=0 1->1=1 2->0=1 3->3=1"

    # Single block, fully filled
    blocks = Block.create_blocks_covering_shuffle(shuffle, 4)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=0 1->1=1 2->0=1 3->3=1"

    # No blocks (empty shuffle)
    key = Key.create_random_key(0, seed=234)
    assert key.__repr__() == "Key: "
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=345)
    assert shuffle.__repr__() == "Shuffle:"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 0

def test_repr():
    key = Key.create_random_key(4, seed=234)
    assert key.__repr__() == "Key: 1101"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=345)
    assert shuffle.__repr__() == "Shuffle: 0->2=0 1->1=1 2->0=1 3->3=1"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__repr__() == "Block: 0->2=0 1->1=1 2->0=1 3->3=1"

def test_str():
    key = Key.create_random_key(4, seed=234)
    assert key.__str__() == "1101"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=345)
    assert shuffle.__str__() == "0111"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 5)
    assert len(blocks) == 1
    assert blocks[0].__str__() == "0111"

def test_size():
    key = Key.create_random_key(65)
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM)
    blocks = Block.create_blocks_covering_shuffle(shuffle, 30)
    assert len(blocks) == 3
    assert blocks[0].size == 30
    assert blocks[1].size == 30
    assert blocks[2].size == 5

def test_current_parity():

    # Even parity block.
    key = Key.create_random_key(10, seed=12345)
    assert key.__str__() == "1011011010"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=67890)
    assert shuffle.__str__() == "1111101000"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "1111101000"
    assert block.current_parity == 0

    # Odd parity block.
    key = Key.create_random_key(10, seed=111111)
    assert key.__str__() == "0011001011"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=22222)
    assert shuffle.__str__() == "0010110011"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "0010110011"
    assert block.current_parity == 1

    # Split block into sub-blocks.
    (left_sub_block, right_sub_block) = block.split()

    # Even parity sub-block.
    assert left_sub_block.__str__() == "00101"
    assert left_sub_block.current_parity == 0

    # Odd parity sub-block.
    assert right_sub_block.__str__() == "10011"
    assert right_sub_block.current_parity == 1

def test_split():

    # Split block with even number of bits into sub-blocks.
    key = Key.create_random_key(10, seed=12345)
    assert key.__str__() == "1011011010"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=67890)
    assert shuffle.__str__() == "1111101000"
    blocks = Block.create_blocks_covering_shuffle(shuffle, 10)
    assert len(blocks) == 1
    block = blocks[0]
    assert block.__str__() == "1111101000"
    (left_sub_block, right_sub_block) = block.split()
    assert left_sub_block.__str__() == "11111"
    assert right_sub_block.__str__() == "01000"

    # Split right sub-block with odd number of bits into sub-sub-blocks.
    (left_sub_sub_block, right_sub_sub_block) = right_sub_block.split()
    assert left_sub_sub_block.__str__() == "010"
    assert right_sub_sub_block.__str__() == "00"

    # Split left sub-sub-block with odd number of bits into sub-sub-sub-blocks.
    (left_sub_sub_sub_block, right_sub_sub_sub_block) = left_sub_sub_block.split()
    assert left_sub_sub_sub_block.__str__() == "01"
    assert right_sub_sub_sub_block.__str__() == "0"

    # A block that was already split is not allowed to be split again.
    with pytest.raises(AssertionError):
        block.split()

    # Not allowed to split a block of size 1.
    with pytest.raises(AssertionError):
        right_sub_sub_sub_block.split()

def test_get_blocks_containing_key_index():

    # Forget about blocks that were added in other test cases.
    Block.clear_key_index_to_block_map()

    # A block that contains only key bits 1, 2, and 4
    key1 = Key.create_random_key(5, seed=111)
    assert key1.__repr__() == "Key: 01101"
    shuffle1 = Shuffle(key1, Shuffle.ALGORITHM_RANDOM, seed=222)
    assert shuffle1.__repr__() == ("Shuffle: 0->1=1 1->2=1 2->4=1 3->0=0 4->3=0")
    block1 = Block(shuffle1, 0, 3)
    assert block1.__repr__() == ("Block: 0->1=1 1->2=1 2->4=1")
    assert Block.get_blocks_containing_key_index(0) == []
    assert Block.get_blocks_containing_key_index(1) == [block1]
    assert Block.get_blocks_containing_key_index(2) == [block1]
    assert Block.get_blocks_containing_key_index(3) == []
    assert Block.get_blocks_containing_key_index(4) == [block1]
    assert Block.get_blocks_containing_key_index(5) == []

    # A block that contains only key bits 0, 1, and 5
    key2 = Key.create_random_key(6, seed=333)
    assert key2.__repr__() == "Key: 110101"
    shuffle2 = Shuffle(key2, Shuffle.ALGORITHM_RANDOM, seed=444)
    assert shuffle2.__repr__() == ("Shuffle: 0->4=0 1->3=1 2->2=0 3->5=1 4->0=1 5->1=1")
    block2 = Block(shuffle2, 3, 6)
    assert block2.__repr__() == ("Block: 3->5=1 4->0=1 5->1=1")
    assert Block.get_blocks_containing_key_index(0) == [block2]
    assert Block.get_blocks_containing_key_index(1) == [block1, block2]
    assert Block.get_blocks_containing_key_index(2) == [block1]
    assert Block.get_blocks_containing_key_index(3) == []
    assert Block.get_blocks_containing_key_index(4) == [block1]
    assert Block.get_blocks_containing_key_index(5) == [block2]

    # Create sub-blocks for block2
    (left_sub_block, right_sub_block) = block2.split()
    assert left_sub_block.__repr__() == ("Block: 3->5=1 4->0=1")
    assert right_sub_block.__repr__() == ("Block: 5->1=1")
    assert Block.get_blocks_containing_key_index(0) == [block2, left_sub_block]
    assert Block.get_blocks_containing_key_index(1) == [block1, block2, right_sub_block]
    assert Block.get_blocks_containing_key_index(2) == [block1]
    assert Block.get_blocks_containing_key_index(3) == []
    assert Block.get_blocks_containing_key_index(4) == [block1]
    assert Block.get_blocks_containing_key_index(5) == [block2, left_sub_block]
