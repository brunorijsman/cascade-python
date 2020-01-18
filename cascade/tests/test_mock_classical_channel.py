from cascade.block import Block
from cascade.mock_classical_channel import MockClassicalChannel
from cascade.key import Key
from cascade.shuffle import Shuffle

def test_create_mock_classical_channel():
    Key.set_random_seed(1)
    correct_key = Key.create_random_key(32)
    _channel = MockClassicalChannel(correct_key)

def test_start_and_end_reconciliation():
    Key.set_random_seed(2)
    correct_key = Key.create_random_key(32)
    channel = MockClassicalChannel(correct_key)
    channel.start_reconciliation()
    channel.end_reconciliation()

def test_ask_parities():
    Key.set_random_seed(3)
    Shuffle.set_random_seed(77716)
    correct_key = Key.create_random_key(32)
    shuffle = Shuffle(correct_key.get_size(), Shuffle.SHUFFLE_RANDOM)
    blocks = Block.create_covering_blocks(correct_key, shuffle, 8)
    assert len(blocks) == 4
    assert blocks[0].__str__() == "01010011"
    assert blocks[1].__str__() == "01011100"
    assert blocks[2].__str__() == "10110001"
    assert blocks[3].__str__() == "01001110"
    channel = MockClassicalChannel(correct_key)
    channel.start_reconciliation()
    parities = channel.ask_parities(blocks)
    assert parities[0] == 0
    assert parities[1] == 0
    assert parities[2] == 0
    assert parities[3] == 0
    channel.end_reconciliation()
