from datetime import datetime
from algo_core.domain.strategy import Instrument

class Trade:
    def __init__(self, instrument: Instrument, entry_time: datetime, entry_price: float, exit_time: datetime, exit_price: float):
        self.instrument = instrument
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.exit_time = exit_time
        self.exit_price = exit_price

    def profit(self) -> float:
        return self.exit_price - self.entry_price

    def __repr__(self):
        return f"Trade(instrument={self.instrument}, entry_time={self.entry_time}, entry_price={self.entry_price}, exit_time={self.exit_time}, exit_price={self.exit_price})"
