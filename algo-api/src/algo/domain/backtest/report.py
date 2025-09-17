from operator import is_
from algo.domain.strategy import Instrument, PositionAction
from enum import Enum

from datetime import datetime, date
from typing import List


# Transaction domain class
class Transaction:
    def __init__(self, time: datetime, price: float, action: PositionAction, quantity: int):
        self.time = time
        self.price = price
        self.action = action
        self.quantity = quantity

    def __repr__(self):
        return f"Transaction(time={self.time}, price={self.price}, action={self.action}, quantity={self.quantity})"


class PositionType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class PositionExitType(Enum):
    EXIT_RULES = "EXIT_RULES"
    STOP_LOSS = "STOP_LOSS"

class Position:
    def __init__(self, instrument: Instrument, position_type: PositionType, quantity: int, entry_price: float, entry_time: datetime, stop_loss: float = None):
        if entry_price == 0:
            raise ValueError("Entry price cannot be zero.")
        if quantity == 0:
            raise ValueError("Quantity cannot be zero.")
        self.instrument = instrument
        self.position_type = position_type
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.transactions: List[Transaction] = []
        # Create the entry transaction
        entry_action = PositionAction.BUY if position_type == PositionType.LONG else PositionAction.SELL
        entry_txn = Transaction(entry_time, entry_price, entry_action, quantity)
        self.transactions.append(entry_txn)
        self.exit_type = None  # To track how the position was exited

    def exit(self, exit_price: float, exit_time: datetime, exit_type: PositionExitType = PositionExitType.EXIT_RULES):
        exit_action = PositionAction.SELL if self.position_type == PositionType.LONG else PositionAction.BUY
        exit_txn = Transaction(exit_time, exit_price, exit_action, self.quantity)
        self.transactions.append(exit_txn)
        self.exit_type = exit_type  # Store exit type for reference

    def is_open(self) -> bool:
        # Position is open if only entry transaction exists
        return len(self.transactions) == 1

    def process_stop_loss(self, price: float, time: datetime):
        if not self.is_open() or self.stop_loss is None:
            return False
        # For LONG, stop loss triggers if price <= stop_loss
        # For SHORT, stop loss triggers if price >= stop_loss
        if self.position_type == PositionType.LONG and price <= self.stop_loss:
            self.exit(self.stop_loss, time, PositionExitType.STOP_LOSS)
            return True
        elif self.position_type == PositionType.SHORT and price >= self.stop_loss:
            self.exit(self.stop_loss, time, PositionExitType.STOP_LOSS)
            return True
        return False

    def pnl(self) -> float:
        if self.is_open():
            return 0.0
        # Use pnl_points for calculation
        return self.pnl_points() * self.quantity
    
    def pnl_percentage(self) -> float:
        if self.is_open():
            return 0.0
        entry_txn = self.transactions[0]
        return (self.pnl_points() / entry_txn.price) * 100  

    def pnl_points(self) -> float:
        if self.is_open():
            return 0.0
        entry_txn = self.transactions[0]
        exit_txn = self.transactions[-1]
        # For LONG: exit - entry
        # For SHORT: entry - exit
        if self.position_type == PositionType.LONG:
            return exit_txn.price - entry_txn.price
        else:
            return entry_txn.price - exit_txn.price

    def entry_price(self) -> float:
        return self.transactions[0].price if self.transactions else None

    def entry_time(self) -> datetime:
        return self.transactions[0].time if self.transactions else None

    def exit_price(self) -> float:
        if self.is_open():
            return None
        return self.transactions[-1].price

    def exit_time(self) -> datetime:
        if self.is_open():
            return None
        return self.transactions[-1].time
    
    def __repr__(self):
        return (f"Position(instrument={self.instrument}, position_type={self.position_type}, "
                f"quantity={self.quantity}, stop_loss={self.stop_loss}, transactions={self.transactions})")

