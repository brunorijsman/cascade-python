import pytest
from bb84.cascade.key import Key

def test_create_empty_key():
    key = Key()
    assert key.size == 0

def test_create_random_key():
    key = Key.create_random_key(32)
    assert key.size == 32
    assert key.get_bit(0) in [0, 1]
    assert key.get_bit(7) in [0, 1]
    assert key.get_bit(31) in [0, 1]

def test_size():
    key = Key()
    assert key.size == 0
    key = Key.create_random_key(7)
    assert key.size == 7
    with pytest.raises(AssertionError):
        assert Key.create_random_key(-1)
    with pytest.raises(AssertionError):
        assert Key.create_random_key("hello")

def test_get_bit():
    key = Key.create_random_key(11)
    assert key.get_bit(0) in [0, 1]
    assert key.get_bit(3) in [0, 1]
    assert key.get_bit(10) in [0, 1]
    with pytest.raises(AssertionError):
        assert key.get_bit(11)
    with pytest.raises(AssertionError):
        assert key.get_bit(-1)
    with pytest.raises(AssertionError):
        assert key.get_bit("hello")

def test_set_bit():
    key = Key.create_random_key(13)
    key.set_bit(0, 0)
    assert key.get_bit(0) == 0
    key.set_bit(0, 1)
    assert key.get_bit(0) == 1
    key.set_bit(4, 0)
    assert key.get_bit(4) == 0
    key.set_bit(4, 1)
    assert key.get_bit(4) == 1
    key.set_bit(12, 0)
    assert key.get_bit(12) == 0
    key.set_bit(12, 1)
    assert key.get_bit(12) == 1
    with pytest.raises(AssertionError):
        key.set_bit(14, 0)
    with pytest.raises(AssertionError):
        key.set_bit(-1, 0)
    with pytest.raises(AssertionError):
        key.set_bit(1, 2)
    with pytest.raises(AssertionError):
        key.set_bit(1, -1)
    with pytest.raises(AssertionError):
        key.set_bit("hello", 0)
    with pytest.raises(AssertionError):
        key.set_bit(1, "hello")

def test_copy_without_noise():
    key = Key.create_random_key(64)
    key_copy = key.copy()
    assert key.size == key_copy.size
    # Make sure it is an accurate copy.
    assert key.difference(key_copy) == 0
    # Make sure that each key has an independent copy of the bits; i.e. that changing a bit in the
    # original key does not affect the copied key, or vice versa.
