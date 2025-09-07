import json
import os
from algo.domain.strategy_repository import StrategyRepository
from algo.domain.strategy import Strategy
from algo.infrastructure.jsonstrategy import JsonStrategy
from algo.config_context import get_config


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

    def list_strategies(self) -> list[Strategy]:
        """Return a list of all available Strategy objects by reading all JSON files in the config directory."""
        strategies = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.base_dir, filename)
                with open(file_path, 'r') as f:
                    strategy_data = json.load(f)
                strategy = JsonStrategy(strategy_data)
                strategies.append(strategy)
        return strategies