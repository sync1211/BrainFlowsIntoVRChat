from logic.base_logic import Base_Logic

from brainflow.board_shim import BoardShim
import time

class Timeout(Base_Logic):
    def __init__(self, board, window_seconds=2, board_timeout=5):
        super().__init__(board)
        
        board_id = board.get_board_id()
        self.time_channel = BoardShim.get_timestamp_channel(board_id)
        self.sampling_rate = BoardShim.get_sampling_rate(board_id)

        self.window_seconds = window_seconds
        self.max_sample_size = self.sampling_rate * window_seconds
        self.board_timeout = board_timeout

    def get_data_dict(self):
        data = self.board.get_current_board_data(self.max_sample_size)
        time_data = data[self.time_channel]
        last_sample_time = time_data[-1]
        current_time = time.time()
        time_diff = current_time - last_sample_time

        if time_diff > self.board_timeout:
            raise TimeoutError("Biosensor board timed out")
        return {
            "osc_time_diff" : time_diff
        }
