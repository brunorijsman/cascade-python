class Key:

    def __init__(self, key_size, copy_of_key=None, error_rate=None):
        """
        Create a key.

        Args:
            key_size (int): The size of the key in bits
            copy_of_key (None or Key): If not None, set the bits in this key to random values.
                If not None, create a copy of this key
            error_rate (None or float between 0.0 and 1.0 inclusive): If None, no noise is applied.
                If not None, this is the probability of a bit flip when copying a key. 
        """

        # Validate arguments
        assert isinstance(key_size, int)
        assert key_size > 0
        assert copy_of_key is None or isinstance(copy_of_key, Key)
        assert error_rate is None or isinstance(error_rate, float)
        if error_rate is not None:
            assert copy_of_key is not None
            assert 0.0 <= error_rate <= 1.0

        # Bits are stored as dictionary, indexed by index [0..key_size), value 0 or 1
        self._bits = {}

        if copy_of_key:

            # Copy bits from another key, and apply noise if asked to do so.
            for i in range(key_size):
                bit_value = copy_of_key._bit[i]
                if error_rate and random.random() < error_rate:
                    bit_value = 1 - bit_value
                self._bits[i] = bit_value
            
        else:

            # Create a new random key
            for i in range(key_size):
                self._bits[i] = random.randint(0, 1)

    def split_into_blocks(self, block_size, shuffle):
        pass