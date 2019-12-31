class Stats:
    """
    Statistics about one or more Cascade protocol invocations.
    """

    def __init__(self):
        """
        Create a new statistics context with all counters initialized to zero.
        """
        self.code_version = None
        self.elapsed_process_time = None
        self.elapsed_real_time = None
        self.ask_parity_messages = 0
        self.ask_parity_blocks = 0
        self.infer_parity_blocks = 0
        self.remaining_bit_errors = 0
        self.remaining_frame_errors = 0
