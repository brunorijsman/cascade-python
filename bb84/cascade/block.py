from bb84.cascade.key import Key

class Block:

    def __init__(self, key):
        """
        Create a block from a key. The block contains all bits in the key.

        Params:
            key (Key): the key from which to create the block.
        """

        # Validate arguments
        assert isinstance(key, Key)

        # The key underlying this block
        self._key = key

        # The ordered sub-set of bits in the key that are used in this block. In this case,
        # the block uses all bits in the key in the original key order.
        self._key_bit_indices = range(0, key.size)
