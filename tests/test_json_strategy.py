import pytest
from infrastructure.jsonstrategy import JsonStrategy
from domain.strategy import (
    RuleSet,
    Condition,
    Expression,
    PositionAction,
    InstrumentType,
    Exchange,
    Expiry,
    Expiring,
)


@pytest.fixture
def sample_json():
    return {
        "strategy_name": "bullish_nifty",
        "symbol": "NIFTY",
        "exchange": "NSE",
        "timeframe": "5m",
        "capital": 100000,
        "position": {
            "action": "BUY",
            "instrument": {
                "type": "PE",
                "expiry": "MONTHLY",
                "expiring": "NEXT",
                "atm": -50,
                "symbol": "NIFTY",
                "exchange": "NSE",
            },
        },
        "entry_rules": {
            "logic": "AND",
            "conditions": [
                {
                    "operator": ">",
                    "left": {"type": "ema", "params": {"period": 20, "price": "close"}},
                    "right": {"type": "ema", "params": {"period": 50, "price": "close"}},
                },
                {
                    "operator": ">",
                    "left": {"type": "price", "params": {"price": "close"}},
                    "right": {"type": "ema", "params": {"period": 20, "price": "close"}},
                },
            ],
        },
        "exit_rules": {
            "logic": "OR",
            "conditions": [
                {
                    "operator": "<",
                    "left": {"type": "ema", "params": {"period": 20, "price": "close"}},
                    "right": {"type": "ema", "params": {"period": 50, "price": "close"}},
                },
                {
                    "operator": "<",
                    "left": {"type": "price", "params": {"price": "close"}},
                    "right": {"type": "ema", "params": {"period": 20, "price": "close"}},
                },
            ],
        },
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


def test_position(strategy):
    assert strategy.get_position().action == PositionAction.BUY
    assert strategy.get_position().instrument.type == InstrumentType.PE
    assert strategy.get_position().instrument.atm == -50
    assert strategy.get_position().instrument.exchange == Exchange.NSE
    assert strategy.get_position().instrument.expiry == Expiry.MONTHLY
    assert strategy.get_position().instrument.expiring == Expiring.NEXT
    assert strategy.get_position().instrument.symbol == "NIFTY"


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
