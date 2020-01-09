import sys

import argparse
import json
import git

from cascade.key import Key
from cascade.mock_classical_channel import MockClassicalChannel
from cascade.reconciliation import Reconciliation

from study.data_point import DataPoint

DEFAULT_RUNS = 10         # TODO: Make this a larger number

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description="Run Cascade experiments")
    parser.add_argument('experiments_file_name', metavar="experiments-file", type=str,
                        help="experiments definition file")
    # TODO: Move runs to definition file, and replace with sample argument
    parser.add_argument('-r', '--runs', type=int, default=DEFAULT_RUNS,
                        help=(f"number of reconciliation runs per experiment "
                              f"(default: {DEFAULT_RUNS})"))
    parser.add_argument('-e', '--experiment-name', type=str,
                        help=f"name of experiment to run (default: run all experiments)")
    args = parser.parse_args()
    return args

def parse_experiments_file(file_name):
    with open(file_name) as json_file:
        experiments = json.load(json_file)
    return experiments

def select_experiment(experiments, experiment_name):
    for experiment in experiments:
        if experiment['experiment_name'] == experiment_name:
            return [experiment]
    sys.exit(f"Experiment name {experiment_name} not found")

def data_points_in_multiple_experiments(experiments):
    total_nr_data_points = 0
    for experiment in experiments:
        total_nr_data_points += data_points_in_one_experiment(experiment)
    return total_nr_data_points

def data_points_in_one_experiment(experiment):
    error_rates = make_list(experiment['error_rate'])
    key_sizes = make_list(experiment['key_size'])
    return len(error_rates) * len(key_sizes)

def run_multiple_experiments(experiments, runs):
    total_nr_data_points = data_points_in_multiple_experiments(experiments)
    data_point_nr = 0
    for experiment in experiments:
        data_point_nr = run_experiment(experiment, runs, data_point_nr, total_nr_data_points)

def run_experiment(experiment, runs, start_data_point_nr, total_nr_data_points):
    algorithm = experiment['algorithm']
    error_rates = make_list(experiment['error_rate'])
    key_sizes = [round(v) for v in make_list(experiment['key_size'])]
    experiment_name = experiment['experiment_name']
    data_file_name = "data__" + experiment_name
    data_point_nr = start_data_point_nr
    with open(data_file_name, mode="w") as data_file:
        for key_size in key_sizes:
            for error_rate in error_rates:
                percent = data_point_nr / total_nr_data_points * 100.0
                print(f"percent={percent:.2f} "
                      f"algorithm={algorithm} "
                      f"key_size={key_size} "
                      f"error_rate={error_rate:.4f}")
                data_point_nr += 1
                produce_data_point(data_file, runs, algorithm, key_size, "exact", error_rate)
    return data_point_nr

def make_list(value):
    if isinstance(value, dict):
        start = value['start']
        end = value['end']
        assert ('step_size' in value) != ('step_factor' in value)   # logical xor
        step_size = value.get('step_size', 0.0)
        step_factor = value.get('step_factor', 1.0)
        lst = []
        current = start
        while current <= end:
            lst.append(current)
            current += step_size
            current *= step_factor
        return lst
    return value

def produce_data_point(data_file, runs, algorithm, key_size, error_method, error_rate):
    data_point = DataPoint(algorithm, key_size, error_rate, get_code_version())
    for _ in range(runs):
        run_reconciliation(data_point, algorithm, key_size, error_method, error_rate)
    print(to_json(data_point), file=data_file)

def run_reconciliation(data_point, algorithm, key_size, error_method, error_rate):
    # Key.set_random_seed(seed)
    # Shuffle.set_random_seed(seed+1)
    correct_key = Key.create_random_key(key_size)
    noisy_key = correct_key.copy(error_rate, error_method)
    actual_bit_errors = correct_key.difference(noisy_key)
    data_point.actual_bit_errors.record_value(actual_bit_errors)
    actual_bit_error_rate = actual_bit_errors / key_size
    data_point.actual_bit_error_rate.record_value(actual_bit_error_rate)
    mock_classical_channel = MockClassicalChannel(correct_key)
    reconciliation = Reconciliation(algorithm, mock_classical_channel, noisy_key, error_rate)
    reconciliated_key = reconciliation.reconcile()
    data_point.record_reconciliation_stats(reconciliation.stats)
    remaining_bit_errors = correct_key.difference(reconciliated_key)
    data_point.remaining_bit_errors.record_value(remaining_bit_errors)
    remaining_bit_error_rate = remaining_bit_errors / key_size
    data_point.remaining_bit_error_rate.record_value(remaining_bit_error_rate)
    if remaining_bit_errors > 0:
        data_point.remaining_frame_errors.record_value(1.0)
    else:
        data_point.remaining_frame_errors.record_value(0.0)

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
    experiments = parse_experiments_file(args.experiments_file_name)
    if args.experiment_name is not None:
        experiments = select_experiment(experiments, args.experiment_name)
    runs = args.runs
    run_multiple_experiments(experiments, runs)

if __name__ == "__main__":
    main()
