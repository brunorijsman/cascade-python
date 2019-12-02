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
# TODO: Stop all processes and simulaqron at script exit
# TODO: Fix eve observing script
# TODO: Add observe_qubit_percentage to Middle class
# TODO: Control message tracing with environment variable
# TODO: Have class for decision
# TODO: Eve to report which key bits she gleaned ?=wrongbasis 01=gleaned .=did not measure
# TODO: Keep stats for measured qubits
# TODO: If qubit is measured, do so immediately
# TODO: Report Alice and Bob key, and differences at end of run

def percent_str(count, total):
    if total == 0:
        return f"-"
    percentage = 100.0 * float(count) / float(total)
    return f"{percentage:.1f}%"

def throughput_str(count, duration, unit):
    throughput = count / duration
    return f"[{throughput:.1f} {unit}/sec]"

def key_str(key):
    # TODO: ? if Eve is not certain of key bit because of wrong basis
    string = ""
    for bit in key:
        if bit is None:
            string += '.'
        else:
            string += str(bit)
    return string

class Basis:

    _COMPUTATIONAL = 0
    _HADAMARD = 1

    def __init__(self, basis):
        assert basis in [self._COMPUTATIONAL, self._HADAMARD], \
               "Basis must be COMPUTATIONAL or HADAMARD"
        self._basis = basis

    def __eq__(self, other):
        return self._basis == other._basis

    def __repr__(self):
        return self.to_str()

    @classmethod
    def random(cls):
        basis = random.randint(0, 1)
        return Basis(basis)

    def is_computational(self):
        return self._basis == self._COMPUTATIONAL

    def is_hadamard(self):
        return self._basis == self._HADAMARD

    def to_str(self):
        if self.is_computational():
            return "+"
        assert self.is_hadamard()
        return "x"

    def to_bytes(self):
        if self.is_computational():
            return b"+"
        assert self.is_hadamard()
        return b"x"

    @classmethod
    def from_bytes(cls, data):
        assert len(data) == 1, "Bytes representation of basis much have length 1"
        if data == b"+":
            return Basis(cls._COMPUTATIONAL)
        assert data == b"x", "Bytes representation of basis must be + or x"
        return Basis(cls._HADAMARD)

