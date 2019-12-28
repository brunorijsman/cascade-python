class Stats:
    """
    Statistics about one or more Cascade protocol invocations.
    """

    def __init__(self):
        """
        Create a new statistics context with all counters initialized to zero.
        """
        self.start_reconciliation_messages = 0
        self.end_reconciliation_messages = 0
        self.ask_parities_messages = 0
        self.ask_parity_ranges = 0
        self.bit_errors = 0
        self.frame_errors = 0
