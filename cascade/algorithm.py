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
            estimated error rate, the key size, and the Cascade iteration number.
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

# Name in Demystifying paper: Cascade orig.
# Name in Andre Reis Thesis : original

def _original_block_size_function(estimated_bit_error_rate, key_size, iteration):
    if estimated_bit_error_rate < _MIN_ESTIMATED_BIT_ERROR_RATE:
        estimated_bit_error_rate = _MIN_ESTIMATED_BIT_ERROR_RATE
    if iteration == 1:
        return math.ceil(0.73 / estimated_bit_error_rate)
    return 2 * _original_block_size_function(estimated_bit_error_rate, key_size, iteration - 1)

_ORIGINAL_ALGORITHM = Algorithm(name="original",
                                cascade_iterations=4,
                                block_size_function=_original_block_size_function,
                                biconf_iterations=0,
                                biconf_error_free_streak=False,
                                biconf_correct_complement=False,
                                biconf_cascade=False,
                                sub_block_reuse=False,
                                block_parity_inference=False)

# Name in Demystifying paper: Cascade mod. (1)
# Name in Andre Reis Thesis : biconf

def _biconf_block_size_function(estimated_bit_error_rate, key_size, iteration):
    if estimated_bit_error_rate < _MIN_ESTIMATED_BIT_ERROR_RATE:
        estimated_bit_error_rate = _MIN_ESTIMATED_BIT_ERROR_RATE
    if iteration == 1:
        return math.ceil(0.92 / estimated_bit_error_rate)
    return 3 * _biconf_block_size_function(estimated_bit_error_rate, key_size, iteration - 1)

_BICONF_ALGORITHM = Algorithm(name="biconf",
                              cascade_iterations=2,
                              block_size_function=_biconf_block_size_function,
                              biconf_iterations=10,
                              biconf_error_free_streak=True,
                              biconf_correct_complement=False,
                              biconf_cascade=False,
                              sub_block_reuse=False,
                              block_parity_inference=False)

# Name in Demystifying paper: Cascade opt. (2)
# Name in Andre Reis Thesis : yanetal (Yan et al.)

def _yanetal_block_size_function(estimated_bit_error_rate, key_size, iteration):
    if estimated_bit_error_rate < _MIN_ESTIMATED_BIT_ERROR_RATE:
        estimated_bit_error_rate = _MIN_ESTIMATED_BIT_ERROR_RATE
    if iteration == 1:
        return math.ceil(0.80 / estimated_bit_error_rate)
    if iteration == 2:
        return 5 * _yanetal_block_size_function(estimated_bit_error_rate, key_size, iteration - 1)
    return key_size // 2

_YANETAL_ALGORITHM = Algorithm(name="yanetal",
                               cascade_iterations=10,
                               block_size_function=_yanetal_block_size_function,
                               biconf_iterations=0,
                               biconf_error_free_streak=False,
                               biconf_correct_complement=False,
                               biconf_cascade=False,
                               sub_block_reuse=False,
                               block_parity_inference=False)

# Name in Demystifying paper: Cascade opt. (3)
# Name in Andre Reis Thesis : -

def _option3456_block_size_function(estimated_bit_error_rate, key_size, iteration):
    if estimated_bit_error_rate < _MIN_ESTIMATED_BIT_ERROR_RATE:
        estimated_bit_error_rate = _MIN_ESTIMATED_BIT_ERROR_RATE
    if iteration == 1:
        return math.ceil(1.00 / estimated_bit_error_rate)
    if iteration == 2:
        return 2 * _option3456_block_size_function(estimated_bit_error_rate, key_size,
                                                   iteration - 1)
    return key_size // 2

_OPTION3_ALGORITHM = Algorithm(name="option3",
                               cascade_iterations=16,
                               block_size_function=_option3456_block_size_function,
                               biconf_iterations=0,
                               biconf_error_free_streak=False,
                               biconf_correct_complement=False,
                               biconf_cascade=False,
                               sub_block_reuse=False,
                               block_parity_inference=False)

# Name in Demystifying paper: Cascade opt. (4)
# Name in Andre Reis Thesis : -

_OPTION4_ALGORITHM = Algorithm(name="option4",
                               cascade_iterations=16,
                               block_size_function=_option3456_block_size_function,
                               biconf_iterations=0,
                               biconf_error_free_streak=False,
                               biconf_correct_complement=False,
                               biconf_cascade=False,
                               sub_block_reuse=True,
                               block_parity_inference=False)

# Note: Cascade opt. (5) from the Demystifying paper is not supported yet:
# TODO: need to add support for deterministic shuffling

# Note: Cascade opt. (6) from the Demystifying paper is not supported yet:
# TODO: need to add support for singleton block removal

# Name in Demystifying paper: Cascade opt. (7)
# Name in Andre Reis Thesis : option-7

def _option7_block_size_function(estimated_bit_error_rate, key_size, iteration):
    if estimated_bit_error_rate < _MIN_ESTIMATED_BIT_ERROR_RATE:
        estimated_bit_error_rate = _MIN_ESTIMATED_BIT_ERROR_RATE
    if iteration == 1:
        return 2 ** math.ceil(math.log2(1.00 / estimated_bit_error_rate))
    if iteration == 2:
        return 4 * _option7_block_size_function(estimated_bit_error_rate, key_size, iteration - 1)
    return key_size // 2

_OPTION7_ALGORITHM = Algorithm(name="option7",
                               cascade_iterations=14,
                               block_size_function=_option7_block_size_function,
                               biconf_iterations=0,
                               biconf_error_free_streak=False,
                               biconf_correct_complement=False,
                               biconf_cascade=False,
                               sub_block_reuse=True,
                               block_parity_inference=False)

# Name in Demystifying paper: Cascade opt. (8)
# Name in Andre Reis Thesis : option-8

def _option8_block_size_function(estimated_bit_error_rate, key_size, iteration):
    if estimated_bit_error_rate < _MIN_ESTIMATED_BIT_ERROR_RATE:
        estimated_bit_error_rate = _MIN_ESTIMATED_BIT_ERROR_RATE
    alpha = math.log2(1.00 / estimated_bit_error_rate) - 0.5
    if iteration == 1:
        return 2 ** math.ceil(alpha)
    if iteration == 2:
        return 2 ** math.ceil((alpha + 12.0) / 2.0)
    if iteration == 3:
        return 4096
    return key_size // 2

_OPTION8_ALGORITHM = Algorithm(name="option8",
                               cascade_iterations=14,
                               block_size_function=_option8_block_size_function,
                               biconf_iterations=0,
                               biconf_error_free_streak=False,
                               biconf_correct_complement=False,
                               biconf_cascade=False,
                               sub_block_reuse=True,
                               block_parity_inference=False)
