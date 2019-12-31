import json
import random
import git

from cascade.key import Key
from cascade.mock_classical_channel import MockClassicalChannel
from cascade.algorithm import ORIGINAL_ALGORITHM
from cascade.reconciliation import Reconciliation
from cascade.shuffle import Shuffle
from cascade.stats import Stats

REPETITIONS = 5

def get_code_version():
    try:
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        return str(sha)
    except git.InvalidGitRepositoryError:
        return "unknown"

def run_one_key_correction(algorithm, seed, key_size, bit_error_rate):

    if seed is None:
        seed = random.randint(1, 1_000_000_000_000)

    print(f"Experiment")
    print(f" algorithm={json.dumps(algorithm, default=lambda o: o.__dict__)}")
    print(f" seed={seed}")
    print(f" key_size={key_size}")
    print(f" bit_error_rate={bit_error_rate}")

    Key.set_random_seed(seed)
    Shuffle.set_random_seed(seed+1)

    # Create a random original (sent) key without errors.
    correct_key = Key.create_random_key(key_size)

    # Create the corresponding noisy (received) key with some random errors.
    noisy_key = correct_key.copy(error_rate=bit_error_rate)

    # Prepare stats block with code version.
    stats = Stats()
    stats.code_version = get_code_version()

    # Create a mock reconciliation.
    mock_classical_channel = MockClassicalChannel(correct_key, stats)
    reconciliation = Reconciliation(algorithm, mock_classical_channel, noisy_key, bit_error_rate,
                                    stats)

    # Do the reconciliation.
    reconciliated_key = reconciliation.reconcile()

    # Update statistics for bit errors and frame errors
    bit_errors = correct_key.difference(reconciliated_key)
    reconciliation.stats.remaining_bit_errors += bit_errors
    if bit_errors > 0:
        reconciliation.stats.remaining_frame_errors += 1

    print(f" stats={json.dumps(stats.__dict__)}")

def run_experiment_series_increasing_error_rate(algorithm, key_size):
    bit_error_rate = 0.00
    while bit_error_rate <= 0.12:
        run_one_key_correction(algorithm, None, key_size, bit_error_rate)
        bit_error_rate += 0.01

def run_all_experiments():
    key_size = 10_000
    run_experiment_series_increasing_error_rate(ORIGINAL_ALGORITHM, key_size)

if __name__ == "__main__":
    run_all_experiments()
