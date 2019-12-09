import random
from bb84.cascade.key import Key

class Shuffle:

    ALGORITHM_NONE = 0
    ALGORITHM_RANDOM = 1

    def __init__(self, key, algorithm, seed=None):
        """
        Create a shuffle, i.e. shuffle the bits of a key according to some algorithm.

        Params:
            key (Key): The key to be shuffled. The key itself is not modified in any way; all the
                bookkeeping to keep track of the shuffling is in the created Shuffle object.
            algorirthm (int): The algorithm used to shuffle the key:
                ALGORITHM_NONE: Do not shuffle the key (keep the key bits in the original order).
                ALGORITHM_RANDOM: Randomly shuffle th key.
            seed(None or int): The seed value for the random number generator for algorithm
                to ALGORITHM_RANDOM. Using the same seed value is guaranteed to produce the same
                shuffle order. This is intended to allow experiments to be reproduced exactly.
        """

        # Validate arguments.
        assert isinstance(key, Key)
        assert algorithm in [self.ALGORITHM_NONE, self.ALGORITHM_RANDOM]
        assert seed is None or isinstance(seed, int)
        if algorithm != self.ALGORITHM_RANDOM:
            assert seed is None

        # The key underlying this block.
        self._key = key

        # Map the shuffle indexes to key indexes.
        self._shuffle_index_to_key_index = {}
        for index in range(0, key.size):
            self._shuffle_index_to_key_index[index] = index
        if algorithm == self.ALGORITHM_RANDOM:
            local_random = random.Random(seed)
            local_random.shuffle(self._shuffle_index_to_key_index, local_random.random)

    def get_key_bit(self, shuffle_index):
        """
        Get the key bit value for the given shuffle index.

        Params:
            shuffle_index (int): The shuffle index.

        Returns:
            The key bit value for the given shuffle index.
        """

        # Validate arguments.
        assert isinstance(shuffle_index, int)
        assert shuffle_index in self._shuffle_index_to_key_index

        # Return the key bit.
        key_index = self._shuffle_index_to_key_index[shuffle_index]
        return self._key.get_bit(key_index)
