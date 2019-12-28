import random
import time
import cqc.pythonLib as cqclib
from .bit_state import BitState
from .constants import *
from .report import Report
from .stats import Stats

# TODO: The following is a terrible hack to avoid BrokenPipe errors in Simulaqron
# when a node sends two messages in succession. Remove this once issue #246 is fixed.
NEED_SLEEP_BEFORE_SEND = False

def random_basis():
    if random.randint(0, 1) == 0:
        return BASIS_COMPUTATIONAL
    return BASIS_HADAMARD

class Node:

    def __init__(self, name, **kwargs):
        self._name = name
        # TODO: Add log_level=logging.DEBUG to the following line to debug Simulaqron issues
        self._cqc_connection = cqclib.CQCConnection(name)
        self._cqc_connection.__enter__()
        self._key_size = None
        self._window_size = None
        self._block_size = None
        self._revealed_bits_in_block = 0
        self._key = []
        self._tx_stats = Stats(False, None)
        self._rx_stats = Stats(True, None)
        self._trace = kwargs.get("trace")
        self._report = kwargs.get("report")

    def __del__(self):
        # TODO: Is this inherited?
        self._cqc_connection.__exit__(None, None, None)

    def send_msg(self, to, kind, msg):

        # TODO: The following is a terrible hack to avoid BrokenPipe errors in Simulaqron
        # when a node sends two messages in succession. Remove this once issue #246 is fixed.
        global NEED_SLEEP_BEFORE_SEND
        if NEED_SLEEP_BEFORE_SEND:
            time.sleep(1)
        NEED_SLEEP_BEFORE_SEND = True

        if self._trace:
            print(f"TX [{self._name}->{to}] ({kind}) {msg}")
        # TODO: Add close_after=False once we have fixed the issues in Simulaqron
        self._cqc_connection.sendClassical(to, msg)

    def recv_msg(self, kind):

        # TODO: The following is a terrible hack to avoid BrokenPipe errors in Simulaqron
        # when a node sends two messages in succession. Remove this once issue #246 is fixed.
        global NEED_SLEEP_BEFORE_SEND
        NEED_SLEEP_BEFORE_SEND = False

        # TODO: Add close_after=False once we have fixed the issues in Simulaqron
        msg = self._cqc_connection.recvClassical()
        if self._trace:
            print(f"RX [{self._name}] ({kind}) {msg}")
        return msg

    def send_parameters(self, peer_name):
        msg = (self._key_size.to_bytes(2, 'big') +
               self._window_size.to_bytes(2, 'big') +
               self._block_size.to_bytes(2, 'big'))
        self.send_msg(peer_name, "paramters", msg)

    def receive_parameters(self):
        msg = self.recv_msg("parameters")
        assert len(msg) == 6, "Parameters message must be 6 bytes"
        self._key_size = int.from_bytes(msg[0:2], 'big')
        self._window_size = int.from_bytes(msg[2:4], 'big')
        self._block_size = int.from_bytes(msg[4:6], 'big')
        self._tx_stats.block_size = self._block_size
        self._rx_stats.block_size = self._block_size

    def send_random_qubits_window(self, peer_name):
        window = []
        for _ in range(self._window_size):
            bit = random.randint(0, 1)
            tx_basis = random_basis()
            bit_state = BitState(bit, tx_basis, None)
            bit_state.encode_qubit(self._cqc_connection)
            window.append(bit_state)
            self._cqc_connection.sendQubit(bit_state.qubit, peer_name)
            self._tx_stats.qubit += 1
        return window

    def receive_and_measure_qubits_window(self, measure_percentage):

        # TODO: The following is a terrible hack to avoid BrokenPipe errors in Simulaqron
        # when a node sends two messages in succession. Remove this once issue #246 is fixed.
        global NEED_SLEEP_BEFORE_SEND
        NEED_SLEEP_BEFORE_SEND = False

        window = []
        for _ in range(self._window_size):
            qubit = self._cqc_connection.recvQubit()
            self._rx_stats.qubit += 1
            bit_state = BitState(None, None, qubit)
            if random.randint(1, 100) <= measure_percentage:
                bit_state.measure_basis = random_basis()
                bit_state.measure_qubit()
            window.append(bit_state)
        return window

    def propagate_qubits_window(self, window, peer_name):
        for bit_state in window:
            bit_state.tx_basis = bit_state.measure_basis
            if bit_state.qubit is None:
                bit_state.encode_qubit(self._cqc_connection)
            self._cqc_connection.sendQubit(bit_state.qubit, peer_name)
            self._tx_stats.qubit += 1
        return window

    def key_is_complete(self):
        key_len = len(self._key)
        if key_len < self._key_size:
            return False
        assert key_len == self._key_size, "Key length should never exceed requested key size"
        return True

    def decide_what_to_do_with_bit(self, bit_state):
        if bit_state.tx_basis != bit_state.measure_basis:
            bit_state.decision = DECISIONBASIS_MISMATCH
            return
        if self.key_is_complete():
            keep_as_key = False
        elif self._revealed_bits_in_block > (self._key_size + 1) // 2:
            keep_as_key = True
        else:
            keep_as_key = random.randint(0, 1) == 0
        if keep_as_key:
            bit_state.decision = DECISION_KEEP_AS_KEY
            self._key.append(bit_state.bit)
        else:
            if bit_state.bit == 0:
                bit_state.decision = DECISION_REVEAL_AS_0
            else:
                bit_state.decision = DECISION_REVEAL_AS_1
            self._revealed_bits_in_block += 1

    def decide_what_to_do_with_block(self, block):
        for bit_state in block:
            self.decide_what_to_do_with_bit(bit_state)

    @staticmethod
    def count_decision(decision, stats):
        if decision == DECISIONBASIS_MISMATCH:
            stats.decision_basis_mismatch += 1
        elif decision == DECISION_KEEP_AS_KEY:
            stats.decision_use_as_key += 1
        elif decision == DECISION_REVEAL_AS_0:
            stats.decision_reveal_as_0 += 1
        elif decision == DECISION_REVEAL_AS_1:
            stats.decision_reveal_as_1 += 1

    def send_measure_basis(self, block, peer_name):
        msg = b""
        for bit_state in block:
            msg += bit_state.measure_basis
        self.send_msg(peer_name, "basis", msg)
        self._tx_stats.basis_msg += 1

    def receive_measure_basis(self, block):
        msg = self.recv_msg("basis")
        self._rx_stats.basis_msg += 1
        assert len(msg) == self._block_size, "Chosen basis message has wrong size"
        i = 0
        for bit_state in block:
            bit_state.measure_basis = msg[i:i+1]
            if bit_state.tx_basis is not None and bit_state.measure_basis != bit_state.tx_basis:
                bit_state.base_mismatch = True
            i += 1

    def send_decisions(self, block, peer_name):
        msg = b""
        for bit_state in block:
            msg += bit_state.decision
            self.count_decision(bit_state.decision, self._tx_stats)
        self.send_msg(peer_name, "decision", msg)
        self._tx_stats.decision_msg += 1

    def receive_decisions(self, block):
        msg = self.recv_msg("decision")
        self._rx_stats.decision_msg += 1
        assert len(msg) == self._block_size, "Server decisions message has wrong size"
        i = 0
        for bit_state in block:
            bit_state.decision = msg[i:i+1]
            self.count_decision(bit_state.decision, self._rx_stats)
            if bit_state.decision == DECISION_KEEP_AS_KEY:
                if bit_state.base_mismatch:
                    # If this is Eve and Eve guessed the wrong basis, the key bit is set to -1
                    self._key.append(-1)
                else:
                    self._key.append(bit_state.bit)
            i += 1

    @staticmethod
    def compute_comparison(block):
        for bit_state in block:
            if bit_state.decision == DECISION_REVEAL_AS_0:
                if bit_state.bit == 0:
                    bit_state.comparison = COMPARISON_SAME
                else:
                    bit_state.comparison = COMPARISON_DIFFERENT
            elif bit_state.decision == DECISION_REVEAL_AS_1:
                if bit_state.bit == 1:
                    bit_state.comparison = COMPARISON_SAME
                else:
                    bit_state.comparison = COMPARISON_DIFFERENT
            else:
                bit_state.comparison = COMPARISON_NONE

    @staticmethod
    def count_comparison(comparison, stats):
        if comparison == COMPARISON_NONE:
            stats.comparison_none += 1
        elif comparison == COMPARISON_SAME:
            stats.comparison_same += 1
        elif comparison == COMPARISON_DIFFERENT:
            stats.comparison_different += 1

    def send_comparison(self, block, peer_name):
        msg = b""
        for bit_state in block:
            msg += bit_state.comparison
            self.count_comparison(bit_state.comparison, self._tx_stats)
        self._tx_stats.comparison_msg += 1
        self.send_msg(peer_name, "comparison", msg)

    def receive_comparison(self, block):
        msg = self.recv_msg("comparison")
        self._rx_stats.comparison_msg += 1
        i = 0
        for bit_state in block:
            bit_state.comparison = msg[i:i+1]
            self.count_comparison(bit_state.comparison, self._rx_stats)
            i += 1

    def key_str(self):
        string = ""
        for bit in self._key:
            if bit is None:
                string += '.'
            elif bit is -1:
                string += '?'
            else:
                string += str(bit)
        return string

    def print_report(self, elapsed_time):
        report = Report()
        report.add(f"*** {self._name} ***")
        report.add(f"Elapsed time: {elapsed_time:.1f} secs")
        report.add(f"Key size: {self._key_size}")
        report.add(f"Key: {self.key_str()}")
        report.add(f"Block size: {self._block_size}")
        self._tx_stats.add_to_report(report, elapsed_time)
        self._rx_stats.add_to_report(report, elapsed_time)
        report.print()
