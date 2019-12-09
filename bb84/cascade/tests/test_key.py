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
    key = Key.create_random_key(16, 1234567890)
    assert key.size == 16
    assert key.__str__() == "0101101010011110"
    with pytest.raises(AssertionError):
        assert Key.create_random_key(-1)
    with pytest.raises(AssertionError):
        assert Key.create_random_key("hello")
    with pytest.raises(AssertionError):
        assert Key.create_random_key(64, "hello")

def test_repr():
    # TODO
    pass

def test_str():
    # TODO
    pass

def test_size():
    key = Key()
    assert key.size == 0
    key = Key.create_random_key(7)
    assert key.size == 7

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

def test_flip_bit():
    key = Key.create_random_key(9)
    original_value = key.get_bit(0)
    key.flip_bit(0)
    assert key.get_bit(0) == 1 - original_value
    original_value = key.get_bit(3)
    key.flip_bit(3)
    assert key.get_bit(3) == 1 - original_value
    original_value = key.get_bit(8)
    key.flip_bit(8)
    assert key.get_bit(8) == 1 - original_value
    with pytest.raises(AssertionError):
        key.flip_bit(10)
    with pytest.raises(AssertionError):
        key.flip_bit(-1)
    with pytest.raises(AssertionError):
        key.flip_bit("hello")

def test_copy_without_noise():
    # Copy an empty key.
    key = Key()
    key_copy = key.copy()
    assert key.size == key_copy.size
    # Make sure it is an accurate copy.
    assert key.size == key_copy.size
    assert key.difference(key_copy) == 0
    # Copy a non-empty key.
    key = Key.create_random_key(64)
    key_copy = key.copy()
    # Make sure it is an accurate copy.
    assert key.size == key_copy.size
    assert key.difference(key_copy) == 0
    # Make sure that each key has an independent copy of the bits; i.e. that changing a bit in the
    # original key does not affect the copied key, or vice versa.
    original_value = key.get_bit(1)
    assert key_copy.get_bit(1) == original_value
    key_copy.flip_bit(1)
    assert key.get_bit(1) == original_value
    assert key_copy.get_bit(1) == 1 - original_value

def test_copy_with_noise():
    # Copy a non-empty key.
    key = Key.create_random_key(64)
    key_copy = key.copy(5)
    # Make sure the copy has the expected amount of noise.
    assert key.size == key_copy.size
    assert key.difference(key_copy) == 5
    # Make sure that each key has an independent copy of the bits; i.e. that changing a bit in the
    # original key does not affect the copied key, or vice versa.
    original_value = key.get_bit(1)
    noisy_copy_value = key_copy.get_bit(1)
    key_copy.flip_bit(1)
    assert key.get_bit(1) == original_value
    assert key_copy.get_bit(1) == 1 - noisy_copy_value
    # Extreme case, flip all bits.
    key_copy = key.copy(64)
    assert key.size == key_copy.size
    assert key.difference(key_copy) == 64
    # Test parameter checks.
    with pytest.raises(AssertionError):
        key.copy(65)

def test_difference():
    # Normal case.
    key = Key.create_random_key(64)
    key_copy = key.copy(5)
    assert key.difference(key_copy) == 5
    # Special case: compare with self.
    assert key.difference(key) == 0
    # Special case: empty key.
    empty_key_1 = Key()
    empty_key_2 = Key()
    assert empty_key_1.difference(empty_key_2) == 0
    # Keys of different sizes.
    with pytest.raises(AssertionError):
        key.difference(empty_key_1)
