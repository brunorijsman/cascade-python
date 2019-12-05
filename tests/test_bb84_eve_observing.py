import pytest
from .common import *

@pytest.fixture(scope="function", autouse=True)
def start_stop_simulaqron():
    start_simulaqron(True)
    yield
    stop_simulaqron()

def run_eve_observing_scenario(key_size, block_size, window_size):

    (alice, bob, eve) = run_nodes(key_size, block_size, window_size, True, 50)

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

    eve_key = eve.key_str()
    print(f"Eve key: {eve_key}")
    assert len(eve_key) == key_size
    for c in alice_key:
        assert c in ['0', '1', '.', '?']

    for i in range(key_size):
        if eve_key[i] == '.':
            # Eve did not observe, so Alice and Bob must have same key bit
            assert alice_key[i] == bob_key[i]
        elif eve_key[i] in ['0', '1']:
            # Eve guessed the correct basis, so Alice and Bob must have same key bit
            assert alice_key[i] == bob_key[i]
        else:
            # Eve guessed the wrong basis, so Alice and Bob may or may not have the same bit
            pass

def test_key_16_block_4_window_2():
    run_eve_observing_scenario(key_size=16, block_size=4, window_size=2)

def test_key_64_block_32_window_8():
    run_eve_observing_scenario(key_size=64, block_size=32, window_size=8)

def test_key_16_block_4_window_1():
    # Window size is degenerate value of 1
    run_eve_observing_scenario(key_size=16, block_size=4, window_size=1)

def test_key_16_block_4_window_4():
    # Block size is same as window size
    run_eve_observing_scenario(key_size=16, block_size=4, window_size=4)

def test_key_8_block_8_window_4():
    # Key size is same as block size
    run_eve_observing_scenario(key_size=8, block_size=8, window_size=4)

def test_key_8_block_8_window_8():
    # Key size, block size, and window size are all the same
    run_eve_observing_scenario(key_size=8, block_size=8, window_size=8)

def test_key_27_block_8_window_4():
    # Key size is not a multiple of block size
    run_eve_observing_scenario(key_size=27, block_size=8, window_size=4)
