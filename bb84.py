import random
# import time
import sys
import cqc.pythonLib as cqclib

# TODO: Add authentication and data integrety on classical channel (see http://bit.ly/bb84auth)
# TODO: Add documentation comments
# TODO: Add type annotations
# TODO: Add noise estimation
# TODO: Add information reconciliation
# TODO: Add privacy amplification
# TODO: Add throughput
# TODO: Add percentages
# TODO: Figure out why stopping SimulaQron doesn't work
# TODO: Reveal count seems too low; should be the same as key bits count

# def percent_str(count, total):
#     if total == 0:
#         return f"{count} (-)"
#     percentage = 100.0 * float(count) / float(total)
#     return f"{percentage:.1f}%"

# def throughput_str(count, duration):
#     throughput = count / duration
#     return f"{throughput:.1f} qubits/sec"

class Report:

    def __init__(self):
        self._text = ""

    def add(self, line):
        self._text += line + '\n'

    def print(self):
        print(self._text, file=sys.stderr)
        self._text = ""

# TODO: A bit over the top? Get rid of the Bit class?

class Bit:

    def __init__(self, bit):
        assert bit in [0, 1], "Bit value must be 0 or 1"
        self._bit = bit

    def __eq__(self, other):
        return self._bit == other._bit

    def __repr__(self):
        return self.to_str()

    @classmethod
    def random(cls):
        bit = random.randint(0, 1)
        return Bit(bit)

    def is_zero(self):
        return self._bit == 0

    def is_one(self):
        return self._bit == 1

    def to_str(self):
        if self.is_zero():
            return "0"
        assert self.is_one()
        return "1"

    def to_bytes(self):
        if self.is_zero():
            return b"0"
        assert self.is_one()
        return b"1"

    @classmethod
    def from_bytes(cls, data):
        assert len(data) == 1, "Bytes representation of bit much have length 1"
        if data == b"0":
            return Bit(0)
        assert data == b"x", "Bytes representation of bit must be 0 or 1"
        return Bit(1)

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
        self.decision = self.DECISION_NOT_DECIDED

    def to_qubit(self, cqc_connection):
        qubit = cqclib.qubit(cqc_connection)
        if self.basis.is_computational():
            if self.bit.is_zero():
                pass
            elif self.bit.is_one():
                qubit.X()
            else:
                assert False, "Unknown bit value"
        elif self.basis.is_hadamard():
            if self.bit.is_zero():
                qubit.H()
            elif self.bit.is_one():
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
        bit = Bit(qubit.measure())
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

class Stats:

    def __init__(self):
        self._blocks_count = 0
        self._qubits_count = 0
        self._basis_mismatch_count = 0
        self._key_bits_count = 0
        self._revealed_bits_count = 0
        self._comparison_same_count = 0
        self._comparison_different_count = 0

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
        self._comparison_different_count += 1

    def add_to_report(self, report):
        report.add(f"Blocks: {self._blocks_count}")
        report.add(f"Total qubits: {self._qubits_count}")
        report.add(f"Basis mismatches: {self._basis_mismatch_count}")
        report.add(f"Key bits: {self._key_bits_count}")
        report.add(f"Revealed bits: {self._revealed_bits_count}")
        report.add(f"Comparison same: {self._comparison_same_count}")
        report.add(f"Comparison different: {self._comparison_different_count}")

