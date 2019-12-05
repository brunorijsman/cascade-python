import time
from .node import Node

class Server(Node):

    def __init__(self, name, client_name, **kwargs):
        Node.__init__(self, name, **kwargs)
        self._client_name = client_name

    def process_block(self):
        self._tx_stats.block += 1
        self._rx_stats.block += 1
        self._revealed_bits_in_block = 0
        assert self._block_size % self._window_size == 0
        block = []
        for _ in range(self._block_size // self._window_size):
            window = self.send_random_qubits_window(self._client_name)
            block += window
            self.recv_msg("ack")
        self.receive_measure_basis(block)
        self.decide_what_to_do_with_block(block)
        self.send_decisions(block, self._client_name)
        self.receive_comparison(block)

    def agree_key(self):
        start_time = time.perf_counter()
        self.receive_parameters()
        while not self.key_is_complete():
            self.process_block()
        elapsed_time = time.perf_counter() - start_time
        if self._report:
            self.print_report(elapsed_time)
        return self._key
