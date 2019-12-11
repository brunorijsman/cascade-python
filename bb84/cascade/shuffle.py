import random
from bb84.cascade.key import Key

class Shuffle:

    _random = random.Random()

    SHUFFLE_NONE = 0
    """Do not shuffle the bits in the key."""
    SHUFFLE_RANDOM = 1
    """Randomly shuffle the bits in the key."""

    def __init__(self, size, algorithm):
        """
        Create a shuffle. A shuffle represents a permutation of the bits in a key. The shuffle
        can be random or deterministic depending on the shuffle algorithm. A Shuffle object is
        de-coupled from the Key objects: the same Shuffle object can be applied to multiple
        different Key objects, to permute (shuffle) the bits in those different keys according to
        the same pattern. In practice this allows Alice to shuffle the original sent key according
        to the same pattern as Bob shuffles the noisy received key when executing the Cascade
        protocol.

        Args:
            size (int): The size of the shuffle, i.e. the number of bits in the keys that this
                shuffle will be applied to. Must be >= 0 (i.e. empty shuffles are allowed).
            algorirthm (int): The algoritm for generating the shuffle pattern:
                SHUFFLE_NONE: Do not shuffle the key (keep the key bits in the original order).
                SHUFFLE_RANDOM: Randomly shuffle the key.
        """

        # Validate arguments.
        assert isinstance(size, int)
        assert size >= 0
        assert algorithm in [self.SHUFFLE_NONE, self.SHUFFLE_RANDOM]

        # Create a mapping from "shuffle indexes" to "key indexes".
        self._size = size
        self._shuffle_index_to_key_index = {}
        for shuffle_index in range(0, size):
            self._shuffle_index_to_key_index[shuffle_index] = shuffle_index
        if algorithm == self.SHUFFLE_RANDOM:
            random.shuffle(self._shuffle_index_to_key_index, Shuffle._random.random)

    def __repr__(self):
        """
        Get the unambiguous string representation of the shuffle.

        Returns:
            The unambiguous string representation of the shuffle.

        Example:
            >>> shuffle.__repr__()
            'Shuffle: 0->3 1->1 2->2 3->0 4->4 5->5'
        """
        return "Shuffle: " + self.__str__()

    def __str__(self):
        """
        Get the human-readable string representation of the shuffle.

        Returns:
            The human-readable string representation of the shuffle.

        Example:
            >>> shuffle.__str__()
            '0->3 1->1 2->2 3->0 4->4 5->5'
        """
        string = ""
        for shuffle_index in range(self.size):
            key_index = self._shuffle_index_to_key_index[shuffle_index]
            if string:
                string += " "
            string += f"{shuffle_index}->{key_index}"
        return string

    @staticmethod
    def set_random_seed(seed):
        """
        Set the seed for the isolated random number generated that is used only in the shuffle
        module and nowhere else. The application can set the seed to a specific value to make
        experimental results reproducable.

        Args:
            seed (int): The seed value for the random number generator which is isolated to the
                shuffle module.
        """
        Shuffle._random = random.Random(seed)

    @property
    def size(self):
        """
        Get the size of the shuffle in bits.

        Returns:
            The size of the shuffle in bits.
        """
        return self._size

    def get_key_index(self, shuffle_index):
        """
        Get the key index that a given shuffle index is mapped to.

        Args:
            shuffle_index (int): The shuffle index of the bit. Index must be in range
                [0, shuffle.size).

        Returns:
            The key index.
        """

        # Validate arguments.
        assert isinstance(shuffle_index, int)
        assert shuffle_index in self._shuffle_index_to_key_index

        # Return the key index.
        return self._shuffle_index_to_key_index[shuffle_index]

    def get_bit(self, key, shuffle_index):
        """
        Get a bit from a shuffled key.

        Args:
            key (Key): The key. We first shuffle this key according to this shuffle pattern and
                then retrieve the bit at shuffle_index in the shuffled key. The size of the key
                must be equal to the size of this shuffle.
            shuffle_index (int): The index of the bit in the shuffled key. The index must be in
                range [0, shuffle.size).

        Returns:
            The value (0 or 1) of the shuffled key bit at the given index.
        """

        # Validate arguments.
        assert isinstance(key, Key)
        assert key.size == self._size
        assert isinstance(shuffle_index, int)
        assert shuffle_index in self._shuffle_index_to_key_index

        # Return the key bit.
        key_index = self._shuffle_index_to_key_index[shuffle_index]
        return key.get_bit(key_index)

    def set_bit(self, key, shuffle_index, value):
        """
        Set a bit in a shuffled key to a given value.

        Args:
            key (Key): The key. We first shuffle this key according to this shuffle pattern and
                then set the bit at shuffle_index in the shuffled key to the given value. The size
                of the key must be equal to the size of this shuffle.
            shuffle_index (int): The index of the bit in the shuffled key. The index must be in
                range [0, shuffle.size).
            value (int): The new value of the bit. Must be 0 or 1.
        """

        # Validate arguments.
        assert isinstance(key, Key)
        assert key.size == self._size
        assert isinstance(shuffle_index, int)
        assert shuffle_index in self._shuffle_index_to_key_index
        assert isinstance(value, int)
        assert value in [0, 1]

        # Set the key bit.
        key_index = self._shuffle_index_to_key_index[shuffle_index]
        key.set_bit(key_index, value)

    def flip_bit(self, key, shuffle_index):
        """
        Flip a bit in a shuffled key (flip 0 to 1 and vice versa).

        Args:
            key (Key): The key. We first shuffle this key according to this shuffle pattern and
                then flip the bit at shuffle_index in the shuffled key. The size of the key must be
                equal to the size of this shuffle.
            shuffle_index (int): The index of the bit in the shuffled key. The index must be in
                range [0, shuffle.size).
        """

        # Validate arguments.
        assert isinstance(key, Key)
        assert key.size == self._size
        assert isinstance(shuffle_index, int)
        assert shuffle_index in self._shuffle_index_to_key_index

        # Flip the bit value.
        key_index = self._shuffle_index_to_key_index[shuffle_index]
        key.flip_bit(key_index)

    def calculate_parity(self, key, shuffle_start_index, shuffle_end_index):
        """
        Calculate the parity of a contiguous sub-range of bits in a shuffled key.

        Args:
            key (Key): The key for which to calculate the parity after shuffling it.
            shuffle_start_index (int): The index of the first bit (inclusive) in the range of
                bits in the shuffled key over which to calculate the parity.
            shuffle_end_index (int): The index of the last bit (exclusive) in the range of
                bits in the shuffled key over which to calculate the parity.

        Returns:
            The parity of the contiguous sub-range of bits in the shuffled key.
        """

        # Validate arguments.
        assert isinstance(key, Key)
        assert key.size == self._size
        assert isinstance(shuffle_start_index, int)
        assert shuffle_start_index in range(0, key.size)
        assert isinstance(shuffle_end_index, int)
        assert shuffle_end_index in range(0, key.size + 1)

        # Calculate the parity.
        parity = 0
        for shuffle_index in range(shuffle_start_index, shuffle_end_index):
            key_index = self._shuffle_index_to_key_index[shuffle_index]
            if key.get_bit(key_index):
                parity = 1 - parity
        return parity
