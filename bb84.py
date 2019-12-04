import logging
import random
import sys
import time
import cqc.pythonLib as cqclib

# TODO: Add authentication and data integrety on classical channel (see http://bit.ly/bb84auth)
# TODO: Add documentation comments
# TODO: Add type annotations
# TODO: Add noise estimation
# TODO: Add information reconciliation
# TODO: Add privacy amplification
# TODO: Keep stats for measured qubits
# TODO: Report Alice and Bob key, and differences at end of run
# TODO: Generate documentation
# TODO: Automated unit test
# TODO: CI/CD pipeline
# TODO: Handle case that block size is not multiple of window size
# TODO: Get rid of report kwarg, instead make report public

_DECISION_NONE = b'.'
_DECISION_BASIS_MISMATCH = b'M'
_DECISION_KEEP_AS_KEY = b'K'
_DECISION_REVEAL_AS_0 = b'0'
_DECISION_REVEAL_AS_1 = b'1'

_COMPARISON_NONE = b'.'
_COMPARISON_SAME = b'S'
_COMPARISON_DIFFERENT = b'D'

_BASIS_COMPUTATIONAL = b'+'
_BASIS_HADAMARD = b'x'

_ACK = b'A'

# TODO: The following is a terrible hack to avoid BrokenPipe errors in Simulaqron
# when a node sends two messages in succession. Remove this once issue #246 is fixed.
NEED_SLEEP_BEFORE_SEND = False

def percent_str(count, total):
    if total == 0:
        return f"-"
    percentage = 100.0 * float(count) / float(total)
    return f"{percentage:.1f}%"

def throughput_str(count, duration, unit):
    throughput = count / duration
    return f"[{throughput:.1f} {unit}/sec]"

def random_basis():
    if random.randint(0, 1) == 0:
        return _BASIS_COMPUTATIONAL
    return _BASIS_HADAMARD

class BitState:

    def __init__(self, bit, tx_basis, qubit):
        self.bit = bit
        self.tx_basis = tx_basis
        self.measure_basis = None
        self.base_mismatch = False
        self.qubit = qubit
        self.decision = _DECISION_NONE
        self.comparison = _COMPARISON_NONE

    def encode_qubit(self, cqc_connection):
        self.qubit = cqclib.qubit(cqc_connection)
        if self.bit == 1:
            self.qubit.X()
        if self.tx_basis == _BASIS_HADAMARD:
            self.qubit.H()

    def measure_qubit(self):
        if self.measure_basis == _BASIS_HADAMARD:
            self.qubit.H()
        self.bit = self.qubit.measure()
        self.qubit = None

class Report:

    def __init__(self):
        self._text = ""

    def add(self, line):
        self._text += line + '\n'

    def print(self):
        print(self._text, file=sys.stderr)
        self._text = ""

class Stats:

    def __init__(self, is_rx, block_size):
        self._is_rx = is_rx
        self.block = 0
        self.block_size = block_size
        self.qubit = 0
        self.qubit_measured = 0
        self.basis_msg = 0
        self.decision_msg = 0
        self.decision_basis_mismatch = 0
        self.decision_use_as_key = 0
        self.decision_reveal_as_0 = 0
        self.decision_reveal_as_1 = 0
        self.comparison_msg = 0
        self.comparison_none = 0
        self.comparison_same = 0
        self.comparison_different = 0

    def add_to_report(self, report, elapsed_time):
        if self._is_rx:
            report.add("RX stats:")
        else:
            report.add("TX stats:")
        report.add(f"  Blocks: {self.block} " +
                   f"{throughput_str(self.block, elapsed_time, 'blocks')}")
        if self.qubit:
            report.add(f"  Qubits: {self.qubit} " +
                       f"{throughput_str(self.qubit, elapsed_time, 'qubits')}")
            # TODO: Measured qubits
        if self.basis_msg:
            report.add(f"  Basis messages: {self.basis_msg} " +
                       f"{throughput_str(self.basis_msg, elapsed_time, 'messages')}")
        if self.decision_msg:
            report.add(f"  Decision messages: {self.decision_msg} " +
                       f"{throughput_str(self.decision_msg, elapsed_time, 'messages')}")
            cnt = self.decision_msg * self.block_size
            report.add(f"    Basis mismatch: {self.decision_basis_mismatch} " +
                       f"({percent_str(self.decision_basis_mismatch, cnt)}) " +
                       f"{throughput_str(self.decision_basis_mismatch, elapsed_time, 'bits')}")
            report.add(f"    Use as key: {self.decision_use_as_key} " +
                       f"({percent_str(self.decision_use_as_key, cnt)}) " +
                       f"{throughput_str(self.decision_use_as_key, elapsed_time, 'bits')}")
            reveal = self.decision_reveal_as_0 + self.decision_reveal_as_1
            report.add(f"    Reveal: {reveal} " +
                       f"({percent_str(reveal, cnt)}) " +
                       f"{throughput_str(reveal, elapsed_time, 'bits')}")
            if reveal:
                report.add(f"      Reveal as 0: {self.decision_reveal_as_0} " +
                           f"({percent_str(self.decision_reveal_as_0, reveal)}) " +
                           f"{throughput_str(self.decision_reveal_as_0, elapsed_time, 'bits')}")
                report.add(f"      Reveal as 1: {self.decision_reveal_as_1} " +
                           f"({percent_str(self.decision_reveal_as_1, reveal)}) " +
                           f"{throughput_str(self.decision_reveal_as_1, elapsed_time, 'bits')}")
        if self.comparison_msg:
            report.add(f"  Comparison messages: {self.comparison_msg} " +
                       f"{throughput_str(self.comparison_msg, elapsed_time, 'messages')}")
            cnt = self.comparison_msg * self.block_size
            report.add(f"    Not compared: {self.comparison_none} " +
                       f"({percent_str(self.comparison_none, cnt)}) " +
                       f"{throughput_str(self.comparison_none, elapsed_time, 'bits')}")
            compared = self.comparison_same + self.comparison_different
            report.add(f"    Compared: {compared} " +
                       f"({percent_str(compared, cnt)}) " +
                       f"{throughput_str(compared, elapsed_time, 'bits')}")
            if compared:
                report.add(f"      Same: {self.comparison_same} " +
                           f"({percent_str(self.comparison_same, compared)}) " +
                           f"{throughput_str(self.comparison_same, elapsed_time, 'bits')}")
                report.add(f"      Different: {self.comparison_different} " +
                           f"({percent_str(self.comparison_different, compared)}) " +
                           f"{throughput_str(self.comparison_different, elapsed_time, 'bits')}")

