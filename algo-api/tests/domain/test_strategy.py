import pytest
from typing import Dict, Any, List
from dataclasses import dataclass
from algo.domain.indicators.registry import register_indicator, IndicatorRegistry
from algo.domain.strategy import Strategy, Instrument, Timeframe, RuleSet, Expression, Condition, Position, InstrumentType, Exchange, PositionAction
from datetime import date, timedelta

# --- Mock domain classes ---
# Using real domain classes now for better testing

# --- Mock indicators ---
@register_indicator("ema")
def mock_ema(historical_data: List[Dict[str, Any]], params: Dict[str, Any]) -> float:
    period = params.get("period", 20)
    # Just return period * 10 for testing
    return period * 10

@register_indicator("price")
def mock_price(historical_data: List[Dict[str, Any]], params: Dict[str, Any]) -> float:
    price_col = params.get("price", "close")
    return historical_data[0].get(price_col, 0)

@register_indicator("number")
def mock_price(historical_data: List[Dict[str, Any]], params: Dict[str, Any]) -> float:
    value = params.get("value", 0)
    return value


# --- Dummy strategy implementation ---
class DummyStrategy(Strategy):
    def __init__(self, entry_rules: RuleSet, exit_rules: RuleSet = None, timeframe: Timeframe = Timeframe("1d")):
        self._entry_rules = entry_rules
        self._exit_rules = exit_rules if exit_rules else RuleSet(logic="AND", conditions=[])
        self._timeframe = timeframe

    def get_name(self) -> str:
        return "DummyStrategy"
    
    def get_display_name(self) -> str:
        return "Dummy Strategy"

    def get_instrument(self) -> Instrument:
        return Instrument(type=InstrumentType.STOCK, exchange=Exchange.NSE, instrument_key="DUMMY")

    def get_timeframe(self) -> Timeframe:
        return self._timeframe

    def get_capital(self) -> int:
        return 100000

    def get_entry_rules(self) -> RuleSet:
        return self._entry_rules

    def get_exit_rules(self) -> RuleSet:
        return self._exit_rules
    
    def get_position(self) -> Position:
        return Position(action=PositionAction.BUY, instrument=self.get_instrument())


# --- Test cases ---
def test_should_enter_trade_with_and_logic():
    # price = 105, ema20 = 200
    candle = {"close": 105}
    historical_data = [candle]

    entry_rules = RuleSet(
        logic="AND",
        conditions=[
            Condition(
                operator=">",
                left=Expression(expr_type="price", params={"price": "close"}),
                right=Expression(expr_type="number", params={"value": 50})  # returns 50
            ),
            Condition(
                operator="<",
                left=Expression(expr_type="price", params={"price": "close"}),
                right=Expression(expr_type="number", params={"value": 200}) # returns 200
            )
        ]
    )

    strategy = DummyStrategy(entry_rules)
    assert strategy.should_enter_trade(historical_data) is True

def test_should_enter_trade_with_or_logic():
    candle = {"close": 5}
    historical_data = [candle]

    entry_rules = RuleSet(
        logic="OR",
        conditions=[
            Condition(
                operator=">",
                left=Expression(expr_type="price", params={"price": "close"}),
                right=Expression(expr_type="number", params={"value": 200}) # returns 200
            ),
            Condition(
                operator="<",
                left=Expression(expr_type="price", params={"price": "close"}),
                right=Expression(expr_type="number", params={"value": 10}) # returns 10
            )
        ]
    )

    strategy = DummyStrategy(entry_rules)
    assert strategy.should_enter_trade(historical_data) is True

def test_get_required_history_start_date():
    entry_rules = RuleSet(
        logic="AND",
        conditions=[
            Condition(
                operator=">",
                left=Expression(expr_type="ema", params={"period": 50}),
                right=Expression(expr_type="ema", params={"period": 20})
            )
        ]
    )
    exit_rules = RuleSet(
        logic="AND",
        conditions=[
            Condition(
                operator="<",
                left=Expression(expr_type="ema", params={"period": 10}),
                right=Expression(expr_type="ema", params={"period": 100})
            )
        ]
    )
    
    strategy = DummyStrategy(entry_rules, exit_rules, timeframe=Timeframe("1d"))
    start_date = date(2023, 1, 1)
    
    # Max period is 100. 100 * 1.5 = 150 days buffer
    expected_date = start_date - timedelta(days=150)
    
    assert strategy.get_required_history_start_date(start_date) == expected_date

def test_get_required_history_start_date_no_period():
    entry_rules = RuleSet(
        logic="AND",
        conditions=[
            Condition(
                operator=">",
                left=Expression(expr_type="price", params={"price": "close"}),
                right=Expression(expr_type="price", params={"price": "open"})
            )
        ]
    )
    
    strategy = DummyStrategy(entry_rules, timeframe=Timeframe("1d"))
    start_date = date(2023, 1, 1)
    
    # No period, so should return start_date
    assert strategy.get_required_history_start_date(start_date) == start_date

def test_get_required_history_start_date_hourly():
    entry_rules = RuleSet(
        logic="AND",
        conditions=[
            Condition(
                operator=">",
                left=Expression(expr_type="ema", params={"period": 100}), # max period
                right=Expression(expr_type="ema", params={"period": 20})
            )
        ]
    )
    
    strategy = DummyStrategy(entry_rules, timeframe=Timeframe("60min"))
    start_date = date(2023, 1, 1)
    
    # 100 candles / (375/60 candles_per_day) = 16 days needed
    # 16 * 1.5 = 24 calendar days buffer
    expected_date = start_date - timedelta(days=24)
    
    assert strategy.get_required_history_start_date(start_date) == expected_date

