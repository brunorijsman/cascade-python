class Stats:
    """
    Statistics about one or more Cascade protocol invocations.
    """

    def __init__(self):
        """
        Create a new statistics context with all counters initialized to zero.
        """
        self.channel_uses = 0
