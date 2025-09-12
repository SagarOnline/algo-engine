from algo.domain.strategy import Instrument, PositionAction

from datetime import datetime, date
from typing import List
from algo.domain.backtest.trade import Trade


# Transaction domain class
class Transaction:
    def get_position(self) -> float:
        if self.action == PositionAction.BUY:
            return self.quantity
        elif self.action == PositionAction.SELL:
            return -self.quantity
        return 0.0
    def __init__(self, time: datetime, price: float, action: PositionAction, quantity: int):
        self.time = time
        self.price = price
        self.action = action
        self.quantity = quantity

    def __repr__(self):
        return f"Transaction(time={self.time}, price={self.price}, action={self.action}, quantity={self.quantity})"

# InstrumentTransactions domain class
class TradableInstrument:

    def __init__(self, instrument: Instrument):
        self.instrument = instrument
        self.transactions: list[Transaction] = []
        self.trades: list[Trade] = []
        self.open_positions: list[Transaction] = []   # keeps unmatched transactions

    def execute_order(self, time: datetime, price: float, action: PositionAction, quantity: int):
        txn = Transaction(time, price, action, quantity)
        self.transactions.append(txn)

        # Try to match against an open position
        if self.open_positions:
            last_open = self.open_positions[-1]

            # Check if this closes the position
            if last_open.action != txn.action and last_open.quantity == txn.quantity:
                trade = Trade(
                    entry_time=last_open.time,
                    entry_price=last_open.price,
                    exit_time=txn.time,
                    exit_price=txn.price,
                    quantity=txn.quantity
                )
                self.trades.append(trade)
                self.open_positions.pop()  # remove the matched open txn
                return

        # If no match, treat this as a new open position
        self.open_positions.append(txn)
        
    def is_trade_open(self) -> bool:
        """
        Returns True if there are still open positions.
        """
        return len(self.open_positions) > 0
    
    

    def __repr__(self):
        return f"TradableInstrument(instrument={self.instrument}, transactions={self.transactions})"
        
class BackTestReport:
    def __repr__(self):
        return self.to_dict().__repr__()
    
    def __init__(self, strategy_name: str, tradable: TradableInstrument, start_date: date, end_date: date):
        self.strategy_name = strategy_name
        self.tradable = tradable
        self.start_date: date = start_date
        self.end_date: date = end_date

    def to_dict(self):
        return {
            "instrument":{
                "name": self.tradable.instrument.to_dict(),
                 "trades": [trade.to_dict() for trade in self.tradable.trades]  
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

    # Profit and Loss in points
    def total_pnl_points(self) -> float:
        # Treat transactions as a ledger: BUY is negative, SELL is positive
        return sum(trade.profit_points() for trade in self.tradable.trades)
    
    def total_pnl(self) -> float:
        # Treat transactions as a ledger: BUY is negative, SELL is positive
        return sum(trade.profit() for trade in self.tradable.trades)

    # Profit and Loss in percentage
    def total_pnl_percentage(self) -> float:
        total_invested = sum(trade.entry_price for trade in self.tradable.trades if trade.entry_price > 0)
        if total_invested == 0:
            return 0
        return (self.total_pnl_points() / total_invested) * 100

    # Number of Winning Trades
    def winning_trades_count(self) -> int:
        return sum(1 for trade in self.tradable.trades if trade.profit() > 0)

    # Number of Losing Trades
    def losing_trades_count(self) -> int:
        return sum(1 for trade in self.tradable.trades if trade.profit() < 0)

    # Total Number of Trades executed
    def total_trades_count(self) -> int:
        return len(self.tradable.trades)

    # Winning Streak (longest consecutive winning trades)
    def winning_streak(self) -> int:
        max_streak = streak = 0
        for trade in self.tradable.trades:
            if trade.profit() > 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        return max_streak

    # Losing Streak (longest consecutive losing trades)
    def losing_streak(self) -> int:
        max_streak = streak = 0
        for trade in self.tradable.trades:
            if trade.profit() < 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        return max_streak

    # Maximum Gain achieved in a trade
    def max_gain(self) -> float:
        if not self.tradable.trades:
            return 0
        return max(trade.profit() for trade in self.tradable.trades)

    # Maximum Loss incurred in a trade
    def max_loss(self) -> float:
        if not self.tradable.trades:
            return 0
        return min(trade.profit() for trade in self.tradable.trades)
