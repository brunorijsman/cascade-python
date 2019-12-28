import math
from bb84.cascade.parameters import ORIGINAL_PARAMETERS
from bb84.cascade.session import Session

def correct_key(parameters, seed, key_size, bit_error_rate, expected_bit_errors=0):

    # Create mock session and Alice's key.
    (session, alice_key) = Session.create_mock_session_and_key(key_size, seed, seed+1, parameters)

    # Create the corresponding noisy key with some random errors as received by Bob.
    nr_bit_errors = math.ceil(bit_error_rate * alice_key.size)
    bob_key = alice_key.copy(error_count=nr_bit_errors)

    # Attempt to correct the noisy key by running the Cascade algorithm.
    session.correct_key(bob_key, bit_error_rate)

    # Check if the number of remaining bit errors is what we expect it to be.
    bit_errors = alice_key.difference(bob_key)
    assert bit_errors == expected_bit_errors

def test_correct_key_default_parameters():
    for key_size in [32, 64, 100, 1000, 10000]:
        for bit_error_rate in [0.00, 0.01, 0.1, 0.2]:
            correct_key(ORIGINAL_PARAMETERS, 1111, key_size, bit_error_rate, 0)

# For profiling
# TODO: Move this to a separate profile.py and include in coverage test
if __name__ == "__main__":
    correct_key(ORIGINAL_PARAMETERS, 1111, 10000, 0.01, 0)
