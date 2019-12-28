import math
from bb84.cascade.session import Session, ORIGINAL_PARAMETERS
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

# TODO: Finish this

def correct_key(parameters, seed, key_size, bit_error_rate, expected_bit_errors=0):

    Key.set_random_seed(seed)
    Shuffle.set_random_seed(seed+1)

    session = Session(parameters)

    # Create a random original (sent) key without errors.
    tx_key = Key.create_random_key(key_size)

    # Create the corresponding noisy (received) key with some random errors.
    bit_error_rate = 0.1
    nr_bit_errors = math.ceil(bit_error_rate * tx_key.size)
    rx_key = tx_key.copy(nr_bit_errors)

    # Function that performs Alice's job of providing the correct parity for a block.
    ask_correct_parity_function = lambda shuffle_identifier, start_index, end_index: \
        Shuffle.create_shuffle_from_identifier(shuffle_identifier).calculate_parity(
            tx_key, start_index, end_index)

    # Attempt to correct the noisy key by running the Cascade algorithm.
    session.correct_key(rx_key, bit_error_rate, ask_correct_parity_function)

    # Check if the number of remaining bit errors is what we expect it to be.
    bit_errors = tx_key.difference(rx_key)
    assert bit_errors == expected_bit_errors

def test_correct_key_default_parameters():
    for key_size in [32, 64, 100, 1000, 10000]:
        for bit_error_rate in [0.00, 0.01, 0.1, 0.2]:
            correct_key(ORIGINAL_PARAMETERS, 1111, key_size, bit_error_rate, 0)

# For profiling
# TODO: Move this to a separate profile.py and include in coverage test
if __name__ == "__main__":
    correct_key(ORIGINAL_PARAMETERS, 1111, 10000, 0.01, 0)
