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
    key = Key.create_random_key(8, seed=123)
    assert key.__repr__() == "Key: 01011001"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=456)
    assert shuffle.__repr__() == "Shuffle: 0->0=0 1->4=1 2->1=1 3->7=1 4->3=1 5->2=0 6->6=0 7->5=0"
    block = Block(shuffle, 3, 6)
    assert block.__repr__() == "Block: 3->7=1 4->3=1 5->2=0"
    # Special case: block covers entire shuffle
    block = Block(shuffle, 0, 8)
    assert block.__repr__() == "Block: 0->0=0 1->4=1 2->1=1 3->7=1 4->3=1 5->2=0 6->6=0 7->5=0"
    # Special case: single bit block
    block = Block(shuffle, 2, 3)
    assert block.__repr__() == "Block: 2->1=1"
    # Special case: empty block
    block = Block(shuffle, 2, 2)
    assert block.__repr__() == "Block:"

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
