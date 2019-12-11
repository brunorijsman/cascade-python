class Session:
    """
    A Cascade session. Represents the state of a single information reconciliation exchange in
    progress between a client and a server. This state is stored in an object to allow multiple
    information reconciliation sessions to happen concurrently and still keep their state separate.
    """

    def __init__(self):
        """
        Create a Cascade session.
        """

        # Map key indexes to bloks.
        self._key_index_to_blocks = {}

        # Map iterations to error block priority queues.
        self._iteration_to_error_block_queue = {}

    def register_block(self, block):
        """
        Register the existence of a new block.
        """

        # Cannot validate isinstance(block, Block) because that would cause a circular import
        # dependency.

        # For every key bit covered by the block, append the block to the list of blocks that depend
        # on that partical key bit.
        for key_index in block.key_indexes:
            if key_index in self._key_index_to_blocks:
                assert block not in self._key_index_to_blocks[key_index]
                self._key_index_to_blocks[key_index].append(block)
            else:
                self._key_index_to_blocks[key_index] = [block]

    def get_blocks_containing_key_index(self, key_index):
        """
        Get a list of block that contain a given key index.

        Args:
            key_index (int): The key index that we are looking for.

        Returns:
            The list of block that contain a given key index.
        """
        assert isinstance(key_index, int)
        assert key_index >= 0
        return self._key_index_to_blocks.get(key_index, [])
