import math

ALGORITHMS = {}

class Algorithm:
    """
    A Cascade algorithm.

    Attributes:
        name (str): A human-readable string that uniquely identifies the algorithm.
    """

    def __init__(self, name, cascade_iterations, block_size_function, error_free_biconf_iterations,
                 sub_block_reuse, block_parity_inference):
        self.name = name
        self.cascade_iterations = cascade_iterations
        self.block_size_function = block_size_function
        self.error_free_biconf_iterations = error_free_biconf_iterations
        self.sub_block_reuse = sub_block_reuse
        self.block_parity_inference = block_parity_inference
        ALGORITHMS[name] = self

def get_algorithm_by_name(name):
    """
    Get an algorithm object by name.

    Params:
        name (str): The name of the algorithm to be retrieved.

    Returns:
        The algorithm object corresponding to the given name, or None if no such algorithm exists.
    """
    return ALGORITHMS.get(name)

_MIN_ESTIMATED_BIT_ERROR_RATE = 0.00001

def _original_block_size_function(estimated_bit_error_rate, iteration):
    if estimated_bit_error_rate < _MIN_ESTIMATED_BIT_ERROR_RATE:
        estimated_bit_error_rate = _MIN_ESTIMATED_BIT_ERROR_RATE
    if iteration == 1:
        return math.ceil(0.73 / estimated_bit_error_rate)
    return 2 * _original_block_size_function(estimated_bit_error_rate, iteration - 1)

_ORIGINAL_ALGORITHM = Algorithm(name="original",
                                cascade_iterations=4,
                                block_size_function=_original_block_size_function,
                                error_free_biconf_iterations=None,
                                sub_block_reuse=False,
                                block_parity_inference=False)

def _biconf_block_size_function(estimated_bit_error_rate, iteration):
    if estimated_bit_error_rate < _MIN_ESTIMATED_BIT_ERROR_RATE:
        estimated_bit_error_rate = _MIN_ESTIMATED_BIT_ERROR_RATE
    if iteration == 1:
        return math.ceil(0.92 / estimated_bit_error_rate)
    return 3 * _biconf_block_size_function(estimated_bit_error_rate, iteration - 1)

_BICONF_ALGORITHM = Algorithm(name="biconf",
                              cascade_iterations=2,
                              block_size_function=_biconf_block_size_function,
                              error_free_biconf_iterations=10,
                              sub_block_reuse=False,
                              block_parity_inference=False)
