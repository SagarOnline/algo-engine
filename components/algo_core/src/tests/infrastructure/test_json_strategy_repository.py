import os
import json
import pytest
from algo_core.infrastructure.json_strategy_repository import JsonStrategyRepository


class DummyConfig:
    class BacktestEngine:
        strategy_json_config_dir = None

    backtest_engine = BacktestEngine()


def make_strategy_json(tmpdir, name, data):
    file_path = os.path.join(tmpdir, f"{name}.json")
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path


@pytest.fixture
def patch_config(monkeypatch, tmp_path):
    DummyConfig.backtest_engine.strategy_json_config_dir = str(tmp_path)
    monkeypatch.setattr(
        "algo_core.infrastructure.json_strategy_repository.get_config",
        lambda: DummyConfig,
    )
    return tmp_path


def test_get_strategy_success(patch_config, tmp_path):
    # Arrange
    strategy_name = "bullish_nifty"
    strategy_data = {
        "strategy_name": "bullish_nifty",
        "instrument": {
            "type": "FUTURE",
            "expiry": "MONTHLY",
            "expiring": "NEXT",
            "atm": -50,
            "instrument_key": "NSE_INDEX|Nifty 50",
            "exchange": "NSE",
        },
        "timeframe": "15min",
        "capital": 100000,
        "position": {
            "action": "BUY",
            "instrument": {
                "type": "FUTURE",
                "expiry": "MONTHLY",
                "expiring": "NEXT",
                "atm": -50,
                "instrument_key": "NSE_FO|64103",
                "exchange": "NSE",
            },
        },
        "entry_rules": {
            "logic": "AND",
            "conditions": [
                {
                    "operator": ">",
                    "left": {"type": "ema", "params": {"period": 20, "price": "close"}},
                    "right": {
                        "type": "ema",
                        "params": {"period": 50, "price": "close"},
                    },
                },
                {
                    "operator": ">",
                    "left": {"type": "price", "params": {"price": "close"}},
                    "right": {
                        "type": "ema",
                        "params": {"period": 20, "price": "close"},
                    },
                },
            ],
        },
        "exit_rules": {
            "logic": "OR",
            "conditions": [
                {
                    "operator": "<",
                    "left": {"type": "ema", "params": {"period": 20, "price": "close"}},
                    "right": {
                        "type": "ema",
                        "params": {"period": 50, "price": "close"},
                    },
                },
                {
                    "operator": "<",
                    "left": {"type": "price", "params": {"price": "close"}},
                    "right": {
                        "type": "ema",
                        "params": {"period": 20, "price": "close"},
                    },
                },
            ],
        },
    }
    make_strategy_json(tmp_path, strategy_name, strategy_data)
    repo = JsonStrategyRepository()
    # Act
    strategy = repo.get_strategy(strategy_name)
    # Assert
    assert strategy is not None
    assert strategy.strategy_name == "bullish_nifty"


def test_get_strategy_file_not_found(patch_config):
    repo = JsonStrategyRepository()
    with pytest.raises(FileNotFoundError):
        repo.get_strategy("nonexistent_strategy")
