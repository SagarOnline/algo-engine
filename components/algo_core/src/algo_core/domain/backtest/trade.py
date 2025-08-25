from datetime import datetime
from algo_core.domain.strategy import Instrument

class Trade:

    def __init__(self, entry_time: datetime, entry_price: float, exit_time: datetime, exit_price: float, quantity: int):
        self.entry_time = entry_time
        self.entry_price = entry_price
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.quantity = quantity

    def profit(self) -> float:
        return (self.exit_price - self.entry_price) * self.quantity
    
    def profit_points(self) -> float:
        return (self.exit_price - self.entry_price)

    def profit_percentage(self) -> float:
        if self.entry_price == 0:
            return 0.0
        return ((self.exit_price - self.entry_price) / self.entry_price) * 100

    def to_dict(self):
        return {
            "entry_time": self.entry_time,
            "entry_price": self.entry_price,
            "exit_time": self.exit_time,
            "exit_price": self.exit_price,
            "profit": self.profit(),
            "profit_percentage": self.profit_percentage(),
            "quantity": self.quantity
        }
        
    def __repr__(self):
        return f"Trade(entry_time={self.entry_time}, entry_price={self.entry_price}, exit_time={self.exit_time}, exit_price={self.exit_price}, quantity={self.quantity})"