class BitState:

    DECISION_NONE = b'?'
    DECISION_BASIS_MISMATCH = b'M'
    DECISION_KEEP_AS_KEY = b'K'
    DECISION_REVEAL_AS_0 = b'0'
    DECISION_REVEAL_AS_1 = b'1'

    COMPARISON_NONE = b'.'
    COMPARISON_SAME = b'S'
    COMPARISON_DIFFERENT = b'D'

    def __init__(self, bit, basis, qubit):
        self.bit = bit
        self.basis = basis
        self.client_basis = None
        self.qubit = qubit
        self.decision = self.DECISION_NONE
        self.comparison = self.COMPARISON_NONE

    def encode_qubit(self, cqc_connection):
        self.qubit = cqclib.qubit(cqc_connection)
        if self.basis.is_computational():
            if self.bit == 0:
                pass
            elif self.bit == 1:
                self.qubit.X()
            else:
                assert False, "Unknown bit value"
        elif self.basis.is_hadamard():
            if self.bit == 0:
                self.qubit.H()
            elif self.bit == 1:
                self.qubit.X()
                self.qubit.H()
            else:
                assert False, "Unknown bit value"
        else:
            assert False, "Unknown basis"

    def measure_qubit(self):
        if self.client_basis.is_computational():
            pass
        elif self.client_basis.is_hadamard():
            self.qubit.H()
        else:
            assert False, "Unknown basis"
        self.bit = self.qubit.measure()
        self.qubit = None

    def encode_decision(self):
        return self.decision

    def decode_decission(self, encoded_decision):
        assert len(encoded_decision) == 1, "Encoded decision must be 1 byte"
        assert self.decision in [self.DECISION_NONE,
                                 self.DECISION_BASIS_MISMATCH,
                                 self.DECISION_KEEP_AS_KEY,
                                 self.DECISION_REVEAL_AS_0,
                                 self.DECISION_REVEAL_AS_1], \
               f"Encoded decision has unexpected value {encoded_decision}"
        self.decision = encoded_decision

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

    def __init__(self, name):
        self._name = name
        self._cqc_connection = cqclib.CQCConnection(name)
        self._cqc_connection.__enter__()
        self._key_size = None
        self._revealed_bits_in_block = 0
        self._block_size = None
        self._key = []
        self._tx_stats = Stats(False, None)
        self._rx_stats = Stats(True, None)

    def __del__(self):
        # TODO: Is this inherited?
        self._cqc_connection.__exit__(None, None, None)

    def send_parameters(self, peer_name):
        assert self._block_size is not None, "Block size must be set"
        assert self._key_size is not None, "Key size must be set"
        msg = self._block_size.to_bytes(2, 'big') + self._key_size.to_bytes(2, 'big')
        self._cqc_connection.sendClassical(peer_name, msg)

    def receive_parameters(self):
        msg = self._cqc_connection.recvClassical()
        assert len(msg) == 4, "Parameters message must be 2 bytes"
        self._block_size = int.from_bytes(msg[0:2], 'big')
        self._key_size = int.from_bytes(msg[2:4], 'big')
        self._tx_stats.block_size = self._block_size
        self._rx_stats.block_size = self._block_size

    def create_random_qubits_block(self):
        block = []
        for _ in range(self._block_size):
            bit = random.randint(0, 1)
            basis = Basis.random()
            bit_state = BitState(bit, basis, None)
            block.append(bit_state)
        return block

    def send_qubits_block(self, block, peer_name):
        for bit_state in block:
            if bit_state.qubit is None:
                bit_state.encode_qubit(self._cqc_connection)
            self._cqc_connection.sendQubit(bit_state.qubit, peer_name)
            self._tx_stats.qubit += 1
        return block

    def receive_qubits_block(self):
        block = []
        for _ in range(self._block_size):
            qubit = self._cqc_connection.recvQubit()
            self._rx_stats.qubit += 1
            bit_state = BitState(None, None, qubit)
            block.append(bit_state)
        return block

    @staticmethod
    def measure_qubits_block(block, measure_percentage=None):
        for bit_state in block:
            assert bit_state.basis is None, "Basis must be none"
            if measure_percentage is None:
                measure = True
            else:
                measure = random.randint(1, 100) <= measure_percentage
            if measure:
                bit_state.client_basis = Basis.random()
                bit_state.measure_qubit()
                bit_state.basis = bit_state.client_basis
        return block

    def key_is_complete(self):
        key_len = len(self._key)
        if key_len < self._key_size:
            return False
        assert key_len == self._key_size, "Key length should never exceed requested key size"
        return True

    def decide_what_to_do_with_bit(self, bit_state):
        if bit_state.basis != bit_state.client_basis:
            bit_state.decision = BitState.DECISION_BASIS_MISMATCH
            return
        if self.key_is_complete():
            keep_as_key = False
        elif self._revealed_bits_in_block > (self._key_size + 1) // 2:
            keep_as_key = True
        else:
            keep_as_key = random.randint(0, 1) == 0
        if keep_as_key:
            bit_state.decision = BitState.DECISION_KEEP_AS_KEY
            self._key.append(bit_state.bit)
        else:
            if bit_state.bit == 0:
                bit_state.decision = BitState.DECISION_REVEAL_AS_0
            else:
                bit_state.decision = BitState.DECISION_REVEAL_AS_1
            self._revealed_bits_in_block += 1  ###@@@ Right thing for middle?

    def decide_what_to_do_with_block(self, block):
        for bit_state in block:
            self.decide_what_to_do_with_bit(bit_state)

    @staticmethod
    def count_decision(decision, stats):
        if decision == BitState.DECISION_BASIS_MISMATCH:
            stats.decision_basis_mismatch += 1
        elif decision == BitState.DECISION_KEEP_AS_KEY:
            stats.decision_use_as_key += 1
        elif decision == BitState.DECISION_REVEAL_AS_0:
            stats.decision_reveal_as_0 += 1
        elif decision == BitState.DECISION_REVEAL_AS_1:
            stats.decision_reveal_as_1 += 1

    def send_client_basis(self, block, peer_name):
        msg = b""
        for bit_state in block:
            msg += bit_state.client_basis.to_bytes()
        self._cqc_connection.sendClassical(peer_name, msg)

    def receive_client_basis(self, block):
        msg = self._cqc_connection.recvClassical()
        assert len(msg) == self._block_size, "Chosen basis message has wrong size"
        i = 0
        for bit_state in block:
            bit_state.client_basis = Basis.from_bytes(msg[i:i+1])
            i += 1

    def send_decisions(self, block, peer_name):
        msg = b""
        for bit_state in block:
            msg += bit_state.encode_decision()
            self.count_decision(bit_state.decision, self._tx_stats)
        self._cqc_connection.sendClassical(peer_name, msg)
        self._tx_stats.decision_msg += 1

    def receive_decisions(self, block):
        msg = self._cqc_connection.recvClassical()
        self._rx_stats.decision_msg += 1
        assert len(msg) == self._block_size, "Server decisions message has wrong size"
        i = 0
        for bit_state in block:
            bit_state.decode_decission(msg[i:i+1])
            self.count_decision(bit_state.decision, self._rx_stats)
            if bit_state.decision == BitState.DECISION_KEEP_AS_KEY:
                self._key.append(bit_state.bit)
            i += 1

    @staticmethod
    def compute_comparison(block):
        for bit_state in block:
            if bit_state.decision == bit_state.DECISION_REVEAL_AS_0:
                if bit_state.bit == 0:
                    bit_state.comparison = BitState.COMPARISON_SAME
                else:
                    bit_state.comparison = BitState.COMPARISON_DIFFERENT
            elif bit_state.decision == bit_state.DECISION_REVEAL_AS_1:
                if bit_state.bit == 1:
                    bit_state.comparison = BitState.COMPARISON_SAME
                else:
                    bit_state.comparison = BitState.COMPARISON_DIFFERENT
            else:
                bit_state.comparison = BitState.COMPARISON_NONE

    @staticmethod
    def count_comparison(comparison, stats):
        if comparison == BitState.COMPARISON_NONE:
            stats.comparison_none += 1
        elif comparison == BitState.COMPARISON_SAME:
            stats.comparison_same += 1
        elif comparison == BitState.COMPARISON_DIFFERENT:
            stats.comparison_different += 1


    def send_comparison(self, block, peer_name):
        msg = b""
        for bit_state in block:
            msg += bit_state.comparison
            self.count_comparison(bit_state.comparison, self._tx_stats)
        self._tx_stats.comparison_msg += 1
        self._cqc_connection.sendClassical(peer_name, msg)

    def receive_comparison(self, block):
        msg = self._cqc_connection.recvClassical()
        self._rx_stats.comparison_msg += 1
        i = 0
        for bit_state in block:
            bit_state.comparison = msg[i:i+1]
            self.count_comparison(bit_state.comparison, self._rx_stats)
            i += 1

    def print_report(self, elapsed_time):
        report = Report()
        report.add(f"*** {self._name} ***")
        report.add(f"Elpased time: {elapsed_time:.1f} secs")
        report.add(f"Key size: {self._key_size}")
        report.add(f"Key: {key_str(self._key)}")
        report.add(f"Block size: {self._block_size}")
        self._tx_stats.add_to_report(report, elapsed_time)
        self._rx_stats.add_to_report(report, elapsed_time)
        report.print()

