import pytest
import test_common

@pytest.fixture(scope="function", autouse=True)
def start_stop_simulaqron():
    test_common.start_simulaqron(True)
    yield
    test_common.stop_simulaqron()

def run_eve_not_observing_scenario(key_size, block_size, window_size):

    (alice, bob, eve) = test_common.run_nodes(key_size, block_size, window_size, True, 0)

    alice_key = alice.key_str()
    print(f"Alice key: {alice_key}")
    assert len(alice_key) == key_size
    for c in alice_key:
        assert c in ['0', '1']

    bob_key = bob.key_str()
    print(f"Bob key: {bob_key}")
    assert len(bob_key) == key_size
    for c in alice_key:
        assert c in ['0', '1']

    assert alice_key == bob_key

    eve_key = eve.key_str()
    assert eve_key == '.' * key_size

def test_key_16_block_4_window_2():
    run_eve_not_observing_scenario(key_size=16, block_size=4, window_size=2)

def test_key_64_block_32_window_8():
    run_eve_not_observing_scenario(key_size=64, block_size=32, window_size=8)

def test_key_16_block_4_window_1():
    # Window size is degenerate value of 1
    run_eve_not_observing_scenario(key_size=16, block_size=4, window_size=1)

def test_key_16_block_4_window_4():
    # Block size is same as window size
    run_eve_not_observing_scenario(key_size=16, block_size=4, window_size=4)

def test_key_8_block_8_window_4():
    # Key size is same as block size
    run_eve_not_observing_scenario(key_size=8, block_size=8, window_size=4)

def test_key_8_block_8_window_8():
    # Key size, block size, and window size are all the same
    run_eve_not_observing_scenario(key_size=8, block_size=8, window_size=8)

def test_key_27_block_8_window_4():
    # Key size is not a multiple of block size
    run_eve_not_observing_scenario(key_size=27, block_size=8, window_size=4)