def test_get_required_history_start_date_minute():
    entry_rules = RuleSet(
        logic="AND",
        conditions=[
            Condition(
                operator=">",
                left=Expression(expr_type="ema", params={"period": 200}), # max period
                right=Expression(expr_type="ema", params={"period": 50})
            )
        ]
    )
    
    strategy = DummyStrategy(entry_rules, timeframe=Timeframe("5min"))
    start_date = date(2023, 1, 1)
    
    # 200 candles / (375/5 candles_per_day) = 2.66 days -> ceil(3) = 3 days needed
    # 3 * 1.5 = 4.5 -> ceil(5) = 5 calendar days buffer
    expected_date = start_date - timedelta(days=5)
    
    assert strategy.get_required_history_start_date(start_date) == expected_date
    
def test_expression_evaluate_with_value():
    expr = Expression("number", {"value": 42})
    result = expr.evaluate([{"close": 1}])
    assert result == 42

def test_expression_evaluate_with_price():
    expr = Expression("price", {"price": "close"})
    data = [
        {"close": 10},
    ]
    result = expr.evaluate(data)
    assert result == 10
    
def test_condition_is_satisfied_gt():
    cond = Condition(
        operator=">",
        left=Expression("number", {"value": 10}),
        right=Expression("number", {"value": 5})
    )
    assert cond.is_satisfied([{"close": 1}]) is True
    
def test_condition_is_satisfied_lt():
    cond = Condition(
        operator="<",
        left=Expression("number", {"value": 2}),
        right=Expression("number", {"value": 5})
    )
    assert cond.is_satisfied([{"close": 1}]) is True

def test_condition_is_satisfied_eq():
    cond = Condition(
        operator="==",
        left=Expression("number", {"value": 7}),
        right=Expression("number", {"value": 7})
    )
    assert cond.is_satisfied([{"close": 1}]) is True

def test_condition_is_satisfied_nan():
    import math
    class NanIndicator:
        def __call__(self, historical_data, params):
            return float('nan')
    IndicatorRegistry._registry["nan"] = NanIndicator()
    cond = Condition(
        operator=">",
        left=Expression("nan", {}),
        right=Expression("number", {"value": 1})
    )
    assert cond.is_satisfied([{"close": 1}]) is False
    
def make_condition_true():
    return Condition(
        operator="==",
        left=Expression("number", {"value": 1}),
        right=Expression("number", {"value": 1})
    )

def make_condition_false():
    return Condition(
        operator="==",
        left=Expression("number", {"value": 1}),
        right=Expression("number", {"value": 2})
    )
    
def test_ruleset_apply_on_and():
    ruleset = RuleSet(
        logic="AND",
        conditions=[make_condition_true(), make_condition_true()]
    )
    assert ruleset.apply_on([{"close": 1}]) is True
    ruleset = RuleSet(
        logic="AND",
        conditions=[make_condition_true(), make_condition_false()]
    )
    assert ruleset.apply_on([{"close": 1}]) is False

def test_ruleset_apply_on_or():
    ruleset = RuleSet(
        logic="OR",
        conditions=[make_condition_true(), make_condition_false()]
    )
    assert ruleset.apply_on([{"close": 1}]) is True
    ruleset = RuleSet(
        logic="OR",
        conditions=[make_condition_false(), make_condition_false()]
    )
    assert ruleset.apply_on([{"close": 1}]) is False

def make_condition(val_left, op, val_right):
    return Condition(
        operator=op,
        left=Expression("number", {"value": val_left}),
        right=Expression("number", {"value": val_right})
    )

def test_apply_on_and_all_true():
    ruleset = RuleSet(
        logic="AND",
        conditions=[make_condition(1, "==", 1), make_condition(2, ">", 1)]
    )
    assert ruleset.apply_on([{"close": 1}]) is True

def test_apply_on_and_one_false():
    ruleset = RuleSet(
        logic="AND",
        conditions=[make_condition(1, "==", 1), make_condition(2, "<", 1)]
    )
    assert ruleset.apply_on([{"close": 1}]) is False

def test_apply_on_or_one_true():
    ruleset = RuleSet(
        logic="OR",
        conditions=[make_condition(1, "==", 2), make_condition(2, ">", 1)]
    )
    assert ruleset.apply_on([{"close": 1}]) is True

def test_apply_on_or_all_false():
    ruleset = RuleSet(
        logic="OR",
        conditions=[make_condition(1, "==", 2), make_condition(2, "<", 1)]
    )
    assert ruleset.apply_on([{"close": 1}]) is False

def test_ruleset_get_maximum_period_value():
    ruleset = RuleSet(
        logic="AND",
        conditions=[
            Condition(
                operator=">",
                left=Expression("ema", {"period": 10}),
                right=Expression("ema", {"period": 20})
            ),
            Condition(
                operator="<",
                left=Expression("ema", {"period": 50}),
                right=Expression("ema", {"period": 5})
            ),
            Condition(
                operator="==",
                left=Expression("number", {"value": 1}),
                right=Expression("number", {"value": 2})
            )
        ]
    )
    assert ruleset.get_maximum_period_value() == 50

def test_ruleset_get_maximum_period_value_none():
    ruleset = RuleSet(
        logic="AND",
        conditions=[
            Condition(
                operator=">",
                left=Expression("number", {"value": 1}),
                right=Expression("number", {"value": 2})
            )
        ]
    )
    assert ruleset.get_maximum_period_value() == 0