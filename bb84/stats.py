def percent_str(count, total):
    if total == 0:
        return f"-"
    percentage = 100.0 * float(count) / float(total)
    return f"{percentage:.1f}%"

def throughput_str(count, duration, unit):
    throughput = count / duration
    return f"[{throughput:.1f} {unit}/sec]"

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
