import time
from .node import Node
from .constants import *

class Client(Node):

    def __init__(self, name, server_name, key_size, window_size, block_size, **kwargs):
        Node.__init__(self, name, **kwargs)
        self._server_name = server_name
        self._key_size = key_size
        self._window_size = window_size
        self._block_size = block_size
        self._tx_stats.block_size = self._block_size
        self._rx_stats.block_size = self._block_size

    def process_block(self):
        self._tx_stats.block += 1
        self._rx_stats.block += 1
        assert self._block_size % self._window_size == 0
        block = []
        for _ in range(self._block_size // self._window_size):
            window = self.receive_and_measure_qubits_window(100)
            block += window
            self.send_msg(self._server_name, "ack", ACK)
        self.send_measure_basis(block, self._server_name)
        self.receive_decisions(block)
        self.compute_comparison(block)
        self.send_comparison(block, self._server_name)

    def agree_key(self):
        start_time = time.perf_counter()
        self.send_algorithm(self._server_name)
        while not self.key_is_complete():
            self.process_block()
        elapsed_time = time.perf_counter() - start_time
        if self._report:
            self.print_report(elapsed_time)
        return self._key