class Server(Base):

    def __init__(self, name, client_name):
        Base.__init__(self, name)
        self._client_name = client_name

    def process_block(self):
        self._tx_stats.block += 1
        self._rx_stats.block += 1
        self._revealed_bits_in_block = 0
        block = self.create_random_qubits_block()
        self.send_qubits_block(block, self._client_name)
        self.receive_client_basis(block)
        self.decide_what_to_do_with_block(block)
        self.send_decisions(block, self._client_name)
        self.receive_comparison(block)

    def agree_key(self, report=False):
        start_time = time.perf_counter()
        self.receive_parameters()
        while not self.key_is_complete():
            self.process_block()
        elapsed_time = time.perf_counter() - start_time
        if report:
            self.print_report(elapsed_time)
        return self._key

class Client(Base):

    def __init__(self, name, server_name, key_size, block_size):
        Base.__init__(self, name)
        self._server_name = server_name
        self._key_size = key_size
        self._block_size = block_size
        self._tx_stats.block_size = self._block_size
        self._rx_stats.block_size = self._block_size

    def process_block(self):
        self._tx_stats.block += 1
        self._rx_stats.block += 1
        block = self.receive_qubits_block()
        self.measure_qubits_block(block)
        self.send_client_basis(block, self._server_name)
        self.receive_decisions(block)
        self.compute_comparison(block)
        self.send_comparison(block, self._server_name)

    def agree_key(self, report=False):
        start_time = time.perf_counter()
        self.send_parameters(self._server_name)
        while not self.key_is_complete():
            self.process_block()
        elapsed_time = time.perf_counter() - start_time
        if report:
            self.print_report(elapsed_time)
        return self._key

class Middle(Base):

    def __init__(self, name, server_name, client_name, observe_percentage):
        Base.__init__(self, name)
        self._server_name = server_name
        self._client_name = client_name
        self._observe_percentage = observe_percentage

    def process_block(self):
        self._tx_stats.block += 1
        self._rx_stats.block += 1
        self._revealed_bits_in_block = 0
        block = self.receive_qubits_block()
        self.measure_qubits_block(block, self._observe_percentage)
        self.send_qubits_block(block, self._client_name)
        self.receive_client_basis(block)
        self.send_client_basis(block, self._server_name)
        self.receive_decisions(block)
        self.send_decisions(block, self._client_name)
        self.receive_comparison(block)
        self.send_comparison(block, self._server_name)

    def pass_through(self, report=False):
        start_time = time.perf_counter()
        self.receive_parameters()
        self.send_parameters(self._server_name)
        while not self.key_is_complete():
            self.process_block()
        elapsed_time = time.perf_counter() - start_time
        if report:
            self.print_report(elapsed_time)
