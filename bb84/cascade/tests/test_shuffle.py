import pytest
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

def test_create_shuffle_invalid_args():
    key = Key.create_random_key(64)
    with pytest.raises(AssertionError):
        Shuffle("hello", Shuffle.SHUFFLE_NONE)
    with pytest.raises(AssertionError):
        Shuffle(key, "hello")
    with pytest.raises(AssertionError):
        Shuffle(key, -1)

def test_create_shuffle_none():
    key = Key.create_random_key(64)
    shuffle = Shuffle(key, Shuffle.SHUFFLE_NONE)
    for index in range(key.size):
        assert shuffle.get_bit(index) == key.get_bit(index)

def test_create_shuffle_random():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)
    key = Key.create_random_key(16)
    assert key.__str__() == "0010110001010010"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "1000101001010001"
    key = Key()
    assert key.__str__() == ""
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == ""
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)

def test_repr():
    Key.set_random_seed(2221)
    Shuffle.set_random_seed(2222)
    key = Key()
    shuffle = Shuffle(key, Shuffle.SHUFFLE_NONE)
    assert shuffle.__repr__() == "Shuffle:"
    key = Key.create_random_key(8)
    shuffle = Shuffle(key, Shuffle.SHUFFLE_NONE)
    assert shuffle.__repr__() == "Shuffle: 0->0=1 1->1=0 2->2=1 3->3=1 4->4=1 5->5=0 6->6=1 7->7=0"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2=1 1->3=1 2->5=0 3->6=1 4->4=1 5->0=1 6->7=0 7->1=0"

def test_str():
    Key.set_random_seed(3331)
    Shuffle.set_random_seed(3332)
    key = Key()
    shuffle = Shuffle(key, Shuffle.SHUFFLE_NONE)
    assert shuffle.__str__() == ""
    key = Key.create_random_key(8)
    shuffle = Shuffle(key, Shuffle.SHUFFLE_NONE)
    assert shuffle.__str__() == "00110110"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "00111010"

def test_set_random_seed():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    # TODO

def test_size():
    key = Key()
    shuffle = Shuffle(key, Shuffle.SHUFFLE_NONE)
    assert shuffle.size == 0
    key = Key.create_random_key(19)
    shuffle = Shuffle(key, Shuffle.SHUFFLE_NONE)
    assert shuffle.size == 19

def test_get_bit():
    Key.set_random_seed(5551)
    Shuffle.set_random_seed(5552)
    key = Key.create_random_key(13)
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0100001111001"
    assert shuffle.get_bit(0) == 0
    assert shuffle.get_bit(1) == 1
    assert shuffle.get_bit(2) == 0
    assert shuffle.get_bit(12) == 1
    with pytest.raises(AssertionError):
        shuffle.get_bit(-1)
    with pytest.raises(AssertionError):
        shuffle.get_bit(13)
    with pytest.raises(AssertionError):
        shuffle.get_bit("hello")

def test_set_bit():
    Key.set_random_seed(6661)
    Shuffle.set_random_seed(6662)
    key = Key.create_random_key(6)
    assert key.__repr__() == "Key: 011110"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->0=0 1->1=1 2->2=1 3->4=1 4->5=0 5->3=1"
    shuffle.set_bit(3, 0)
    assert shuffle.__repr__() == "Shuffle: 0->0=0 1->1=1 2->2=1 3->4=0 4->5=0 5->3=1"
    assert key.__repr__() == "Key: 011100"
    shuffle.set_bit(0, 1)
    assert shuffle.__repr__() == "Shuffle: 0->0=1 1->1=1 2->2=1 3->4=0 4->5=0 5->3=1"
    assert key.__repr__() == "Key: 111100"
    shuffle.set_bit(5, 0)
    assert shuffle.__repr__() == "Shuffle: 0->0=1 1->1=1 2->2=1 3->4=0 4->5=0 5->3=0"
    assert key.__repr__() == "Key: 111000"
    with pytest.raises(AssertionError):
        shuffle.set_bit(-1, 0)
    with pytest.raises(AssertionError):
        shuffle.set_bit(13, 0)
    with pytest.raises(AssertionError):
        shuffle.set_bit("hello", 0)
    with pytest.raises(AssertionError):
        shuffle.set_bit(1, -1)
    with pytest.raises(AssertionError):
        shuffle.set_bit(1, 2)
    with pytest.raises(AssertionError):
        shuffle.set_bit(1, "hello")

def test_flip_bit():
    Key.set_random_seed(7771)
    Shuffle.set_random_seed(7772)
    key = Key.create_random_key(6)
    assert key.__repr__() == "Key: 010011"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->1=1 1->0=0 2->5=1 3->2=0 4->4=1 5->3=0"
    shuffle.flip_bit(0)
    assert key.__repr__() == "Key: 000011"
    assert shuffle.__repr__() == "Shuffle: 0->1=0 1->0=0 2->5=1 3->2=0 4->4=1 5->3=0"
    with pytest.raises(AssertionError):
        shuffle.flip_bit(-1)
    with pytest.raises(AssertionError):
        shuffle.flip_bit(6)
    with pytest.raises(AssertionError):
        shuffle.flip_bit("hello")

def test_get_key_index():
    Key.set_random_seed(9991)
    Shuffle.set_random_seed(9992)
    key = Key.create_random_key(6)
    assert key.__repr__() == "Key: 000110"
    shuffle = Shuffle(key, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->3=1 1->5=0 2->4=1 3->0=0 4->1=0 5->2=0"
    assert shuffle.get_key_index(0) == 3
    assert shuffle.get_key_index(1) == 5
    assert shuffle.get_key_index(5) == 2
    with pytest.raises(AssertionError):
        shuffle.get_key_index(-1)
    with pytest.raises(AssertionError):
        shuffle.get_key_index(6)
    with pytest.raises(AssertionError):
        shuffle.get_key_index("hello")
