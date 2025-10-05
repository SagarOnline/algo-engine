from abc import ABC, abstractmethod
from algo.domain.strategy.strategy import Strategy


class StrategyRepository(ABC):
    @abstractmethod
    def get_strategy(self, strategy_name: str) -> Strategy:
        pass

    @abstractmethod
    def list_strategies(self) -> list[Strategy]:
        """Return a list of all available Strategy objects."""
        pass
