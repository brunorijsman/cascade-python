import json
import random

from bb84.cascade.key import Key
from bb84.cascade.mock_classical_channel import MockClassicalChannel
from bb84.cascade.parameters import ORIGINAL_PARAMETERS
from bb84.cascade.reconciliation import Reconciliation
from bb84.cascade.shuffle import Shuffle
from bb84.cascade.stats import Stats

REPETITIONS = 5

def run_one_key_correction(parameters, seed, key_size, bit_error_rate):

    if seed is None:
        seed = random.randint(1, 1_000_000_000_000)

    print(f"Experiment")
    print(f" parameters={json.dumps(parameters, default=lambda o: o.__dict__)}")
    print(f" seed={seed}")
    print(f" key_size={key_size}")
    print(f" bit_error_rate={bit_error_rate}")

    Key.set_random_seed(seed)
    Shuffle.set_random_seed(seed+1)

    # Create a random original (sent) key without errors.
    correct_key = Key.create_random_key(key_size)

    # Create the corresponding noisy (received) key with some random errors.
    noisy_key = correct_key.copy(error_rate=bit_error_rate)

    # Create a mock reconciliation.
    stats = Stats()
    mock_classical_channel = MockClassicalChannel(correct_key, stats)
    reconciliation = Reconciliation(parameters, mock_classical_channel, noisy_key, bit_error_rate,
                                    stats)

    # Do the reconciliation.
    reconciliated_key = reconciliation.reconcile()

    # Update statistics for bit errors and frame errors
    bit_errors = correct_key.difference(reconciliated_key)
    reconciliation.stats.bit_errors += bit_errors
    if bit_errors > 0:
        reconciliation.stats.frame_errors += 1

    print(f" stats={json.dumps(stats.__dict__)}")

def run_experiment_series_increasing_error_rate(parameters, key_size):
    bit_error_rate = 0.00
    while bit_error_rate <= 0.12:
        run_one_key_correction(parameters, None, key_size, bit_error_rate)
        bit_error_rate += 0.01

def run_all_experiments():
    key_size = 10_000
    run_experiment_series_increasing_error_rate(ORIGINAL_PARAMETERS, key_size)

if __name__ == "__main__":
    run_all_experiments()
