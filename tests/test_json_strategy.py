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
from domain.timeframe import Timeframe


@pytest.fixture
def sample_json():
    return {
        "strategy_name": "bullish_nifty",
        "instrument": {
            "type": "PE",
            "expiry": "MONTHLY",
            "expiring": "NEXT",
            "atm": -50,
            "instrument_key": "NIFTY",
            "exchange": "NSE",
        },
        "timeframe": "5min",
        "capital": 100000,
        "position": {
            "action": "BUY",
            "instrument": {
                "type": "PE",
                "expiry": "MONTHLY",
                "expiring": "NEXT",
                "atm": -50,
                "instrument_key": "NIFTY",
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
def sample_json_required_only():
    return {
        "strategy_name": "bullish_nifty",
        "instrument": {"type": "PE", "instrument_key": "NIFTY", "exchange": "NSE"},
        "timeframe": "5min",
        "capital": 100000,
        "position": {
            "action": "BUY",
            "instrument": {"type": "PE", "instrument_key": "NIFTY", "exchange": "NSE"},
        },
        "entry_rules": {
            "logic": "AND",
            "conditions": [
                {
                    "operator": ">",
                    "left": {"type": "ema", "params": {"period": 20, "price": "close"}},
                    "right": {"type": "ema", "params": {"period": 50, "price": "close"}},
                }
            ],
        },
        "exit_rules": {
            "logic": "OR",
            "conditions": [
                {
                    "operator": "<",
                    "left": {"type": "ema", "params": {"period": 20, "price": "close"}},
                    "right": {"type": "ema", "params": {"period": 50, "price": "close"}},
                }
            ],
        },
    }


@pytest.fixture
def strategy(sample_json):
    return JsonStrategy(sample_json)


@pytest.fixture
def strategy_required_only(sample_json_required_only):
    return JsonStrategy(sample_json_required_only)


def test_metadata(strategy):
    assert strategy.get_name() == "bullish_nifty"
    assert strategy.get_timeframe() == Timeframe.FIVE_MINUTES
    assert strategy.get_capital() == 100000


def test_instrument(strategy):
    assert strategy.get_instrument().type == InstrumentType.PE
    assert strategy.get_instrument().exchange == Exchange.NSE
    assert strategy.get_instrument().expiry == Expiry.MONTHLY
    assert strategy.get_instrument().expiring == Expiring.NEXT
    assert strategy.get_instrument().atm == -50
    assert strategy.get_instrument().instrument_key == "NIFTY"


def test_instrument_required_only(strategy_required_only):
    assert strategy_required_only.get_instrument().type == InstrumentType.PE
    assert strategy_required_only.get_instrument().exchange == Exchange.NSE
    assert strategy_required_only.get_instrument().instrument_key == "NIFTY"
    assert strategy_required_only.get_instrument().expiry is None
    assert strategy_required_only.get_instrument().expiring is None
    assert strategy_required_only.get_instrument().atm is None


def test_position(strategy):
    assert strategy.get_position().action == PositionAction.BUY
    assert strategy.get_position().instrument.type == InstrumentType.PE
    assert strategy.get_position().instrument.atm == -50
    assert strategy.get_position().instrument.exchange == Exchange.NSE
    assert strategy.get_position().instrument.expiry == Expiry.MONTHLY
    assert strategy.get_position().instrument.expiring == Expiring.NEXT
    assert strategy.get_position().instrument.instrument_key == "NIFTY"


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
