from operator import is_

from datetime import date

from algo.domain.strategy.tradable_instrument import TradableInstrument


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
