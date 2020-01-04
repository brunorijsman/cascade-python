import argparse
import json
import git

from cascade.key import Key
from cascade.mock_classical_channel import MockClassicalChannel
from cascade.algorithm import ORIGINAL_ALGORITHM
from cascade.reconciliation import Reconciliation
from cascade.stats import Stats

DEFAULT_ALGORITHM = "original"
DEFAULT_ERROR_RATE = 0.01
DEFAULT_KEY_SIZE = 10_000
DEFAULT_RUNS = 100    # TODO: Make this a larger number

ALGORITHMS = {
    "original": ORIGINAL_ALGORITHM,
    "biconf": None,   # TODO
    "yanetal": None   # TODO
}

def error_rate_type(arg):
    try:
        error_rate = float(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("must be a floating point number")
    if error_rate < 0.00 or error_rate > 1.00:
        raise argparse.ArgumentTypeError("must be >= 0.0 and <= 1.0")
    return error_rate

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description="Run Cascade reconciliations")
    parser.add_argument('-a', '--algorithm', type=str, default=DEFAULT_ALGORITHM,
                        help=f"cascade algorithm (default {DEFAULT_ALGORITHM})")
    parser.add_argument('-e', '--error-rate', type=error_rate_type, default=DEFAULT_ERROR_RATE,
                        help=f"quantum bit error rate (default {DEFAULT_ERROR_RATE})")
    parser.add_argument('-k', '--key-size', type=int, default=10000,
                        help=f"key size (default {DEFAULT_KEY_SIZE})")
    parser.add_argument('-r', '--runs', type=int, default=DEFAULT_RUNS,
                        help=f"number of reconciliation runs (default {DEFAULT_RUNS})")
    args = parser.parse_args()
    return args

def run_experiment(runs, algorithm_name, key_size, error_rate):
    for run in range(runs):
        run_reconciliation(run, algorithm_name, key_size, error_rate)
    # stats.code_version = get_code_version()

def run_reconciliation(run, algorithm_name, key_size, error_rate):
    # Key.set_random_seed(seed)
    # Shuffle.set_random_seed(seed+1)
    correct_key = Key.create_random_key(key_size)
    noisy_key = correct_key.copy(error_rate=error_rate)
    stats = Stats()
    mock_classical_channel = MockClassicalChannel(correct_key, stats)
    algorithm = ALGORITHMS[algorithm_name]
    reconciliation = Reconciliation(algorithm, mock_classical_channel, noisy_key, error_rate,
                                    stats)
    reconciliated_key = reconciliation.reconcile()
    bit_errors = correct_key.difference(reconciliated_key)
    reconciliation.stats.remaining_bit_errors += bit_errors
    if bit_errors > 0:
        reconciliation.stats.remaining_frame_errors += 1
    print(f" stats={json.dumps(stats.__dict__)}")

def get_code_version():
    try:
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        return str(sha)
    except git.InvalidGitRepositoryError:
        return "unknown"

def main():
    args = parse_command_line_arguments()
    run_experiment(args.runs, args.algorithm, args.key_size, args.error_rate)

if __name__ == "__main__":
    main()
