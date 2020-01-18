import copy
import random

class Key:
    """
    A key that the Cascade protocol reconciles.
    """
    _random = random.Random()

    ERROR_METHOD_BERNOULLI = "bernoulli"
    ERROR_METHOD_EXACT = "exact"
    ERROR_METHODS = [ERROR_METHOD_BERNOULLI, ERROR_METHOD_EXACT]

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
            A random key of the specified size.
        """
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
        module and nowhere else. If two applications set the seed to the same value, the key
        module produces the exact same sequence of random keys. This is used to make experiments
        reproduceable.

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
        return self._bits[index]

    def set_bit(self, index, value):
        """
        Set the value of the key bit at a given index.

        Args:
            index (int): The index of the bit. Index must be in range [0, key.size).
            value (int): The new value of the bit. Must be 0 or 1.
        """
        self._bits[index] = value

    def flip_bit(self, index):
        """
        Flip the value of the key bit at a given index (0 to 1, and vice versa).

        Args:
            index (int): The index of the bit. Index must be in range [0, key.size).
        """
        self._bits[index] = 1 - self._bits[index]

    def copy(self, error_rate, error_method):
        """
        Copy a key and optionally apply noise.

        Args:
            error_rate (float): The requested error rate.
            error_method (str): The method for choosing errors. Must be one of the error methods in
                ERROR_METHODS.

        Returns:
            A new Key instance, which is a copy of this key, with noise applied.
        """
        # pylint:disable=protected-access
        key = Key()
        key._size = self._size
        key._bits = copy.deepcopy(self._bits)

        if error_method == self.ERROR_METHOD_EXACT:
            error_count = round(error_rate * self._size)
            bits_to_flip = Key._random.sample(self._bits.keys(), error_count)
            for index in bits_to_flip:
                key._bits[index] = 1 - key._bits[index]

        if error_method == self.ERROR_METHOD_BERNOULLI:
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
        difference = 0
        for i in range(self._size):
            # pylint:disable=protected-access
            if self._bits[i] != other_key._bits[i]:
                difference += 1
        return difference
