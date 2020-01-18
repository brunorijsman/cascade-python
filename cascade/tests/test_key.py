from cascade.key import Key

def test_create_empty_key():
    key = Key()
    assert key.get_size() == 0

def test_create_random_key():
    Key.set_random_seed(111)
    key = Key.create_random_key(32)
    assert key.get_size() == 32
    assert key.get_bit(0) in [0, 1]
    assert key.get_bit(7) in [0, 1]
    assert key.get_bit(31) in [0, 1]
    key = Key.create_random_key(16)
    assert key.get_size() == 16
    assert key.__str__() == "1000111110000110"

def test_repr():
    Key.set_random_seed(222)
    key = Key()
    assert key.__repr__() == "Key: "
    key = Key.create_random_key(8)
    assert key.__repr__() == "Key: 00110010"

def test_str():
    Key.set_random_seed(222)
    key = Key()
    assert key.__str__() == ""
    key = Key.create_random_key(8)
    assert key.__str__() == "00110010"

def test_set_random_seed():
    Key.set_random_seed(333)
    key = Key.create_random_key(8)
    assert key.__str__() == "11010111"
    key = Key.create_random_key(8)
    assert key.__str__() == "10101010"
    key = Key.create_random_key(16)
    assert key.__str__() == "1111101101010000"
    # Resetting the seed to the same original value should produce the same sequence of random keys
    Key.set_random_seed(333)
    key = Key.create_random_key(8)
    assert key.__str__() == "11010111"
    key = Key.create_random_key(8)
    assert key.__str__() == "10101010"
    key = Key.create_random_key(16)
    assert key.__str__() == "1111101101010000"

def test_get_size():
    key = Key()
    assert key.get_size() == 0
    key = Key.create_random_key(7)
    assert key.get_size() == 7

def test_get_bit():
    Key.set_random_seed(1234)
    key = Key.create_random_key(11)
    assert key.__str__() == "10000001000"

def test_set_bit():
    Key.set_random_seed(2345)
    key = Key.create_random_key(13)
    assert key.__str__() == "1001011111011"
    key.set_bit(0, 0)
    assert key.__str__() == "0001011111011"
    key.set_bit(0, 1)
    assert key.__str__() == "1001011111011"
    key.set_bit(4, 0)
    assert key.__str__() == "1001011111011"
    key.set_bit(4, 1)
    assert key.__str__() == "1001111111011"
    key.set_bit(12, 0)
    assert key.__str__() == "1001111111010"
    key.set_bit(12, 1)
    assert key.__str__() == "1001111111011"

def test_flip_bit():
    Key.set_random_seed(3456)
    key = Key.create_random_key(9)
    assert key.__str__() == "111001100"
    key.flip_bit(0)
    assert key.__str__() == "011001100"
    key.flip_bit(3)
    assert key.__str__() == "011101100"
    key.flip_bit(8)
    assert key.__str__() == "011101101"

def test_copy_without_noise():

    Key.set_random_seed(3456)

    # Copy an empty key.
    key = Key()
    assert key.__str__() == ""
    key_copy = key.copy(0.0, Key.ERROR_METHOD_EXACT)
    assert key.__str__() == ""
    assert key_copy.__str__() == ""

    # Copy a non-empty key.
    key = Key.create_random_key(64)
    assert key.__str__() == "1110011000011110100111010001100011100000010011010101110100000010"
    key_copy = key.copy(0.0, Key.ERROR_METHOD_EXACT)
    assert key.__str__() == "1110011000011110100111010001100011100000010011010101110100000010"
    assert key_copy.__str__() == "1110011000011110100111010001100011100000010011010101110100000010"

    # Make sure that each key has an independent copy of the bits; i.e. that changing a bit in the
    # original key does not affect the copied key, or vice versa.
    key_copy.flip_bit(1)
    assert key.__str__() == "1110011000011110100111010001100011100000010011010101110100000010"
    assert key_copy.__str__() == "1010011000011110100111010001100011100000010011010101110100000010"

def test_copy_with_exact_noise():

    Key.set_random_seed(5678)

    # Copy a non-empty key with noise
    key = Key.create_random_key(6)
    assert key.__str__() == "001101"
    key_copy = key.copy(0.5, Key.ERROR_METHOD_EXACT)
    assert key.__str__() == "001101"
    assert key_copy.__str__() == "011011"

    # Make sure that each key has an independent copy of the bits; i.e. that changing a bit in the
    # original key does not affect the copied key, or vice versa.
    key_copy.flip_bit(1)
    assert key.__str__() == "001101"
    assert key_copy.__str__() == "001011"

    # Extreme case, flip all bits.
    key_copy = key.copy(1.0, Key.ERROR_METHOD_EXACT)
    assert key_copy.__str__() == "110010"

def test_copy_with_bernoulli_noise():

    Key.set_random_seed(5678)

    # Copy a non-empty key with noise
    key = Key.create_random_key(6)
    assert key.__str__() == "001101"
    key_copy = key.copy(0.5, Key.ERROR_METHOD_BERNOULLI)
    assert key.__str__() == "001101"
    assert key_copy.__str__() == "011100"

    # Make sure that each key has an independent copy of the bits; i.e. that changing a bit in the
    # original key does not affect the copied key, or vice versa.
    key_copy.flip_bit(1)
    assert key.__str__() == "001101"
    assert key_copy.__str__() == "001100"

    # Extreme case, flip probability 1.0.
    key_copy = key.copy(1.0, Key.ERROR_METHOD_BERNOULLI)
    assert key_copy.__str__() == "110010"

def test_difference():
    # Normal case.
    key = Key.create_random_key(64)
    key_copy = key.copy(0.078125, Key.ERROR_METHOD_EXACT)
    assert key.difference(key_copy) == 5
    # Special case: compare with self.
    assert key.difference(key) == 0
    # Special case: empty key.
    empty_key_1 = Key()
    empty_key_2 = Key()
    assert empty_key_1.difference(empty_key_2) == 0
