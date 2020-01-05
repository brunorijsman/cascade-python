import argparse
import json
import git

from cascade.key import Key
from cascade.mock_classical_channel import MockClassicalChannel
from cascade.algorithm import ORIGINAL_ALGORITHM
from cascade.reconciliation import Reconciliation

from study.experiment import Experiment

DEFAULT_ALGORITHM = "original"
DEFAULT_ERROR_METHOD = Key.ERROR_METHOD_EXACT
DEFAULT_ERROR_RATE = 0.01
DEFAULT_KEY_SIZE = 100   # TODO
DEFAULT_RUNS = 10         # TODO: Make this a larger number

# TODO: Put this in algorithm.py
ALGORITHMS = {
    "original": ORIGINAL_ALGORITHM,
    "biconf": None,   # TODO
    "yanetal": None   # TODO
}

def error_method_type(arg):
    if not isinstance(arg, str):
        raise argparse.ArgumentTypeError("must be a string")
    if arg not in Key.ERROR_METHODS:
        raise argparse.ArgumentTypeError(f"valid values: {', '.join(Key.ERROR_METHODS)}")
    return arg

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
    parser.add_argument('-m', '--error-method', type=error_method_type,
                        default=DEFAULT_ERROR_METHOD,
                        help=f"quantum bit error rate (default {DEFAULT_ERROR_METHOD})")
    parser.add_argument('-e', '--error-rate', type=error_rate_type, default=DEFAULT_ERROR_RATE,
                        help=f"quantum bit error rate (default {DEFAULT_ERROR_RATE})")
    parser.add_argument('-k', '--key-size', type=int, default=10000,
                        help=f"key size (default {DEFAULT_KEY_SIZE})")
    parser.add_argument('-r', '--runs', type=int, default=DEFAULT_RUNS,
                        help=f"number of reconciliation runs (default {DEFAULT_RUNS})")
    args = parser.parse_args()
    return args

def run_experiment(runs, algorithm_name, key_size, error_method, error_rate):
    experiment = Experiment(algorithm_name, key_size, error_rate, get_code_version())
    algorithm = ALGORITHMS[algorithm_name]
    for _ in range(runs):
        stats = run_reconciliation(experiment, algorithm, key_size, error_method, error_rate)
    print(to_json(experiment))

def run_reconciliation(experiment, algorithm, key_size, error_method, error_rate):
    # Key.set_random_seed(seed)
    # Shuffle.set_random_seed(seed+1)
    correct_key = Key.create_random_key(key_size)
    noisy_key = correct_key.copy(error_rate, error_method)
    actual_bit_errors = correct_key.difference(noisy_key)
    experiment.actual_bit_errors.record_value(actual_bit_errors)
    actual_bit_error_rate = actual_bit_errors / key_size
    experiment.actual_bit_error_rate.record_value(actual_bit_error_rate)
    mock_classical_channel = MockClassicalChannel(correct_key)
    reconciliation = Reconciliation(algorithm, mock_classical_channel, noisy_key, error_rate)
    reconciliated_key = reconciliation.reconcile()
    experiment.record_reconciliation_stats(reconciliation.stats)
    remaining_bit_errors = correct_key.difference(reconciliated_key)
    experiment.remaining_bit_errors.record_value(remaining_bit_errors)
    remaining_bit_error_rate = remaining_bit_errors / key_size
    experiment.remaining_bit_error_rate.record_value(remaining_bit_error_rate)
    if remaining_bit_errors > 0:
        experiment.remaining_frame_errors.record_value(1.0)
    else:
        experiment.remaining_frame_errors.record_value(0.0)

def get_code_version():
    try:
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        return str(sha)
    except git.InvalidGitRepositoryError:
        return "unknown"

def to_json_encodeable_object(obj):
    members = dir(obj)
    if 'to_json_encodeable_object' in members:
        return obj.to_json_encodeable_object()
    dictionary = {}
    for member in members:
        if member[0] != '_':
            value = getattr(obj, member)
            if not callable(value):
                dictionary[member] = value
    return dictionary

def to_json(obj):
    return json.dumps(obj, default=to_json_encodeable_object)

def main():
    args = parse_command_line_arguments()
    run_experiment(args.runs, args.algorithm, args.key_size, args.error_method, args.error_rate)

if __name__ == "__main__":
    main()
