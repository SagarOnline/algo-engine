from typing import List, Dict
from algo_core.domain.trade import Trade


class BackTestReport:
    def __repr__(self):
        return (
            f"<BackTestReport strategy='{self.strategy_name}', "
            f"pnl={self.pnl}, trades={len(self.trades)}, "
            f"start_date={self.start_date}, end_date={self.end_date}, "
            f"total_pnl_points={self.total_pnl_points()}, "
            f"total_pnl_percentage={self.total_pnl_percentage():.2f}, "
            f"winning_trades={self.winning_trades_count()}, "
            f"losing_trades={self.losing_trades_count()}, "
            f"total_trades={self.total_trades_count()}, "
            f"winning_streak={self.winning_streak()}, "
            f"losing_streak={self.losing_streak()}, "
            f"max_gain={self.max_gain()}, max_loss={self.max_loss()}>"
        )
    def __init__(self, strategy_name: str, pnl: float, trades: List[Trade], start_date=None, end_date=None):
        self.strategy_name = strategy_name
        self.pnl = pnl
        self.trades = trades
        self.start_date = start_date
        self.end_date = end_date

    def to_dict(self):
        return {
            "strategy": self.strategy_name,
            "pnl": self.pnl,
            "trades": [trade.__dict__ for trade in self.trades],
            "start_date": self.start_date,
            "end_date": self.end_date
        }
    
    # Positions & Instruments details
    def positions(self) -> List[Dict]:
        return [
            {
                "instrument": trade.instrument.__dict__,
                "entry_time": trade.entry_time,
                "entry_price": trade.entry_price,
                "exit_time": trade.exit_time,
                "exit_price": trade.exit_price,
                "profit_points": trade.profit(),
                "profit_pct": (trade.profit() / trade.entry_price) * 100 if trade.entry_price else 0
            }
            for trade in self.trades
        ]

    # Profit and Loss in points
    def total_pnl_points(self) -> float:
        return sum(trade.profit() for trade in self.trades)

    # Profit and Loss in percentage
    def total_pnl_percentage(self) -> float:
        total_invested = sum(trade.entry_price for trade in self.trades if trade.entry_price > 0)
        if total_invested == 0:
            return 0
        return (self.total_pnl_points() / total_invested) * 100

    # Number of Winning Trades
    def winning_trades_count(self) -> int:
        return sum(1 for trade in self.trades if trade.profit() > 0)

    # Number of Losing Trades
    def losing_trades_count(self) -> int:
        return sum(1 for trade in self.trades if trade.profit() < 0)

    # Total Number of Trades executed
    def total_trades_count(self) -> int:
        return len(self.trades)

    # Winning Streak (longest consecutive winning trades)
    def winning_streak(self) -> int:
        max_streak = streak = 0
        for trade in self.trades:
            if trade.profit() > 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        return max_streak

    # Losing Streak (longest consecutive losing trades)
    def losing_streak(self) -> int:
        max_streak = streak = 0
        for trade in self.trades:
            if trade.profit() < 0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        return max_streak

    # Maximum Gain achieved in a trade
    def max_gain(self) -> float:
        if not self.trades:
            return 0
        return max(trade.profit() for trade in self.trades)

    # Maximum Loss incurred in a trade
    def max_loss(self) -> float:
        if not self.trades:
            return 0
        return min(trade.profit() for trade in self.trades)
