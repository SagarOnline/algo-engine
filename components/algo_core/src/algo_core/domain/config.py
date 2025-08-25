import os

class BacktestEngineConfig:
    def __init__(self, historical_data_backend: str, reports_path: str, historical_data_path: str, strategies_path: str):
        self.historical_data_backend = historical_data_backend

        self.reports_path = self._get_value(reports_path, 'BACKTEST_ENGINE.REPORTS_PATH', os.getcwd())

        self.historical_data_path = self._get_value(historical_data_path, 'BACKTEST_ENGINE.HISTORICAL_DATA_PATH', os.getcwd())

        self.strategies_path = self._get_value(strategies_path, 'BACKTEST_ENGINE.STRATEGIES_PATH', os.getcwd())

    def _get_value(self, value: str, env_var: str, default: str) -> str:
        env_value = os.environ.get(env_var)
        if env_value:
            return env_value
        elif value:
            return value
        else:
            return default


class Config:
    def __init__(self, backtest_engine: BacktestEngineConfig):
        self.backtest_engine = backtest_engine

    @staticmethod
    def from_dict(config_dict):
        be = config_dict.get('backtest_engine', {})
        backtest_engine = BacktestEngineConfig(
            historical_data_backend=be.get('historical_data_backend', ''),
            reports_path=be.get('reports_path', ''),
            historical_data_path=be.get('historical_data_path', ''),
            strategies_path=be.get('strategies_path', '')
        )
        return Config(backtest_engine=backtest_engine)
