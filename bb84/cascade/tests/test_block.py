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
