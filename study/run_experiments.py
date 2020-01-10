import argparse
import json
import git

from cascade.key import Key
from cascade.mock_classical_channel import MockClassicalChannel
from cascade.reconciliation import Reconciliation

from study.data_point import DataPoint

DEFAULT_RUNS = 10         # TODO: Make this a larger number

TOTAL_NR_DATA_POINTS = None

CURRENT_DATA_POINT_NR = None

def parse_command_line_arguments():
    parser = argparse.ArgumentParser(description="Run Cascade experiments")
    parser.add_argument('experiments_file_name', metavar="experiments-file", type=str,
                        help="experiments definition file")
    # TODO: Move runs to definition file, and replace with sample argument
    parser.add_argument('-r', '--runs', type=int, default=DEFAULT_RUNS,
                        help=(f"number of reconciliation runs per experiment "
                              f"(default: {DEFAULT_RUNS})"))
    args = parser.parse_args()
    return args

def parse_experiments_file(file_name):
    with open(file_name) as json_file:
        experiments = json.load(json_file)
    return experiments

def experiments_to_series(experiments):
    all_series = []
    for experiment in experiments:
        if experiment['independent_variable'] == 'error_rate':
            experiment_series = experiment_to_error_rate_series(experiment)
        elif experiment['independent_variable'] == 'key_size':
            experiment_series = experiment_to_key_size_series(experiment)
        else:
            assert False
        all_series += experiment_series
    return all_series

def experiment_to_error_rate_series(experiment):
    series = []
    for algorithm in make_list(experiment['algorithm']):
        for key_size in make_list(experiment['key_size']):
            serie = dict(name=f"algorithm={algorithm};key_size={key_size};error_rate=vary",
                         algorithms=[algorithm],
                         key_sizes=[key_size],
                         error_rates=make_list(experiment['error_rate']))
            series.append(serie)
    return series

def experiment_to_key_size_series(experiment):
    series = []
    for algorithm in make_list(experiment['algorithm']):
        for error_rate in make_list(experiment['error_rate']):
            serie = dict(name=f"algorithm={algorithm};key_size=vary;error_rate={error_rate}",
                         algorithms=[algorithm],
                         key_sizes=make_list(experiment['key_size'], do_round=True),
                         error_rates=[error_rate])
            series.append(serie)
    return series

def make_list(value, do_round=False):
    if isinstance(value, (int, float, str)):
        return [value]
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        start = value['start']
        end = value['end']
        assert ('step_size' in value) != ('step_factor' in value)
        step_size = value.get('step_size', 0.0)
        step_factor = value.get('step_factor', 1.0)
        lst = []
        current = start
        while current <= end:
            if do_round:
                lst.append(round(current))
            else:
                lst.append(current)
            current += step_size
            current *= step_factor
        return lst
    assert False
    return None

def compute_total_nr_data_points(series):
    global TOTAL_NR_DATA_POINTS
    TOTAL_NR_DATA_POINTS = 0
    for serie in series:
        TOTAL_NR_DATA_POINTS += (len(serie['algorithms']) * 
                                 len(serie['key_sizes']) * 
                                 len(serie['error_rates']))

def run_series(series):
    # TODO: Run in parallel
    global CURRENT_DATA_POINT_NR
    CURRENT_DATA_POINT_NR = 0
    for serie in series:
        run_serie(serie)

def run_serie(serie):
    data_file_name = "data__" + serie['name']
    with open(data_file_name, mode="w") as data_file:
        for algorithm in serie['algorithms']:
            for key_size in serie['key_sizes']:
                for error_rate in serie['error_rates']:
                    # TODO: put number of runs in definition
                    produce_data_point(data_file, 10, algorithm, key_size, "exact", error_rate)
                    report_data_point_done(algorithm, key_size, error_rate)

def report_data_point_done(algorithm, key_size, error_rate):
    global CURRENT_DATA_POINT_NR, TOTAL_NR_DATA_POINTS
    CURRENT_DATA_POINT_NR += 1
    percent = CURRENT_DATA_POINT_NR / TOTAL_NR_DATA_POINTS * 100.0
    print(f"percent={percent:.2f} "
          f"algorithm={algorithm} "
          f"key_size={key_size} "
          f"error_rate={error_rate:.4f}")

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
        data_point.remaining_frame_error_rate.record_value(1.0)
    else:
        data_point.remaining_frame_error_rate.record_value(0.0)

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
    series = experiments_to_series(experiments)
    compute_total_nr_data_points(series)
    run_series(series)

if __name__ == "__main__":
    main()
