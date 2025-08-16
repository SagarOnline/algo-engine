from datetime import datetime
from domain.market import Market

class Trade:
    def __init__(self, market: Market, entry_time: datetime, entry_price: float, exit_time: datetime, exit_price: float):
        self.market = market
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.exit_time = exit_time
        self.exit_price = exit_price

    def profit(self) -> float:
        return self.exit_price - self.entry_price

    def __repr__(self):
        return f"Trade(market={self.market}, entry_time={self.entry_time}, entry_price={self.entry_price}, exit_time={self.exit_time}, exit_price={self.exit_price})"
