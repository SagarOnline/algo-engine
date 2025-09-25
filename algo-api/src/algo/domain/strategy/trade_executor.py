from abc import ABC, abstractmethod
from .strategy_evaluator import TradeSignal

class TradeExecutor(ABC):
    @abstractmethod
    def execute(self, trade_signal: TradeSignal) -> None:
        """Execute the given trade signal."""
        pass
