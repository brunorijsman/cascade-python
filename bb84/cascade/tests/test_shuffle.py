import pytest
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

def test_create_shuffle_invalid_args():
    key = Key.create_random_key(64)
    with pytest.raises(AssertionError):
        assert Shuffle("hello", Shuffle.ALGORITHM_NONE)
    with pytest.raises(AssertionError):
        assert Shuffle(key, "hello")
    with pytest.raises(AssertionError):
        assert Shuffle(key, -1)
    with pytest.raises(AssertionError):
        assert Shuffle(key, Shuffle.ALGORITHM_NONE, 1)
    with pytest.raises(AssertionError):
        assert Shuffle(key, Shuffle.ALGORITHM_RANDOM, "hello")

def test_create_shuffle_none():
    key = Key.create_random_key(64)
    shuffle = Shuffle(key, Shuffle.ALGORITHM_NONE)
    for index in range(key.size):
        assert shuffle.get_key_bit(index) == key.get_bit(index)
