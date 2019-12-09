
from bb84.cascade.block import Block
from bb84.cascade.key import Key

def test_create_block_from_key():
    key = Key.create_random_key(32)
    _block = Block(key)
