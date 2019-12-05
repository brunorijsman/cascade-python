import cqc.pythonLib as cqclib
from .constants import *

class BitState:

    def __init__(self, bit, tx_basis, qubit):
        self.bit = bit
        self.tx_basis = tx_basis
        self.measure_basis = None
        self.base_mismatch = False
        self.qubit = qubit
        self.decision = DECISION_NONE
        self.comparison = COMPARISON_NONE

    def encode_qubit(self, cqc_connection):
        self.qubit = cqclib.qubit(cqc_connection)
        if self.bit == 1:
            self.qubit.X()
        if self.tx_basis == BASIS_HADAMARD:
            self.qubit.H()

    def measure_qubit(self):
        if self.measure_basis == BASIS_HADAMARD:
            self.qubit.H()
        self.bit = self.qubit.measure()
        self.qubit = None
