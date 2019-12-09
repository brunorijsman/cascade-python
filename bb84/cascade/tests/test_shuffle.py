import pytest
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

def test_create_shuffle_invalid_args():
    key = Key.create_random_key(64)
    with pytest.raises(AssertionError):
        Shuffle("hello", Shuffle.ALGORITHM_NONE)
    with pytest.raises(AssertionError):
        Shuffle(key, "hello")
    with pytest.raises(AssertionError):
        Shuffle(key, -1)
    with pytest.raises(AssertionError):
        Shuffle(key, Shuffle.ALGORITHM_NONE, 1)
    with pytest.raises(AssertionError):
        Shuffle(key, Shuffle.ALGORITHM_RANDOM, "hello")

def test_create_shuffle_none():
    key = Key.create_random_key(64)
    shuffle = Shuffle(key, Shuffle.ALGORITHM_NONE)
    for index in range(key.size):
        assert shuffle.get_bit(index) == key.get_bit(index)

def test_create_shuffle_random():
    key = Key.create_random_key(16, seed=1234)
    assert key.__str__() == "1000000100001110"
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=5678)
    assert shuffle.__str__() == "1000001010000110"
    key = Key()
    assert key.__str__() == ""
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=5678)
    assert shuffle.__str__() == ""
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM)

def test_repr():
    key = Key()
    shuffle = Shuffle(key, Shuffle.ALGORITHM_NONE)
    assert shuffle.__repr__() == "Shuffle: "
    key = Key.create_random_key(16, seed=1234)
    shuffle = Shuffle(key, Shuffle.ALGORITHM_NONE)
    assert shuffle.__repr__() == "Shuffle: 1000000100001110"

def test_str():
    key = Key()
    shuffle = Shuffle(key, Shuffle.ALGORITHM_NONE)
    assert shuffle.__str__() == ""
    key = Key.create_random_key(16, seed=1234)
    shuffle = Shuffle(key, Shuffle.ALGORITHM_NONE)
    assert shuffle.__str__() == "1000000100001110"

def test_size():
    key = Key()
    shuffle = Shuffle(key, Shuffle.ALGORITHM_NONE)
    assert shuffle.size == 0
    key = Key.create_random_key(19)
    shuffle = Shuffle(key, Shuffle.ALGORITHM_NONE)
    assert shuffle.size == 19

def test_get_bit():
    key = Key.create_random_key(13, seed=9876)
    shuffle = Shuffle(key, Shuffle.ALGORITHM_RANDOM, seed=5432)
    assert shuffle.__str__() == "1011010001011"
    assert shuffle.get_bit(0) == 1
    assert shuffle.get_bit(1) == 0
    assert shuffle.get_bit(2) == 1
    assert shuffle.get_bit(12) == 1
    with pytest.raises(AssertionError):
        shuffle.get_bit(-1)
    with pytest.raises(AssertionError):
        shuffle.get_bit(13)
    with pytest.raises(AssertionError):
        shuffle.get_bit("hello")
