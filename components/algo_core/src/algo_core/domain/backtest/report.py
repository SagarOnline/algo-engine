from typing import List
from algo_core.domain.trade import Trade


class BackTestReport:
    def __init__(self, strategy_name: str, pnl: float, trades: List[Trade]):
        self.strategy_name = strategy_name
        self.pnl = pnl
        self.trades = trades

    def to_dict(self):
        return {
            "strategy": self.strategy_name,
            "pnl": self.pnl,
            "trades": [trade.__dict__ for trade in self.trades]
        }
