from cascade.algorithm import get_algorithm_by_name

def test_original_algorithm():
    algorithm = get_algorithm_by_name('original')
    assert algorithm.name == "original"
    assert algorithm.cascade_iterations == 4
    assert algorithm.block_size_function(0.0, 10000, 1) == 73000
    assert algorithm.block_size_function(0.1, 10000, 1) == 8
    assert algorithm.block_size_function(0.01, 10000, 1) == 73
    assert algorithm.block_size_function(0.01, 10000, 2) == 146
    assert algorithm.block_size_function(0.01, 10000, 3) == 292
    assert algorithm.block_size_function(0.001, 10000, 1) == 730
    assert algorithm.biconf_iterations == 0
    assert not algorithm.biconf_error_free_streak
    assert not algorithm.biconf_correct_complement
    assert not algorithm.biconf_cascade
    assert not algorithm.sub_block_reuse
    assert not algorithm.block_parity_inference

def test_biconf_algorithm():
    algorithm = get_algorithm_by_name('biconf')
    assert algorithm.name == "biconf"
    assert algorithm.cascade_iterations == 2
    assert algorithm.block_size_function(0.0, 10000, 1) == 92000
    assert algorithm.block_size_function(0.1, 10000, 1) == 10
    assert algorithm.block_size_function(0.01, 10000, 1) == 92
    assert algorithm.block_size_function(0.01, 10000, 2) == 276
    assert algorithm.block_size_function(0.01, 10000, 3) == 828
    assert algorithm.block_size_function(0.001, 10000, 1) == 920
    assert algorithm.biconf_iterations == 10
    assert algorithm.biconf_error_free_streak
    assert not algorithm.biconf_correct_complement
    assert not algorithm.biconf_cascade
    assert not algorithm.sub_block_reuse
    assert not algorithm.block_parity_inference

def test_yanetal_algorithm():
    algorithm = get_algorithm_by_name('yanetal')
    assert algorithm.name == "yanetal"
    assert algorithm.cascade_iterations == 10
    assert algorithm.block_size_function(0.0, 10000, 1) == 80000
    assert algorithm.block_size_function(0.1, 10000, 1) == 8
    assert algorithm.block_size_function(0.01, 10000, 1) == 80
    assert algorithm.block_size_function(0.01, 10000, 2) == 400
    assert algorithm.block_size_function(0.01, 10000, 3) == 5000
    assert algorithm.block_size_function(0.001, 10000, 1) == 800
    assert algorithm.biconf_iterations == 0
    assert not algorithm.biconf_error_free_streak
    assert not algorithm.biconf_correct_complement
    assert not algorithm.biconf_cascade
    assert not algorithm.sub_block_reuse
    assert not algorithm.block_parity_inference

def test_option3_algorithm():
    algorithm = get_algorithm_by_name('option3')
    assert algorithm.name == "option3"
    assert algorithm.cascade_iterations == 16
    assert algorithm.block_size_function(0.0, 10000, 1) == 100000
    assert algorithm.block_size_function(0.1, 10000, 1) == 10
    assert algorithm.block_size_function(0.01, 10000, 1) == 100
    assert algorithm.block_size_function(0.01, 10000, 2) == 200
    assert algorithm.block_size_function(0.01, 10000, 3) == 5000
    assert algorithm.block_size_function(0.001, 10000, 1) == 1000
    assert algorithm.biconf_iterations == 0
    assert not algorithm.biconf_error_free_streak
    assert not algorithm.biconf_correct_complement
    assert not algorithm.biconf_cascade
    assert not algorithm.sub_block_reuse
    assert not algorithm.block_parity_inference

def test_option4_algorithm():
    algorithm = get_algorithm_by_name('option4')
    assert algorithm.name == "option4"
    assert algorithm.cascade_iterations == 16
    assert algorithm.block_size_function(0.0, 10000, 1) == 100000
    assert algorithm.block_size_function(0.1, 10000, 1) == 10
    assert algorithm.block_size_function(0.01, 10000, 1) == 100
    assert algorithm.block_size_function(0.01, 10000, 2) == 200
    assert algorithm.block_size_function(0.01, 10000, 3) == 5000
    assert algorithm.block_size_function(0.001, 10000, 1) == 1000
    assert algorithm.biconf_iterations == 0
    assert not algorithm.biconf_error_free_streak
    assert not algorithm.biconf_correct_complement
    assert not algorithm.biconf_cascade
    assert algorithm.sub_block_reuse
    assert not algorithm.block_parity_inference

def test_option7_algorithm():
    algorithm = get_algorithm_by_name('option7')
    assert algorithm.name == "option7"
    assert algorithm.cascade_iterations == 14
    assert algorithm.block_size_function(0.0, 10000, 1) == 131072
    assert algorithm.block_size_function(0.1, 10000, 1) == 16
    assert algorithm.block_size_function(0.01, 10000, 1) == 128
    assert algorithm.block_size_function(0.01, 10000, 2) == 512
    assert algorithm.block_size_function(0.01, 10000, 3) == 5000
    assert algorithm.block_size_function(0.001, 10000, 1) == 1024
    assert algorithm.biconf_iterations == 0
    assert not algorithm.biconf_error_free_streak
    assert not algorithm.biconf_correct_complement
    assert not algorithm.biconf_cascade
    assert algorithm.sub_block_reuse
    assert not algorithm.block_parity_inference

def test_option8_algorithm():
    algorithm = get_algorithm_by_name('option8')
    assert algorithm.name == "option8"
    assert algorithm.cascade_iterations == 14
    assert algorithm.block_size_function(0.0, 10000, 1) == 131072
    assert algorithm.block_size_function(0.1, 10000, 1) == 8
    assert algorithm.block_size_function(0.01, 10000, 1) == 128
    assert algorithm.block_size_function(0.01, 10000, 2) == 1024
    assert algorithm.block_size_function(0.01, 10000, 3) == 4096
    assert algorithm.block_size_function(0.01, 10000, 4) == 5000
    assert algorithm.block_size_function(0.001, 10000, 1) == 1024
    assert algorithm.biconf_iterations == 0
    assert not algorithm.biconf_error_free_streak
    assert not algorithm.biconf_correct_complement
    assert not algorithm.biconf_cascade
    assert algorithm.sub_block_reuse
    assert not algorithm.block_parity_inference