class TradableInstrument:
    def __init__(self, instrument: Instrument):
        self.instrument = instrument
        self.positions: List[Position] = []  # List of Position objects (open and closed)

    def add_position(self, time: datetime, price: float, action: PositionAction, quantity: int, stop_loss: float = None):
        # Determine position type from action
        position_type = PositionType.LONG if action == PositionAction.BUY else PositionType.SHORT
        position = Position(self.instrument, position_type, quantity, price, time, stop_loss)
        self.positions.append(position)

    def exit_position(self, time: datetime, price: float, action: PositionAction, quantity: int):
        # Find last open position
        open_positions = [p for p in self.positions if p.is_open()]
        if not open_positions:
            raise RuntimeError("No open position to exit.")
        position = open_positions[-1]
        position.exit(price, time)

    def total_pnl_points(self) -> float:
        return sum(p.pnl_points() for p in self.positions if not p.is_open())

    def total_pnl(self) -> float:
        return sum(p.pnl() for p in self.positions if not p.is_open())

    def total_pnl_percentage(self) -> float:
        total_buy = sum(p.transactions[0].price * p.quantity for p in self.positions if not p.is_open())
        total_sell = sum(p.transactions[-1].price * p.quantity for p in self.positions if not p.is_open())
        return ((total_sell - total_buy) / total_buy) if total_buy != 0 else 0

    # Number of Winning Trades
    def winning_trades_count(self) -> int:
        return sum(1 for p in self.positions if not p.is_open() and p.pnl() > 0)

    # Number of Losing Trades
    def losing_trades_count(self) -> int:
        return sum(1 for p in self.positions if not p.is_open() and p.pnl() < 0)

    # Total Number of Trades executed
    def total_trades_count(self) -> int:
        return sum(1 for p in self.positions if not p.is_open())

    # Winning Streak (longest consecutive winning trades)
    def winning_streak(self) -> int:
        max_streak = streak = 0
        for p in self.positions:
            if not p.is_open() and p.pnl() > 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        return max_streak

    # Losing Streak (longest consecutive losing trades)
    def losing_streak(self) -> int:
        max_streak = streak = 0
        for p in self.positions:
            if not p.is_open() and p.pnl() < 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        return max_streak

    # Maximum Gain achieved in a trade
    def max_gain(self) -> float:
        closed_pnls = [p.pnl() for p in self.positions if not p.is_open()]
        return max(closed_pnls) if closed_pnls else 0

    # Maximum Loss incurred in a trade
    def max_loss(self) -> float:
        closed_pnls = [p.pnl() for p in self.positions if not p.is_open()]
        return min(closed_pnls) if closed_pnls else 0

    def is_any_position_open(self) -> bool:
        return any(p.is_open() for p in self.positions)

    def process_stop_loss(self, price: float, time: datetime):
        """
        Runs process_stop_loss on all open positions. Returns True if any position was closed due to stop loss.
        """
        triggered = False
        for position in self.positions:
            if position.is_open():
                if position.process_stop_loss(price, time):
                    triggered = True
        return triggered

    def __repr__(self):
        return f"TradableInstrument_2(instrument={self.instrument}, positions={self.positions})"

class BackTestReport:
    def __init__(self, strategy_name: str, tradable: TradableInstrument, start_date: date, end_date: date):
        self.strategy_name = strategy_name
        self.tradable = tradable
        self.start_date: date = start_date
        self.end_date: date = end_date

    def to_dict(self):
        return {
            "instrument": {
                "name": self.tradable.instrument.to_dict(),
                "positions": [repr(pos) for pos in self.tradable.positions]
            },
            "summary": {
                "strategy": self.strategy_name,
                "start_date": self.start_date,
                "end_date": self.end_date,
                "total_pnl_points": self.total_pnl_points(),
                "total_pnl_percentage": self.total_pnl_percentage(),
                "winning_trades_count": self.winning_trades_count(),
                "losing_trades_count": self.losing_trades_count(),
                "total_trades_count": self.total_trades_count(),
                "winning_streak": self.winning_streak(),
                "losing_streak": self.losing_streak(),
                "max_gain": self.max_gain(),
                "max_loss": self.max_loss(),
            }
        }

    def __repr__(self):
        return self.to_dict().__repr__()
    
    def total_pnl(self) -> float:
        return self.tradable.total_pnl()
    
    def total_pnl_points(self) -> float:
        return self.tradable.total_pnl_points()

    def total_pnl_percentage(self) -> float:
        return self.tradable.total_pnl_percentage()

    def winning_trades_count(self) -> int:
        return self.tradable.winning_trades_count()

    def losing_trades_count(self) -> int:
        return self.tradable.losing_trades_count()

    def total_trades_count(self) -> int:
        return self.tradable.total_trades_count()

    def winning_streak(self) -> int:
        return self.tradable.winning_streak()

    def losing_streak(self) -> int:
        return self.tradable.losing_streak()

    def max_gain(self) -> float:
        return self.tradable.max_gain()

    def max_loss(self) -> float:
        return self.tradable.max_loss()
