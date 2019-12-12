import math

class Parameters:

    def __init__(self, nr_iterations, block_size_function, biconf, sub_block_reuse,
                 block_parity_inference):
        """
        Create a new set of parameters for the Cascade algorithm.

        Args:
            nr_iterations (int): The number of Cascade iterations (also known as the number of
                Cascade passes)

            block_size_function: A function that returns the block size as a function of the
                estimated quantum bit error rate and the iteration number:

                def original_block_size_function(estimated_quantum_bit_error_rate, iteration):

                    # estimated_quantum_bit_error_rate is float >= 0.0, iteration is int >= 1

                    return block_size

            biconf (bool): Use the BICONF algorithm instead of the BINARY algorithm after the second
                Cascade iteration?

            sub_block_reuse (bool): Re-use sub-blocks from previous iterations during Cascade
                effect? If False, only top-level block from previous iterations are re-used during
                Cascade effect.

            block_parity_inference (bool): Avoid asking for block parity by inferring the block
                parity when possible.
        """

        # Validate arguments.
        assert isinstance(nr_iterations, int)
        assert nr_iterations > 1
        assert callable(block_size_function)
        assert isinstance(biconf, bool)
        assert isinstance(sub_block_reuse, bool)
        assert isinstance(block_parity_inference, bool)

        # Set parameters.
        self.nr_iterations = nr_iterations
        self.block_size_function = block_size_function
        self.biconf = biconf                                    # TODO: Not yet supported
        self.sub_block_reuse = sub_block_reuse                  # TODO: We currently always do this
        self.block_parity_inference = block_parity_inference    # TODO: Not yet supported

    def __repr__(self):
        """
        Get the unambiguous string representation of the parameters.

        Returns:
            The unambiguous string representation of the parameters.
        """
        # To make the generated Sphinx documentation look nice.
        return (
            f"Parameters(\n"
            f"  nr_iterations={self.nr_iterations},\n"
            f"  block_size_function={self.block_size_function},\n"
            f"  biconf={self.biconf},\n"
            f"  sub_block_reuse={self.sub_block_reuse},\n"
            f"  block_parity_inference={self.block_parity_inference}\n"
            f")"
        )

def original_block_size_function(estimated_quantum_bit_error_rate, iteration):
    """
    The block size according to the original Cascade algorithm:

    iteration 1: block_size = 0.73 / estimated_quantum_bit_error_rate

    iteration k: block_size = 2 * block_size for iteration k-1
    """
    if estimated_quantum_bit_error_rate < 0.001:
        estimated_quantum_bit_error_rate = 0.001
    return math.ceil((0.73 / estimated_quantum_bit_error_rate) * (2 ** (iteration - 1)))

ORIGINAL_PARAMETERS = Parameters(nr_iterations=4,
                                 block_size_function=original_block_size_function,
                                 biconf=False,
                                 sub_block_reuse=False,
                                 block_parity_inference=False)
"""The parameters for the original Cascade protocol."""