class Base:

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
            bit_state = BitState(bit, tx_basis, None)    ###@@@
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
            bit_state.decision = _DECISION_BASIS_MISMATCH
            return
        if self.key_is_complete():
            keep_as_key = False
        elif self._revealed_bits_in_block > (self._key_size + 1) // 2:
            keep_as_key = True
        else:
            keep_as_key = random.randint(0, 1) == 0
        if keep_as_key:
            bit_state.decision = _DECISION_KEEP_AS_KEY
            self._key.append(bit_state.bit)
        else:
            if bit_state.bit == 0:
                bit_state.decision = _DECISION_REVEAL_AS_0
            else:
                bit_state.decision = _DECISION_REVEAL_AS_1
            self._revealed_bits_in_block += 1

    def decide_what_to_do_with_block(self, block):
        for bit_state in block:
            self.decide_what_to_do_with_bit(bit_state)

    @staticmethod
    def count_decision(decision, stats):
        if decision == _DECISION_BASIS_MISMATCH:
            stats.decision_basis_mismatch += 1
        elif decision == _DECISION_KEEP_AS_KEY:
            stats.decision_use_as_key += 1
        elif decision == _DECISION_REVEAL_AS_0:
            stats.decision_reveal_as_0 += 1
        elif decision == _DECISION_REVEAL_AS_1:
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
            if bit_state.decision == _DECISION_KEEP_AS_KEY:
                if bit_state.base_mismatch:
                    # If this is Eve and Eve guessed the wrong basis, the key bit is set to -1
                    self._key.append(-1)
                else:
                    self._key.append(bit_state.bit)
            i += 1

    @staticmethod
    def compute_comparison(block):
        for bit_state in block:
            if bit_state.decision == _DECISION_REVEAL_AS_0:
                if bit_state.bit == 0:
                    bit_state.comparison = _COMPARISON_SAME
                else:
                    bit_state.comparison = _COMPARISON_DIFFERENT
            elif bit_state.decision == _DECISION_REVEAL_AS_1:
                if bit_state.bit == 1:
                    bit_state.comparison = _COMPARISON_SAME
                else:
                    bit_state.comparison = _COMPARISON_DIFFERENT
            else:
                bit_state.comparison = _COMPARISON_NONE

    @staticmethod
    def count_comparison(comparison, stats):
        if comparison == _COMPARISON_NONE:
            stats.comparison_none += 1
        elif comparison == _COMPARISON_SAME:
            stats.comparison_same += 1
        elif comparison == _COMPARISON_DIFFERENT:
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
        report.add(f"Elpased time: {elapsed_time:.1f} secs")
        report.add(f"Key size: {self._key_size}")
        report.add(f"Key: {self.key_str()}")
        report.add(f"Block size: {self._block_size}")
        self._tx_stats.add_to_report(report, elapsed_time)
        self._rx_stats.add_to_report(report, elapsed_time)
        report.print()

class Server(Base):

    def __init__(self, name, client_name, **kwargs):
        Base.__init__(self, name, **kwargs)
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

class Client(Base):

    def __init__(self, name, server_name, key_size, window_size, block_size, **kwargs):
        Base.__init__(self, name, **kwargs)
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
            self.send_msg(self._server_name, "ack", _ACK)
        self.send_measure_basis(block, self._server_name)
        self.receive_decisions(block)
        self.compute_comparison(block)
        self.send_comparison(block, self._server_name)

    def agree_key(self):
        start_time = time.perf_counter()
        self.send_parameters(self._server_name)
        while not self.key_is_complete():
            self.process_block()
        elapsed_time = time.perf_counter() - start_time
        if self._report:
            self.print_report(elapsed_time)
        return self._key

class Middle(Base):

    def __init__(self, name, server_name, client_name, observe_percentage, **kwargs):
        Base.__init__(self, name, **kwargs)
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
            self.send_msg(self._server_name, "ack", _ACK)
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
