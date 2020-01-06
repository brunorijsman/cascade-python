import time

from aggregate_stats import AggregateStats

class Experiment:

    def __init__(self, algorithm_name, key_size, requested_error_rate, code_version):
        self.execution_time = time.strftime('%Y-%m-%d %H:%M:%S %Z')
        self.algorithm_name = algorithm_name
        self.key_size = key_size
        self.requested_error_rate = requested_error_rate
        self.code_version = code_version
        self.reconciliations = 0
        self.actual_bit_errors = AggregateStats()
        self.actual_bit_error_rate = AggregateStats()
        self.elapsed_process_time = AggregateStats()
        self.elapsed_real_time = AggregateStats()
        self.ask_parity_messages = AggregateStats()
        self.ask_parity_blocks = AggregateStats()
        self.ask_parity_bits = AggregateStats()
        self.reply_parity_bits = AggregateStats()
        self.unrealistic_efficiency = AggregateStats()
        self.realistic_efficiency = AggregateStats()
        self.infer_parity_blocks = AggregateStats()
        self.remaining_bit_errors = AggregateStats()
        self.remaining_bit_error_rate = AggregateStats()
        self.remaining_frame_errors = AggregateStats()

    def record_reconciliation_stats(self, stats):
        self.reconciliations += 1
        self.elapsed_process_time.record_value(stats.elapsed_process_time)
        self.elapsed_real_time.record_value(stats.elapsed_real_time)
        self.ask_parity_messages.record_value(stats.ask_parity_messages)
        self.ask_parity_blocks.record_value(stats.ask_parity_blocks)
        self.ask_parity_bits.record_value(stats.ask_parity_bits)
        self.reply_parity_bits.record_value(stats.reply_parity_bits)
        self.unrealistic_efficiency.record_value(stats.unrealistic_efficiency)
        self.realistic_efficiency.record_value(stats.realistic_efficiency)
        self.infer_parity_blocks.record_value(stats.infer_parity_blocks)
