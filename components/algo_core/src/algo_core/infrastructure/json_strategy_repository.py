

import json
import os
from algo_core.domain.strategy_repository import StrategyRepository
from algo_core.domain.strategy import Strategy
from algo_core.infrastructure.jsonstrategy import JsonStrategy
from algo_core.config_context import get_config


class JsonStrategyRepository(StrategyRepository):
    def __init__(self):
        config = get_config()
        self.base_dir = config.backtest_engine.strategy_json_config_dir

    def get_strategy(self, strategy_name: str) -> Strategy:
        file_path = os.path.join(self.base_dir, f"{strategy_name}.json")
        if not os.path.exists(file_path):
            raise ValueError(f"{strategy_name} is not a valid strategy name.")
        with open(file_path, 'r') as f:
            strategy_data = json.load(f)
        strategy = JsonStrategy(strategy_data)
        return strategy