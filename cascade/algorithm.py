import math

ALGORITHMS = {}

class Algorithm:
    """
    A Cascade algorithm.
    """

    def __init__(self, name, cascade_iterations, block_size_function, biconf_iterations,
                 biconf_error_free_streak, biconf_correct_complement, biconf_cascade,
                 sub_block_reuse, block_parity_inference):
        """
        Create a new Cascade algorithm.

        Params:
            name (str): A human-readable name that uniquely identifies the Cascade algorithm.
            cascade_iterations (int): The number of normal cascade iterations.
            block_size_function (function): A function that computes the block size given the
                Cascade iteration number.
            biconf_iterations (int): The number of BICONF iterations to be run after the normal
                Cascade iterations are completed. 0 means don't run BICONF.
            biconf_error_free_streak (bool): If False, run a fixed number of BICONF iterations as
                indicated by biconf_iterations. If True, keep running BICONF until we see a streak
                of biconf_iterations error-free iterations.
            biconf_correct_complement (bool): If False, run BINARY only on the selected subset of
                bits. If True, run BINARY both on the selected subset of bits as well as the
                complementary set of bits.
            biconf_cascade (bool): Correct cascading errors during BICONF iterations?
            sub_block_reuse (bool): If False, consider only top-level blocks for cascading errors.
                If True, consider blocks of all sizes for cascading errors.
            block_parity_inference (bool): TODO
        """
        self.name = name
        self.cascade_iterations = cascade_iterations
        self.block_size_function = block_size_function
        self.biconf_iterations = biconf_iterations
        self.biconf_error_free_streak = biconf_error_free_streak
        self.biconf_correct_complement = biconf_correct_complement
        self.biconf_cascade = biconf_cascade
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
                                biconf_iterations=0,
                                biconf_error_free_streak=False,
                                biconf_correct_complement=False,
                                biconf_cascade=False,
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
                              biconf_iterations=10,
                              biconf_error_free_streak=True,
                              biconf_correct_complement=False,
                              biconf_cascade=False,
                              sub_block_reuse=False,
                              block_parity_inference=False)
