class Stats:
    """
    Stats of a single reconciliation.
    """

    def __init__(self):
        """
        Create a new stats block with all counters initialized to zero.
        """
        self.elapsed_process_time = None
        self.elapsed_real_time = None
        self.normal_iterations = 0
        self.biconf_iterations = 0
        self.ask_parity_messages = 0
        self.ask_parity_blocks = 0
        self.ask_parity_bits = 0
        self.reply_parity_bits = 0
        self.unrealistic_efficiency = None
        self.realistic_efficiency = None
        self.infer_parity_blocks = 0
