import os
import json
import pytest
from algo.infrastructure.json_strategy_repository import JsonStrategyRepository


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
        "algo.infrastructure.json_strategy_repository.get_config",
        lambda: DummyConfig,
    )
    return tmp_path


def test_get_strategy_success(patch_config, tmp_path):
    # Arrange
    strategy_name = "bullish_nifty"
    strategy_data = _get_strategy_data(strategy_name=strategy_name, timeframe="15min", capital=100000)
    make_strategy_json(tmp_path, strategy_name, strategy_data)
    repo = JsonStrategyRepository()
    # Act
    strategy = repo.get_strategy(strategy_name)
    # Assert
    assert strategy is not None
    assert strategy.name == strategy_name


def _get_strategy_data(strategy_name="bullish_nifty", timeframe="15min", capital=100000):
    strategy_data = {
        "name": strategy_name,
        "display_name": strategy_name.replace("_", " ").title() ,
        "instrument": {
            "type": "FUT",
            "expiry": "MONTHLY",
            "expiring": "NEXT1",
            "atm": -50,
            "instrument_key": "NSE_INDEX|Nifty 50",
            "exchange": "NSE",
        },
        "timeframe": timeframe,
        "capital": capital,
        "position": {
            "action": "BUY",
            "instrument": {
                "type": "FUT",
                "expiry": "MONTHLY",
                "expiring": "NEXT1",
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

    return strategy_data


def test_invalid_strategy_name(patch_config):
    repo = JsonStrategyRepository()
    with pytest.raises(ValueError):
        repo.get_strategy("nonexistent_strategy")


def test_list_strategies_returns_all_strategies(patch_config, tmp_path):
    # Arrange
    strategy_data_1 = _get_strategy_data(strategy_name="bullish_nifty", timeframe="15min", capital=100000)
    strategy_data_2 = _get_strategy_data(strategy_name="bearish_banknifty", timeframe="15min", capital=200000)
    make_strategy_json(tmp_path, "bullish_nifty", strategy_data_1)
    make_strategy_json(tmp_path, "bearish_banknifty", strategy_data_2)
    repo = JsonStrategyRepository()
    # Act
    strategies = repo.list_strategies()
    # Assert
    names = [s.name for s in strategies]
    assert "bullish_nifty" in names
    assert "bearish_banknifty" in names
    assert len(strategies) == 2
