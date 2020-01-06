from cascade.algorithm import get_algorithm_by_name

def test_original_block_size_function():
    algorithm = get_algorithm_by_name('original')
    assert algorithm.block_size_function(0.0, 1) == 73000
    assert algorithm.block_size_function(0.1, 1) == 8
    assert algorithm.block_size_function(0.01, 1) == 73
    assert algorithm.block_size_function(0.01, 2) == 146
    assert algorithm.block_size_function(0.01, 3) == 292
    assert algorithm.block_size_function(0.001, 1) == 730
