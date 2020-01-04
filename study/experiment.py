from .aggregate import Aggregate

class Experiment:

    def __init__(self, code_version):
        self.code_version = code_version
        self.reconciliations = 0
        self.elapsed_process_time = Aggregate()
        self.elapsed_real_time = Aggregate()
        self.ask_parity_messages = Aggregate()
        self.ask_parity_blocks = Aggregate()
        self.infer_parity_blocks = Aggregate()
        self.remaining_bit_errors = Aggregate()
        self.remaining_frame_errors = Aggregate()

    def record_result(self, result):
        self.reconciliations += 1
        self.elapsed_process_time.record_value(result.elapsed_process_time)
        self.elapsed_real_time.record_value(result.elapsed_real_time)
        self.ask_parity_messages.record_value(result.ask_parity_messages)
        self.ask_parity_blocks.record_value(result.ask_parity_blocks)
        self.infer_parity_blocks.record_value(result.infer_parity_blocks)
        self.remaining_bit_errors.record_value(result.remaining_bit_errors)
        self.remaining_frame_errors.record_value(result.remaining_frame_errors)
