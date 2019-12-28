import json

from bb84.cascade.session import Session, ORIGINAL_PARAMETERS
from bb84.cascade.key import Key
from bb84.cascade.shuffle import Shuffle

REPETITIONS = 5

def run_one_key_correction(parameters, seed, key_size, bit_error_rate):

    print(f"Experiment")
    print(f" parameters={json.dumps(parameters, default=lambda o: o.__dict__)}")
    print(f" seed={seed}")
    print(f" key_size={key_size}")
    print(f" bit_error_rate={bit_error_rate}")

    Key.set_random_seed(seed)
    Shuffle.set_random_seed(seed+1)

    session = Session(parameters)

    # Create a random original (sent) key without errors.
    tx_key = Key.create_random_key(key_size)

    # Create the corresponding noisy (received) key with some random errors.
    rx_key = tx_key.copy(error_rate=bit_error_rate)

    # Function that performs Alice's job of providing the correct parity for a block.
    ask_correct_parity_function = lambda shuffle_identifier, start_index, end_index: \
        Shuffle.create_shuffle_from_identifier(shuffle_identifier).calculate_parity(
            tx_key, start_index, end_index)

    # Attempt to correct the noisy key by running the Cascade algorithm.
    session.correct_key(rx_key, bit_error_rate, ask_correct_parity_function)

    # Update statistics for bit errors and frame errors
    bit_errors = tx_key.difference(rx_key)
    session.stats.bit_errors += bit_errors
    if bit_errors > 0:
        session.stats.frame_errors += 1

    print(f" stats={json.dumps(session.stats.__dict__)}")

def run_experiment_series_increasing_ber(parameters, key_size):
    bit_error_rate = 0.00
    while bit_error_rate <= 0.12:
        seed = 1234   # TODO
        run_one_key_correction(parameters, seed, key_size, bit_error_rate)
        bit_error_rate += 0.01

def run_all_experiments():
    key_size = 10_000   # TODO
    run_experiment_series_increasing_ber(ORIGINAL_PARAMETERS, key_size)

if __name__ == "__main__":
    run_all_experiments()
