from cascade.key import Key
from cascade.shuffle import Shuffle

def test_create_shuffle_keep_same():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)

    # Empty shuffle.
    key = Key()
    assert key.__str__() == ""
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
    assert shuffle.__str__() == ""

    # Non-empty shuffle.
    key = Key.create_random_key(8)
    assert key.__str__() == "00101100"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
    assert shuffle.__str__() == "0->0 1->1 2->2 3->3 4->4 5->5 6->6 7->7"
    for index in range(key.get_size()):
        assert shuffle.get_bit(key, index) == key.get_bit(index)

def test_create_shuffle_random():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)

    # Empty shuffle.
    key = Key()
    assert key.__str__() == ""
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == ""

    # Non-empty shuffle.
    key = Key.create_random_key(16)
    assert key.__str__() == "0010110001010010"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == ("0->2 1->9 2->8 3->7 4->3 5->12 6->1 7->5 8->13 "
                                 "9->6 10->0 11->14 12->10 13->4 14->11 15->15")
    key = Key()
    assert key.__str__() == ""

def test_create_shuffle_from_identifier():
    Key.set_random_seed(1111)
    Shuffle.set_random_seed(1112)

    # Empty keep-same shuffle
    key = Key()
    original_shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
    recreated_shuffle = Shuffle.create_shuffle_from_identifier(original_shuffle.get_identifier())
    assert original_shuffle.__repr__() == recreated_shuffle.__repr__()

    # Empty random shuffle
    key = Key()
    original_shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    recreated_shuffle = Shuffle.create_shuffle_from_identifier(original_shuffle.get_identifier())
    assert original_shuffle.__repr__() == recreated_shuffle.__repr__()

    # Non-empty keep-same shuffle
    key = Key.create_random_key(32)
    original_shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
    recreated_shuffle = Shuffle.create_shuffle_from_identifier(original_shuffle.get_identifier())
    assert original_shuffle.__repr__() == recreated_shuffle.__repr__()

    # Non-empty random shuffle
    key = Key.create_random_key(32)
    original_shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    recreated_shuffle = Shuffle.create_shuffle_from_identifier(original_shuffle.get_identifier())
    assert original_shuffle.__repr__() == recreated_shuffle.__repr__()

def test_encode_identifier():
    # pylint:disable=protected-access
    assert Shuffle._encode_identifier(0, 0, 0) == 0
    assert Shuffle._encode_identifier(1, 2, 3) == 302000000001
    assert Shuffle._encode_identifier(999999999, 99, 999999999999) == 99999999999999999999999

def test_decode_identifier():
    # pylint:disable=protected-access
    assert Shuffle._decode_identifier(0) == (0, 0, 0)
    assert Shuffle._decode_identifier(302000000001) == (1, 2, 3)
    assert Shuffle._decode_identifier(99999999999999999999999) == (999999999, 99, 999999999999)

def test_repr():
    Key.set_random_seed(2221)
    Shuffle.set_random_seed(2222)
    key = Key.create_random_key(8)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->2 3->3 4->4 5->5 6->6 7->7"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->0 1->1 2->6 3->4 4->3 5->2 6->5 7->7"

def test_str():
    Key.set_random_seed(3331)
    Shuffle.set_random_seed(3332)
    key = Key.create_random_key(8)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
    assert shuffle.__str__() == "0->0 1->1 2->2 3->3 4->4 5->5 6->6 7->7"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->0 1->4 2->2 3->6 4->7 5->3 6->1 7->5"

def test_set_random_seed():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    key = Key.create_random_key(8)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == "0->1 1->3 2->2 3->7 4->5 5->6 6->4 7->0"

def test_get_size():
    key = Key.create_random_key(19)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_KEEP_SAME)
    assert shuffle.get_size() == 19

def test_get_identifier():
    Key.set_random_seed(4441)
    Shuffle.set_random_seed(4442)
    key = Key.create_random_key(8)
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.get_identifier() == 18048933084901000000008

def test_get_key_index():
    Shuffle.set_random_seed(9992)
    shuffle = Shuffle(6, Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->5 1->4 2->2 3->0 4->1 5->3"
    assert shuffle.get_key_index(0) == 5
    assert shuffle.get_key_index(1) == 4
    assert shuffle.get_key_index(5) == 3

def test_get_bit():
    Key.set_random_seed(5551)
    Shuffle.set_random_seed(5552)
    key = Key.create_random_key(13)
    assert key.__str__() == "1011010010010"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__str__() == ("0->5 1->9 2->3 3->12 4->10 5->6 6->11 7->7 8->0 9->4 "
                                 "10->1 11->2 12->8")
    assert shuffle.get_bit(key, 0) == 1   # Shuffle bit 0 -> Key bit 5 -> Bit value 1
    assert shuffle.get_bit(key, 1) == 0   # Shuffle bit 1 -> Key bit 9 -> Bit value 0
    assert shuffle.get_bit(key, 2) == 1   # Shuffle bit 2 -> Key bit 3 -> Bit value 1
    assert shuffle.get_bit(key, 12) == 1  # Shuffle bit 12 -> Key bit 8 -> Bit value 1

def test_set_bit():
    Key.set_random_seed(6661)
    Shuffle.set_random_seed(6662)
    key = Key.create_random_key(6)
    assert key.__repr__() == "Key: 011110"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->1 1->5 2->0 3->4 4->2 5->3"
    shuffle.set_bit(key, 3, 0)                  # Shuffle bit 3 -> Key bit 4 -> Bit value 1->0
    assert key.__repr__() == "Key: 011100"
    shuffle.set_bit(key, 0, 1)                  # Shuffle bit 0 -> Key bit 1 -> Bit value 1->1
    assert key.__repr__() == "Key: 011100"
    shuffle.set_bit(key, 5, 0)                  # Shuffle bit 5 -> Key bit 3 -> Bit value 0->0
    assert key.__repr__() == "Key: 011000"

def test_flip_bit():
    Key.set_random_seed(7771)
    Shuffle.set_random_seed(7772)
    key = Key.create_random_key(6)
    assert key.__repr__() == "Key: 010011"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->5 1->2 2->4 3->3 4->1 5->0"
    shuffle.flip_bit(key, 0)                    # Shuffle bit 0 -> Key bit 5 -> Bit value 1->0
    assert key.__repr__() == "Key: 010010"

def test_calculate_parity():
    Key.set_random_seed(8881)
    Shuffle.set_random_seed(8882)
    key = Key.create_random_key(10)
    assert key.__repr__() == "Key: 1011111100"
    shuffle = Shuffle(key.get_size(), Shuffle.SHUFFLE_RANDOM)
    assert shuffle.__repr__() == "Shuffle: 0->1 1->4 2->5 3->9 4->6 5->0 6->7 7->2 8->3 9->8"
    assert shuffle.__str__() == "0->1 1->4 2->5 3->9 4->6 5->0 6->7 7->2 8->3 9->8"
    assert shuffle.calculate_parity(key, 0, 10) == 1
    assert shuffle.calculate_parity(key, 4, 8) == 0
    assert shuffle.calculate_parity(key, 1, 2) == 1
