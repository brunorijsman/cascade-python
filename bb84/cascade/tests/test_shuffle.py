import pytest
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

def test_create_shuffle_invalid_args():
    with pytest.raises(AssertionError):
        Shuffle(-1, Shuffle.SHUFFLE_NONE)
    with pytest.raises(AssertionError):
        Shuffle("hello", Shuffle.SHUFFLE_NONE)
    with pytest.raises(AssertionError):
        Shuffle(32, "hello")
    with pytest.raises(AssertionError):
        Shuffle(32, -1)

def test_create_shuffle_none():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)

    # Empty shuffle.
    key = Key()
    assert key.__str__() == ""
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_NONE)
    assert shuffle.__str__() == ""

    # Non-empty shuffle.
    key = Key.create_random_key(8)
    assert key.__str__() == "00101100"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_NONE)
    assert shuffle.__str__() == "0->0 1->1 2->2 3->3 4->4 5->5 6->6 7->7"
    for index in range(key.size):
        assert shuffle.get_bit(key, index) == key.get_bit(index)

def test_create_shuffle_random():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)

    # Empty shuffle.
    key = Key()
    assert key.__str__() == ""
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == ""

    # Non-empty shuffle.
    key = Key.create_random_key(16)
    assert key.__str__() == "0010110001010010"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == ("0->2 1->13 2->6 3->12 4->11 5->15 6->14 7->1 "
                                 "8->8 9->5 10->7 11->9 12->0 13->10 14->3 15->4")
    key = Key()
    assert key.__str__() == ""

def test_repr():
    Key.set_random_seed(2221)
    Shuffle.set_random_seed(2222)
    key = Key.create_random_key(8)
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_NONE)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->2 3->3 4->4 5->5 6->6 7->7"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->2 1->3 2->5 3->6 4->4 5->0 6->7 7->1"

def test_str():
    Key.set_random_seed(3331)
    Shuffle.set_random_seed(3332)
    key = Key.create_random_key(8)
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_NONE)
    assert shuffle.__str__() == "0->0 1->1 2->2 3->3 4->4 5->5 6->6 7->7"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->4 1->7 2->3 3->2 4->5 5->1 6->6 7->0"

def test_set_random_seed():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    # TODO

def test_size():
    key = Key.create_random_key(19)
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_NONE)
    assert shuffle.size == 19

def test_get_bit():
    Key.set_random_seed(5551)
    Shuffle.set_random_seed(5552)
    key = Key.create_random_key(13)
    assert key.__str__() == "1011010010010"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == ("0->4 1->11 2->6 3->9 4->12 5->1 6->3 7->0 8->5 9->2 "
                                 "10->7 11->10 12->8")
    assert shuffle.get_bit(key, 0) == 0
    assert shuffle.get_bit(key, 1) == 1
    assert shuffle.get_bit(key, 2) == 0
    assert shuffle.get_bit(key, 12) == 1
    with pytest.raises(AssertionError):
        shuffle.get_bit(key, -1)
    with pytest.raises(AssertionError):
        shuffle.get_bit(key, 13)
    with pytest.raises(AssertionError):
        shuffle.get_bit(key, "hello")
    with pytest.raises(AssertionError):
        shuffle.get_bit("hello", 1)

def test_set_bit():
    Key.set_random_seed(6661)
    Shuffle.set_random_seed(6662)
    key = Key.create_random_key(6)
    assert key.__repr__() == "Key: 011110"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->2 3->4 4->5 5->3"
    shuffle.set_bit(key, 3, 0)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->2 3->4 4->5 5->3"
    assert key.__repr__() == "Key: 011100"
    shuffle.set_bit(key, 0, 1)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->2 3->4 4->5 5->3"
    assert key.__repr__() == "Key: 111100"
    shuffle.set_bit(key, 5, 0)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->2 3->4 4->5 5->3"
    assert key.__repr__() == "Key: 111000"
    with pytest.raises(AssertionError):
        shuffle.set_bit("hello", 1, 0)
    with pytest.raises(AssertionError):
        shuffle.set_bit(key, -1, 0)
    with pytest.raises(AssertionError):
        shuffle.set_bit(key, 13, 0)
    with pytest.raises(AssertionError):
        shuffle.set_bit(key, "hello", 0)
    with pytest.raises(AssertionError):
        shuffle.set_bit(key, 1, -1)
    with pytest.raises(AssertionError):
        shuffle.set_bit(key, 1, 2)
    with pytest.raises(AssertionError):
        shuffle.set_bit(key, 1, "hello")

def test_flip_bit():
    Key.set_random_seed(7771)
    Shuffle.set_random_seed(7772)
    key = Key.create_random_key(6)
    assert key.__repr__() == "Key: 010011"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->1 1->0 2->5 3->2 4->4 5->3"
    shuffle.flip_bit(key, 0)
    assert key.__repr__() == "Key: 000011"
    assert shuffle.__repr__() == "Shuffle: 0->1 1->0 2->5 3->2 4->4 5->3"
    with pytest.raises(AssertionError):
        shuffle.flip_bit("hello", 1)
    with pytest.raises(AssertionError):
        shuffle.flip_bit(key, -1)
    with pytest.raises(AssertionError):
        shuffle.flip_bit(key, 6)
    with pytest.raises(AssertionError):
        shuffle.flip_bit(key, "hello")

def test_get_key_index():
    Key.set_random_seed(9991)
    Shuffle.set_random_seed(9992)
    key = Key.create_random_key(6)
    assert key.__repr__() == "Key: 000110"
    shuffle = Shuffle(key.size, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->3 1->5 2->4 3->0 4->1 5->2"
    assert shuffle.get_key_index(0) == 3
    assert shuffle.get_key_index(1) == 5
    assert shuffle.get_key_index(5) == 2
    with pytest.raises(AssertionError):
        shuffle.get_key_index(-1)
    with pytest.raises(AssertionError):
        shuffle.get_key_index(6)
    with pytest.raises(AssertionError):
        shuffle.get_key_index("hello")
