import copy
import random

class Key:
    """
    A key that is used to symmetrically encrypt and decrypt messages.
    """
    _random = random.Random()

    def __init__(self):
        """
        Create an empty key.
        """

        self._size = 0
        self._bits = {}  # Bits are stored as dictionary, indexed by index [0..size), value 0 or 1.

    @staticmethod
    def create_random_key(size):
        """
        Create an random key.

        Args:
            size (int): The size of the key in bits. Must be >= 0.

        Returns:
            A new key of the specified size with random bits.
        """

        # Validate arguments.
        assert isinstance(size, int)
        assert size >= 0

        # Create a new random key.
        # pylint:disable=protected-access
        key = Key()
        key._size = size
        for i in range(size):
            key._bits[i] = Key._random.randint(0, 1)

        return key

    def __repr__(self):
        """
        Get the unambiguous string representation of the key.

        Returns:
            The unambiguous string representation of the key.
        """
        return "Key: " + self.__str__()

    def __str__(self):
        """
        Get the human-readable string representation of the key.

        Returns:
            The human-readable string representation of the key.
        """
        string = ""
        for i in range(self._size):
            string += str(self._bits[i])
        return string

    @staticmethod
    def set_random_seed(seed):
        """
        Set the seed for the isolated random number generated that is used only in the key
        module and nowhere else. The application can set the seed to a specific value to make
        experimental stats reproduceable.

        Args:
            seed (int): The seed value for the random number generator which is isolated to the
                shuffle module.
        """
        Key._random = random.Random(seed)

    def get_size(self):
        """
        Get the size of the key in bits.

        Returns:
            The size of the key in bits.
        """
        return self._size

    def get_bit(self, index):
        """
        Get the value of the key bit at a given index.

        Args:
            index (int): The index of the bit. Index must be in range [0, key.size).

        Returns:
            The value (0 or 1) of the key bit at the given index.
        """

        # Validate arguments.
        assert isinstance(index, int)
        assert 0 <= index < self._size

        # Return the bit value.
        return self._bits[index]

    def set_bit(self, index, value):
        """
        Set the value of the key bit at a given index.

        Args:
            index (int): The index of the bit. Index must be in range [0, key.size).
            value (int): The new value of the bit. Must be 0 or 1.
        """

        # Validate arguments.
        assert isinstance(index, int)
        assert 0 <= index < self._size
        assert isinstance(value, int)
        assert value in [0, 1]

        # Set the bit value.
        self._bits[index] = value

    def flip_bit(self, index):
        """
        Flip the value of the key bit at a given index (0 to 1, and vice versa).

        Args:
            index (int): The index of the bit. Index must be in range [0, key.size).
        """

        # Validate arguments.
        assert isinstance(index, int)
        assert 0 <= index < self._size

        # Flip the bit value.
        self._bits[index] = 1 - self._bits[index]

    def copy(self, error_count=None, error_rate=None):
        """
        Copy a key and optionally apply noise.

        Args:
            error_count (None or int): If None, ignore. If an int, the exact number of bits that
                are flipped in the copy of the key.
            error_rate (None or float): If None, ignore. If a float, the probability that each
                individual bit is flipped in the copy of they.

            If error_count and error_rate are both None, then no bit flip errors are introduced in
            the copy. Error_count and error_rate cannot both be non-None.

        Returns:
            A new Key instance, which is a copy of this key, with noise applied if asked for.
        """

        # Validate arguments.
        if error_count is not None:
            assert isinstance(error_count, int)
            assert 0 <= error_count <= self._size
            assert error_rate is None
        if error_rate is not None:
            assert isinstance(error_rate, float)
            assert 0.0 <= error_rate <= 1.0
            assert error_count is None

        # Create a new key which is a copy of this one.
        # pylint:disable=protected-access
        key = Key()
        key._size = self._size
        key._bits = copy.deepcopy(self._bits)

        # First option for applying noise: flip the exact number of requested bits.
        if error_count is not None:
            bits_to_flip = Key._random.sample(self._bits.keys(), error_count)
            for index in bits_to_flip:
                key._bits[index] = 1 - key._bits[index]

        # Second option for applying noise:
        if error_rate is not None:
            for index in self._bits.keys():
                if Key._random.random() <= error_rate:
                    key._bits[index] = 1 - key._bits[index]

        return key

    def difference(self, other_key):
        """
        Return the number of bits that are different between this key and the other_key (also known
        as the Hamming distance).

        Args:
            other_key (Key): The other key that this key has to be compared with. Must be the same
                size as this key.

        Returns:
            The number of bits that are different between this key and the other key.
        """

        # Validate arguments.
        # pylint:disable=protected-access
        assert isinstance(other_key, Key)
        assert self._size == other_key._size

        # Compute difference.
        difference = 0
        for i in range(self._size):
            if self._bits[i] != other_key._bits[i]:
                difference += 1
        return difference
