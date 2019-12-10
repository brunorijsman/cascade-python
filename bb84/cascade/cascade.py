from bb84.cascade.block import Block

def binary(block, ask_correct_parity_function):
    """
    Try to locate a single bit error in a block by recursively dividing the block into sub-blocks
    and comparing the parity of those sub-blocks with the parity of the corresponding sub-block
    in a known good block.

    Params:

        block: The block in which we will attempt to correct one bit error.

        get_correct_parity_function: A function which takes one Block as a parameter and returns
        the correct parity for the block. In other words, we assume that the block contains some
        errors due to noise and/or due to an eavesdropper, and we want the know the parity of the
        block without the errors. In real life this involves asking the party who sent us the block;
        in simulation we can get it more easily because we ourselves introduced the errors on
        purpose.
    """

    # Validate parameters.
    assert isinstance(block, Block)

    # TODO: Validate has odd errors

    ###@@@ TODO: Continue from here

    _correct_parity = ask_correct_parity_function(block)
