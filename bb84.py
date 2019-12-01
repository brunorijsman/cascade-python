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
# TODO: Count classical messages
# TODO: Fix eve observing script
# TODO: Add observe_qubit_percentage to Middle class
# TODO: Report RX and TX stats separately
# TODO: Control message tracing with environment variable

def percent_str(count, total):
    if total == 0:
        return f"{count} (-)"
    percentage = 100.0 * float(count) / float(total)
    return f"{percentage:.1f}%"

def throughput_str(count, duration, unit):
    throughput = count / duration
    return f"[{throughput:.1f} {unit}/sec]"

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

    DECISION_NOT_DECIDED = b'?'
    DECISION_BASIS_MISMATCH = b'M'
    DECISION_KEEP_AS_KEY = b'K'
    DECISION_REVEAL_AS_0 = b'0'
    DECISION_REVEAL_AS_1 = b'1'

    REVEAL_COMPARISON_NOT_COMPARED = b'.'
    REVEAL_COMPARISON_SAME = b'S'
    REVEAL_COMPARISON_DIFFERENT = b'D'

    def __init__(self, bit, basis):
        self.bit = bit
        self.basis = basis
        self.client_basis = None
        self.decision = self.DECISION_NOT_DECIDED

    def to_qubit(self, cqc_connection):
        qubit = cqclib.qubit(cqc_connection)
        if self.basis.is_computational():
            if self.bit == 0:
                pass
            elif self.bit == 1:
                qubit.X()
            else:
                assert False, "Unknown bit value"
        elif self.basis.is_hadamard():
            if self.bit == 0:
                qubit.H()
            elif self.bit == 1:
                qubit.X()
                qubit.H()
            else:
                assert False, "Unknown bit value"
        else:
            assert False, "Unknown basis"
        return qubit

    @classmethod
    def from_qubit(cls, qubit, basis):
        if basis.is_computational():
            pass
        elif basis.is_hadamard():
            qubit.H()
        else:
            assert False, "Unknown basis"
        bit = qubit.measure()
        return BitState(bit, basis)

    def encode_decision(self):
        return self.decision

    def decode_decission(self, encoded_decision):
        assert len(encoded_decision) == 1, "Encoded decision must be 1 byte"
        assert self.decision in [self.DECISION_NOT_DECIDED,
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

    def __init__(self):
        self._blocks_count = 0
        self._qubits_count = 0
        self._basis_mismatch_count = 0
        self._key_bits_count = 0
        self._revealed_bits_count = 0
        self._comparison_same_count = 0
        self._comparison_diff_count = 0

    def count_block(self):
        self._blocks_count += 1

    def count_qubit(self):
        self._qubits_count += 1

    def count_basis_mismatch(self):
        self._basis_mismatch_count += 1

    def count_key_bit(self):
        self._key_bits_count += 1

    def count_revealed_bit(self):
        self._revealed_bits_count += 1

    def count_comparison_same(self):
        self._comparison_same_count += 1

    def count_comparison_different(self):
        self._comparison_diff_count += 1

    def add_to_report(self, report, elapsed_time):
        report.add(f"Blocks: {self._blocks_count} " +
                   f"{throughput_str(self._blocks_count, elapsed_time, 'blocks')}")
        report.add(f"Total qubits: {self._qubits_count} " +
                   f"{throughput_str(self._qubits_count, elapsed_time, 'qubits')}")
        report.add(f"Basis mismatches: {self._basis_mismatch_count} " +
                   f"({percent_str(self._basis_mismatch_count, self._qubits_count)} of total) " +
                   f"{throughput_str(self._basis_mismatch_count, elapsed_time, 'mismatches')}")
        report.add(f"Key bits: {self._key_bits_count} " +
                   f"({percent_str(self._key_bits_count, self._qubits_count)} of total) " +
                   f"{throughput_str(self._key_bits_count, elapsed_time, 'bits')}")
        basis_match_count = self._qubits_count - self._basis_mismatch_count
        report.add(f"Revealed bits: {self._revealed_bits_count} " +
                   f"({percent_str(self._revealed_bits_count, basis_match_count)} of "
                   f"matching basis) " +
                   f"{throughput_str(self._revealed_bits_count, elapsed_time, 'bits')}")
        report.add(f"Comparison same: {self._comparison_same_count} " +
                   f"({percent_str(self._comparison_same_count, self._revealed_bits_count)} " +
                   f"of revealed) " +
                   f"{throughput_str(self._comparison_same_count, elapsed_time, 'comparisons')}")
        report.add(f"Comparison different: {self._comparison_diff_count} " +
                   f"({percent_str(self._comparison_diff_count, self._revealed_bits_count)} " +
                   f"of revealed) " +
                   f"{throughput_str(self._comparison_diff_count, elapsed_time, 'comparisons')}")

class Base:

    def __init__(self, name):
        self._name = name
        self._cqc_connection = cqclib.CQCConnection(name)
        self._cqc_connection.__enter__()
        self._key_size = None
        self._revealed_bits_in_block = 0
        self._block_size = None
        self._key = []
        self._stats = Stats()

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

    def send_qubits_block(self, peer_name):
        block = []
        for _ in range(self._block_size):
            bit = random.randint(0, 1)
            basis = Basis.random()
            bit_state = BitState(bit, basis)
            qubit = bit_state.to_qubit(self._cqc_connection)
            self._cqc_connection.sendQubit(qubit, peer_name)
            self._stats.count_qubit()
            block.append(bit_state)
        return block

    def receive_qubits_block(self):
        block = []
        for _ in range(self._block_size):
            basis = Basis.random()
            qubit = self._cqc_connection.recvQubit()
            self._stats.count_qubit()
            bit_state = BitState.from_qubit(qubit, basis)
            block.append(bit_state)
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
            self._stats.count_basis_mismatch()
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
            self._stats.count_key_bit()
        else:
            if bit_state.bit == 0:
                bit_state.decision = BitState.DECISION_REVEAL_AS_0
            else:
                bit_state.decision = BitState.DECISION_REVEAL_AS_1
            self._revealed_bits_in_block += 1
            self._stats.count_revealed_bit()

    def decide_what_to_do_with_block(self, block):
        for bit_state in block:
            self.decide_what_to_do_with_bit(bit_state)

    def send_client_basis(self, block, peer_name):
        msg = b""
        for bit_state in block:
            msg += bit_state.basis.to_bytes()
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
        self._cqc_connection.sendClassical(peer_name, msg)

    def receive_decisions(self, block):
        msg = self._cqc_connection.recvClassical()
        assert len(msg) == self._block_size, "Server decisions message has wrong size"
        i = 0
        for bit_state in block:
            bit_state.decode_decission(msg[i:i+1])
            if bit_state.decision == bit_state.DECISION_KEEP_AS_KEY:
                self._key.append(bit_state.bit)
                self._stats.count_key_bit()
            elif bit_state.decision == BitState.DECISION_BASIS_MISMATCH:
                self._stats.count_basis_mismatch()
            elif bit_state.decision in [BitState.DECISION_REVEAL_AS_0,
                                        BitState.DECISION_REVEAL_AS_1]:
                self._stats.count_revealed_bit()
            i += 1

    def send_reveal_comparison(self, block, peer_name):
        msg = b""
        for bit_state in block:
            if bit_state.decision == bit_state.DECISION_REVEAL_AS_0:
                if bit_state.bit == 0:
                    msg += BitState.REVEAL_COMPARISON_SAME
                    self._stats.count_comparison_same()
                else:
                    msg += BitState.REVEAL_COMPARISON_DIFFERENT
                    self._stats.count_comparison_different()
            elif bit_state.decision == bit_state.DECISION_REVEAL_AS_1:
                if bit_state.bit == 1:
                    msg += BitState.REVEAL_COMPARISON_SAME
                    self._stats.count_comparison_same()
                else:
                    msg += BitState.REVEAL_COMPARISON_DIFFERENT
                    self._stats.count_comparison_different()
            else:
                msg += BitState.REVEAL_COMPARISON_NOT_COMPARED
        self._cqc_connection.sendClassical(peer_name, msg)

    def receive_reveal_comparison(self, block):
        msg = self._cqc_connection.recvClassical()
        i = 0
        for _bit_state in block:
            reveal_comparison = msg[i:i+1]
            if reveal_comparison == BitState.REVEAL_COMPARISON_SAME:
                self._stats.count_comparison_same()
            elif reveal_comparison == BitState.REVEAL_COMPARISON_DIFFERENT:
                self._stats.count_comparison_different()
            i += 1
        # TODO: Store in bitstate for noise estimation

    def print_report(self, elapsed_time):
        report = Report()
        report.add(f"*** {self._name} ***")
        report.add(f"Elpased time: {elapsed_time:.1f} secs")
        report.add(f"Key size: {self._key_size}")
        report.add(f"Key: {''.join([str(bit) for bit in self._key])}")
        report.add(f"Block size: {self._block_size}")
        self._stats.add_to_report(report, elapsed_time)
        report.print()

class Server(Base):

    def __init__(self, name, client_name):
        Base.__init__(self, name)
        self._client_name = client_name

    def process_block(self):
        self._stats.count_block()
        self._revealed_bits_in_block = 0
        block = self.send_qubits_block(self._client_name)
        self.receive_client_basis(block)
        self.decide_what_to_do_with_block(block)
        self.send_decisions(block, self._client_name)
        self.receive_reveal_comparison(block)

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

    def process_block(self):
        self._stats.count_block()
        block = self.receive_qubits_block()
        self.send_client_basis(block, self._server_name)
        self.receive_decisions(block)
        self.send_reveal_comparison(block, self._server_name)

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

    def __init__(self, name, server_name, client_name):
        Base.__init__(self, name)
        self._server_name = server_name
        self._client_name = client_name

    def process_block(self):
        self._stats.count_block()
        self._revealed_bits_in_block = 0
        block = self.receive_qubits_block()         ###@@@
        block = self.send_qubits_block(self._client_name)   ###@@@
        self.receive_client_basis(block)
        self.send_client_basis(block, self._server_name)
        self.receive_decisions(block)
        self.send_decisions(block, self._client_name)
        self.receive_reveal_comparison(block)
        self.send_reveal_comparison(block, self._server_name)

    def pass_through(self, report=False):
        start_time = time.perf_counter()
        self.receive_parameters()
        self.send_parameters(self._server_name)
        while not self.key_is_complete():
            self.process_block()
        elapsed_time = time.perf_counter() - start_time
        if report:
            self.print_report(elapsed_time)
