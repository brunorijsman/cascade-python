import argparse
import json
import git

from cascade.key import Key
from cascade.mock_classical_channel import MockClassicalChannel
from cascade.reconciliation import Reconciliation

from study.experiment import Experiment

DEFAULT_EXPERIMENTS_FILE = "experiments.json"
DEFAULT_RUNS = 10         # TODO: Make this a larger number

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description="Run Cascade experiments")
    parser.add_argument('experiments_file', metavar="experiments-file", type=str, nargs='?',
                        default=DEFAULT_EXPERIMENTS_FILE,
                        help=f"experiments file (default {DEFAULT_EXPERIMENTS_FILE})")
    parser.add_argument('-r', '--runs', type=int, default=DEFAULT_RUNS,
                        help=f"number of reconciliation runs (default {DEFAULT_RUNS})")
    args = parser.parse_args()
    return args

def parse_experiments_file(file_name):
    with open(file_name) as json_file:
        experiments = json.load(json_file)
    return experiments

def data_points_in_multiple_experiments(experiments):
    total_nr_data_points = 0
    for experiment in experiments:
        total_nr_data_points += data_points_in_one_experiment(experiment)
    return total_nr_data_points

def data_points_in_one_experiment(experiment):
    error_rates = make_list(experiment['error_rate'])
    key_sizes = make_list(experiment['key_size'])
    return len(error_rates) * len(key_sizes)

def run_experiment(experiment, total_nr_data_points):
    algorithm = experiment['algorithm']
    error_rates = make_list(experiment['error_rate'])
    key_sizes = make_list(experiment['key_size'])
    data_file_name = experiment['data_file']
    with open(data_file_name, mode="w") as data_file:
        data_point_nr = 0
        for key_size in key_sizes:
            for error_rate in error_rates:
                # TODO: percent across ALL experiments in this process
                percent = data_point_nr / total_nr_data_points * 100.0
                print(f"percent={percent:.2f} "
                      f"algorithm={algorithm} "
                      f"key_size={key_size} "
                      f"error_rate={error_rate:.4rf}")
                data_point_nr += 1
                produce_data_point(data_file, algorithm, key_size, "exact", error_rate)

def make_list(value):
    if isinstance(value, dict):
        start = value['start']
        end = value['end']
        step = value['step']
        lst = []
        current = start
        while current <= end:
            lst.append(current)
            current += step
        return lst
    return [value]

def produce_data_point(data_file, algorithm, key_size, error_method, error_rate):
    experiment = Experiment(algorithm, key_size, error_rate, get_code_version())
    run_reconciliation(data_file, experiment, algorithm, key_size, error_method, error_rate)

def run_reconciliation(data_file, experiment, algorithm, key_size, error_method, error_rate):
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
    print(to_json(reconciliation.stats), file=data_file)

def get_code_version():
    try:
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        return str(sha)
    except git.InvalidGitRepositoryError:
        return "unknown"

# TODO: need this?
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
    experiments = parse_experiments_file(args.experiments_file)
    total_nr_data_points = data_points_in_multiple_experiments(experiments)
    for experiment in experiments:
        run_experiment(experiment, total_nr_data_points)

if __name__ == "__main__":
    main()
