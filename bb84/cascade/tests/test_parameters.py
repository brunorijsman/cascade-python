import pytest
from bb84.cascade.parameters import *

def dummy_block_size_function(_estimated_quantum_bit_error_rate, _iteration):
    return 100

def test_create_parameters():
    # Validate nr_iterations argument.
    with pytest.raises(AssertionError):
        Parameters(nr_iterations="not-an-int",
                   block_size_function=dummy_block_size_function,
                   biconf=False,
                   sub_block_reuse=False,
                   block_parity_inference=False)
    with pytest.raises(AssertionError):
        Parameters(nr_iterations=0,
                   block_size_function=dummy_block_size_function,
                   biconf=False,
                   sub_block_reuse=False,
                   block_parity_inference=False)
    # Validate block_size_function argument.
    with pytest.raises(AssertionError):
        Parameters(nr_iterations=4,
                   block_size_function="not-a-function",
                   biconf=False,
                   sub_block_reuse=False,
                   block_parity_inference=False)
    # Validate biconf argument.
    with pytest.raises(AssertionError):
        Parameters(nr_iterations=4,
                   block_size_function=dummy_block_size_function,
                   biconf="not-a-bool",
                   sub_block_reuse=False,
                   block_parity_inference=False)
    # Validate sub_block_reuse argument.
    with pytest.raises(AssertionError):
        Parameters(nr_iterations=4,
                   block_size_function=dummy_block_size_function,
                   biconf=False,
                   sub_block_reuse="not-a-bool",
                   block_parity_inference=False)
    # Validate block_parity_inference argument.
    with pytest.raises(AssertionError):
        Parameters(nr_iterations=4,
                   block_size_function=dummy_block_size_function,
                   biconf=False,
                   sub_block_reuse=False,
                   block_parity_inference="not-a-bool")
    # Create parameters.
    Parameters(nr_iterations=4,
               block_size_function=dummy_block_size_function,
               biconf=False,
               sub_block_reuse=False,
               block_parity_inference=False)

def test_repr():
    parameters = Parameters(nr_iterations=4,
                            block_size_function=dummy_block_size_function,
                            biconf=False,
                            sub_block_reuse=False,
                            block_parity_inference=False)
    string = (f"Parameters(\n"
              f"  nr_iterations=4,\n"
              f"  block_size_function={dummy_block_size_function},\n"
              f"  biconf=False,\n"
              f"  sub_block_reuse=False,\n"
              f"  block_parity_inference=False\n"
              f")")
    assert parameters.__str__() == string

def test_original_block_size_function():
    assert original_block_size_function(0.1, 1) == 8
    assert original_block_size_function(0.01, 1) == 73
    assert original_block_size_function(0.001, 1) == 730
    assert original_block_size_function(0.0, 1) == 730
    assert original_block_size_function(0.01, 2) == 146
    assert original_block_size_function(0.01, 3) == 292
