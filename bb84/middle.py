import time
from .node import Node
from .constants import *

class Middle(Node):

    def __init__(self, name, server_name, client_name, observe_percentage, **kwargs):
        Node.__init__(self, name, **kwargs)
        self._server_name = server_name
        self._client_name = client_name
        self._observe_percentage = observe_percentage

    def process_block(self):
        self._tx_stats.block += 1
        self._rx_stats.block += 1
        self._revealed_bits_in_block = 0
        assert self._block_size % self._window_size == 0
        block = []
        for _ in range(self._block_size // self._window_size):
            window = self.receive_and_measure_qubits_window(self._observe_percentage)
            self.send_msg(self._server_name, "ack", ACK)
            self.propagate_qubits_window(window, self._client_name)
            self.recv_msg("ack")
            block += window
        self.receive_measure_basis(block)
        self.send_measure_basis(block, self._server_name)
        self.receive_decisions(block)
        self.send_decisions(block, self._client_name)
        self.receive_comparison(block)
        self.send_comparison(block, self._server_name)

    def pass_through(self):
        start_time = time.perf_counter()
        self.receive_parameters()
        self.send_parameters(self._server_name)
        while not self.key_is_complete():
            self.process_block()
        elapsed_time = time.perf_counter() - start_time
        if self._report:
            self.print_report(elapsed_time)
