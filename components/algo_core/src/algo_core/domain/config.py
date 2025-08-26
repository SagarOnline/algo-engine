import os
from enum import Enum


def get_value(value: str, env_var: str, default: str) -> str:
    env_value = os.environ.get(env_var)
    if env_value:
        return env_value
    elif value:
        return value
    else:
        return default


class HistoricalDataBackend(Enum):
    PARQUET_FILES = "PARQUET_FILES"
    UPSTOX_API = "UPSTOX_API"


class UpstoxConfig:
    def __init__(
        self,
        #  api_key: str, api_secret: str, redirect_uri: str,
        redirect_url: str,
    ):
        # self.api_key = api_key
        # self.api_secret = api_secret
        # self.redirect_uri = redirect_uri
        self.redirect_url = get_value(
            redirect_url, "BROKER_API.UPSTOX.REDIRECT_URL", ""
        )


class BrokerAPIConfig:
    def __init__(self, upstox_config: UpstoxConfig = None):
        self.upstox_config = upstox_config


class BacktestEngineConfig:
    def __init__(
        self,
        historical_data_backend: HistoricalDataBackend,
        reports_path: str,
        historical_data_path: str,
        strategies_path: str,
    ):
        backend = get_value(
            historical_data_backend,
            "BACKTEST_ENGINE.HISTORICAL_DATA_BACKEND",
            HistoricalDataBackend.PARQUET_FILES.value,
        )

        self.historical_data_backend = HistoricalDataBackend[backend]

        self.reports_path = get_value(
            reports_path, "BACKTEST_ENGINE.REPORTS_PATH", os.getcwd()
        )

        self.historical_data_path = get_value(
            historical_data_path, "BACKTEST_ENGINE.HISTORICAL_DATA_PATH", os.getcwd()
        )

        self.strategies_path = get_value(
            strategies_path, "BACKTEST_ENGINE.STRATEGIES_PATH", os.getcwd()
        )


class Config:
    def __init__(self, backtest_engine: BacktestEngineConfig, broker_api: dict):
        self.backtest_engine = backtest_engine
        self.broker_api = broker_api

    @staticmethod
    def from_dict(config_dict):
        be = config_dict.get("backtest_engine", {})
        backtest_engine = BacktestEngineConfig(
            historical_data_backend=be.get("historical_data_backend", ""),
            reports_path=be.get("reports_path", ""),
            historical_data_path=be.get("historical_data_path", ""),
            strategies_path=be.get("strategies_path", ""),
        )
        broker_api = config_dict.get("broker_api", {})
        broker_api_config = BrokerAPIConfig(
            upstox_config=UpstoxConfig(
                redirect_url=broker_api.get("upstox", {}).get("redirect_url", "")
            )
        )
        return Config(backtest_engine=backtest_engine, broker_api=broker_api_config)
