import pytest
from infrastructure.jsonstrategy import JsonStrategy
from domain.strategy import RuleSet,Condition,Expression


@pytest.fixture
def sample_json():
    return {
        "strategy_name": "bullish_nifty",
        "symbol": "NIFTY",
        "exchange": "NSE",
        "timeframe": "5m",
        "capital": 100000,
        "entry_rules": {
            "logic": "AND",
            "conditions": [
                {
                    "operator": ">",
                    "left": {
                        "type": "ema",
                        "params": {"period": 20, "price": "close"}
                    },
                    "right": {
                        "type": "ema",
                        "params": {"period": 50, "price": "close"}
                    }
                },
                {
                    "operator": ">",
                    "left": {
                        "type": "price",
                        "params": {"price": "close"}
                    },
                    "right": {
                        "type": "ema",
                        "params": {"period": 20, "price": "close"}
                    }
                }
            ]
        },
        "exit_rules": {
            "logic": "OR",
            "conditions": [
                {
                    "operator": "<",
                    "left": {
                        "type": "ema",
                        "params": {"period": 20, "price": "close"}
                    },
                    "right": {
                        "type": "ema",
                        "params": {"period": 50, "price": "close"}
                    }
                },
                {
                    "operator": "<",
                    "left": {
                        "type": "price",
                        "params": {"price": "close"}
                    },
                    "right": {
                        "type": "ema",
                        "params": {"period": 20, "price": "close"}
                    }
                }
            ]
        }
    }

@pytest.fixture
def strategy(sample_json):
    return JsonStrategy(sample_json)

def test_metadata(strategy):
    assert strategy.get_name() == "bullish_nifty"
    assert strategy.get_symbol() == "NIFTY"
    assert strategy.get_exchange() == "NSE"
    assert strategy.get_timeframe() == "5m"
    assert strategy.get_capital() == 100000

def test_entry_rules(strategy):
    ruleset = strategy.get_entry_rules()
    assert isinstance(ruleset, RuleSet)
    assert ruleset.logic == "AND"
    assert len(ruleset.conditions) == 2
    for cond in ruleset.conditions:
        assert isinstance(cond, Condition)
        assert isinstance(cond.left, Expression)
        assert isinstance(cond.right, Expression)

def test_exit_rules(strategy):
    ruleset = strategy.get_exit_rules()
    assert isinstance(ruleset, RuleSet)
    assert ruleset.logic == "OR"
    assert len(ruleset.conditions) == 2
    for cond in ruleset.conditions:
        assert isinstance(cond, Condition)
        assert isinstance(cond.left, Expression)
        assert isinstance(cond.right, Expression)
