from abc import ABC, abstractmethod
from algo.domain.strategy import Strategy

import os
import json
from algo.domain.strategy import Strategy

class StrategyRepository(ABC):
    @abstractmethod
    def get_strategy(self, strategy_name: str) -> Strategy:
        pass