class Server:

    def __init__(self, server_name, client_name, key_size):
        self._server_name = server_name
        self._client_name = client_name
        self._cqc_connection = cqclib.CQCConnection(server_name)
        self._cqc_connection.__enter__()   # TODO: Also call __exit__ somewhere
        self._key_size = key_size
        self._revealed_bits_in_block = 0
        self._block_size = None
        self._key = []
        self._stats = Stats()

    def receive_block_size_from_client(self):
        msg = self._cqc_connection.recvClassical()
        assert len(msg) == 2, "Block size message must be 2 bytes"
        self._block_size = int.from_bytes(msg, 'big')

    def send_qubits_block(self):
        block = []
        for _ in range(self._block_size):
            bit = Bit.random()
            basis = Basis.random()
            print(f"Server TX bit {bit.to_str()}{basis.to_str()}")
            bit_state = BitState(bit, basis)
            qubit = bit_state.to_qubit(self._cqc_connection)
            self._cqc_connection.sendQubit(qubit, self._client_name)
            self._stats.count_qubit()
            block.append(bit_state)
        return block

    def key_is_complete(self):
        key_len = len(self._key)
        if key_len < self._key_size:
            return False
        assert key_len == self._key_size, "Key length should never exceed requested key size"
        return True

    def decide_what_to_do_with_bit(self, bit_state, client_basis):
        if bit_state.basis != client_basis:
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
            if bit_state.bit.is_zero():
                bit_state.decision = BitState.DECISION_REVEAL_AS_0
            else:
                bit_state.decision = BitState.DECISION_REVEAL_AS_1
            self._revealed_bits_in_block += 1
            self._stats.count_revealed_bit()

    def receive_client_basis(self, block):
        msg = self._cqc_connection.recvClassical()
        print(f"Server RX basis {msg}")
        assert len(msg) == self._block_size, "Chosen basis message has wrong size"
        i = 0
        for bit_state in block:
            client_basis = Basis.from_bytes(msg[i:i+1])
            self.decide_what_to_do_with_bit(bit_state, client_basis)
            i += 1

    def send_decisions(self, block):
        msg = b""
        for bit_state in block:
            msg += bit_state.encode_decision()
        print(f"Server TX decision {msg}")
        self._cqc_connection.sendClassical(self._client_name, msg)

    def receive_reveal_comparison(self, block):
        msg = self._cqc_connection.recvClassical()
        print(f"Server RX reveal comparison: {msg}")
        i = 0
        for _bit_state in block:
            reveal_comparison = msg[i:i+1]
            if reveal_comparison == BitState.REVEAL_COMPARISON_SAME:
                self._stats.count_comparison_same()
            elif reveal_comparison == BitState.REVEAL_COMPARISON_DIFFERENT:
                self._stats.count_comparison_different()
            i += 1
        # TODO: Store in bitstate for noise estimation

    def process_block(self):
        self._stats.count_block()
        self._revealed_bits_in_block = 0
        block = self.send_qubits_block()
        self.receive_client_basis(block)
        self.send_decisions(block)
        self.receive_reveal_comparison(block)

    def print_report(self):
        report = Report()
        report.add(f"Server {self._server_name}")
        report.add(f"Key size: {self._key_size}")
        report.add(f"Key: {self._key}")
        report.add(f"Block size: {self._block_size}")
        self._stats.add_to_report(report)
        report.print()

    def agree_key(self, report=False):
        self.receive_block_size_from_client()
        while not self.key_is_complete():
            self.process_block()
        if report:
            self.print_report()
        return self._key

class Client:

    def __init__(self, client_name, server_name, key_size, block_size):
        self._client_name = client_name
        self._server_name = server_name
        self._cqc_connection = cqclib.CQCConnection(client_name)
        self._cqc_connection.__enter__()
        self._key_size = key_size
        self._block_size = block_size
        self._key = []
        self._stats = Stats()

    def __del__(self):
        self._cqc_connection.__exit__(None, None, None)
        pass

    def send_block_size_to_server(self):
        # TODO: Eve could change the block size. Is that a vulnerability?
        msg = self._block_size.to_bytes(2, 'big')
        self._cqc_connection.sendClassical(self._server_name, msg)

    def receive_qubits_block(self):
        block = []
        for _ in range(self._block_size):
            basis = Basis.random()
            qubit = self._cqc_connection.recvQubit()
            self._stats.count_qubit()
            bit_state = BitState.from_qubit(qubit, basis)
            print(f"Client RX bit {bit_state.bit.to_str()}{bit_state.basis.to_str()}")
            block.append(bit_state)
        return block

    def key_is_complete(self):
        key_len = len(self._key)
        if key_len < self._key_size:
            return False
        assert key_len == self._key_size, "Key length should never exceed requested key size"
        return True

    def send_client_basis(self, block):
        msg = b""
        for bit_state in block:
            msg += bit_state.basis.to_bytes()
        self._cqc_connection.sendClassical(self._server_name, msg)
        print(f"Client TX basis: {msg}")

    def receive_decisions(self, block):
        msg = self._cqc_connection.recvClassical()
        print(f"Client RX decision {msg}")
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

    def send_reveal_comparison(self, block):
        msg = b""
        for bit_state in block:
            if bit_state.decision == bit_state.DECISION_REVEAL_AS_0:
                if bit_state.bit.is_zero():
                    msg += BitState.REVEAL_COMPARISON_SAME
                    self._stats.count_comparison_same()
                else:
                    msg += BitState.REVEAL_COMPARISON_DIFFERENT
                    self._stats.count_comparison_different()
            elif bit_state.decision == bit_state.DECISION_REVEAL_AS_1:
                if bit_state.bit.is_one():
                    msg += BitState.REVEAL_COMPARISON_SAME
                    self._stats.count_comparison_same()
                else:
                    msg += BitState.REVEAL_COMPARISON_DIFFERENT
                    self._stats.count_comparison_different()
            else:
                msg += BitState.REVEAL_COMPARISON_NOT_COMPARED
        self._cqc_connection.sendClassical(self._server_name, msg)
        print(f"Client TX reveal comparison: {msg}")

    def process_block(self):
        self._stats.count_block()
        block = self.receive_qubits_block()
        self.send_client_basis(block)
        self.receive_decisions(block)
        self.send_reveal_comparison(block)

    def print_report(self):
        report = Report()
        report.add(f"Client {self._client_name}")
        report.add(f"Key size: {self._key_size}")
        report.add(f"Key: {self._key}")
        report.add(f"Block size: {self._block_size}")
        self._stats.add_to_report(report)
        report.print()

    def agree_key(self, report=False):
        self.send_block_size_to_server()
        while not self.key_is_complete():
            self.process_block()
        if report:
            self.print_report()
        return self._key
