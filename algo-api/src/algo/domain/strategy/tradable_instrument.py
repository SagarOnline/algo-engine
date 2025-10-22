# Transaction domain class
from enum import Enum
from typing import List
from algo.domain.instrument.instrument import Instrument
from algo.domain.strategy.strategy import TradeAction


from datetime import datetime



class Transaction:
    def __init__(self, time: datetime, price: float, action: TradeAction, quantity: int):
        self.time = time
        self.price = price
        self.action = action
        self.quantity = quantity

    def __repr__(self):
        return f"Transaction(time={self.time}, price={self.price}, action={self.action}, quantity={self.quantity})"


class PositionType(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class TriggerType(Enum):
    ENTRY_RULES = "ENTRY_RULES"
    EXIT_RULES = "EXIT_RULES"
    STOP_LOSS = "STOP_LOSS"


class Position:
    def __init__(self, instrument: Instrument, position_type: PositionType, quantity: int, entry_price: float, entry_time: datetime, stop_loss: float = None, trigger_type: TriggerType = TriggerType.ENTRY_RULES):
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
        entry_action = TradeAction.BUY if position_type == PositionType.LONG else TradeAction.SELL
        entry_txn = Transaction(entry_time, entry_price, entry_action, quantity)
        self.transactions.append(entry_txn)
        self.entry_trigger_type = trigger_type  # To track how the position was entered
        self.exit_trigger_type = None  # To track how the position was exited

    def exit(self, exit_price: float, exit_time: datetime, trigger_type: TriggerType = TriggerType.EXIT_RULES):
        self.exit_trigger_type = trigger_type  # Store trigger type for reference
        
        # If trigger type is STOP_LOSS, calculate the stop loss price based on entry price and stop loss offset
        if trigger_type == TriggerType.STOP_LOSS and self.stop_loss is not None:
            actual_exit_price = self.stop_loss
        else:
            actual_exit_price = exit_price
        exit_action = TradeAction.SELL if self.position_type == PositionType.LONG else TradeAction.BUY
        exit_txn = Transaction(exit_time, actual_exit_price, exit_action, self.quantity)
        self.transactions.append(exit_txn)
        

    def is_open(self) -> bool:
        # Position is open if only entry transaction exists
        return len(self.transactions) == 1

    def has_stop_loss_hit(self, price: float) -> bool:
        """
        Check if the stop loss should be triggered based on the current price.
        Stop loss is treated as an offset from entry price.

        Args:
            price: Current market price

        Returns:
            bool: True if stop loss should be triggered, False otherwise
        """
        if not self.is_open() or self.stop_loss is None:
            return False
            
        entry_price = self.transactions[0].price
        
        # For LONG, stop loss triggers if price <= (entry_price - stop_loss_offset)
        # For SHORT, stop loss triggers if price >= (entry_price + stop_loss_offset)
        if self.position_type == PositionType.LONG:
            return price <= self.stop_loss
        else:  # SHORT
            return price >= self.stop_loss

    def pnl(self) -> float:
        if self.is_open():
            return 0.0
        # Use pnl_points for calculation
        return self.pnl_points() * self.quantity

    def pnl_percentage(self) -> float:
        if self.is_open():
            return 0.0
        entry_txn = self.transactions[0]
        return (self.pnl_points() / entry_txn.price)

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

    def add_position(self, time: datetime, price: float, action: TradeAction, quantity: int, stop_loss: float = None, trigger_type: TriggerType = TriggerType.ENTRY_RULES):
        # Determine position type from action
        position_type = PositionType.LONG if action == TradeAction.BUY else PositionType.SHORT
        position = Position(self.instrument, position_type, quantity, price, time, stop_loss, trigger_type)
        self.positions.append(position)

    def exit_position(self, time: datetime, price: float, action: TradeAction, quantity: int, trigger_type: TriggerType = TriggerType.EXIT_RULES):
        # Find last open position
        open_positions = [p for p in self.positions if p.is_open()]
        if not open_positions:
            raise RuntimeError("No open position to exit.")
        position = open_positions[-1]
        position.exit(price, time, trigger_type)

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
        closed_pnls = [p.pnl() for p in self.positions if not p.is_open() and p.pnl() > 0]
        return max(closed_pnls) if closed_pnls else 0

    # Maximum Loss incurred in a trade
    def max_loss(self) -> float:
        closed_pnls = [p.pnl() for p in self.positions if not p.is_open() and p.pnl() < 0]
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
        return f"TradableInstrument(instrument={self.instrument}, positions={self.positions})"