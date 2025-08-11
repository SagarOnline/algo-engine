import pytest
from typing import Dict, Any, List
from dataclasses import dataclass
from domain.indicators.registry import register_indicator, IndicatorRegistry

# --- Mock domain classes ---
@dataclass
class Expression:
    type: str
    params: Dict[str, Any]

@dataclass
class Condition:
    operator: str
    left: Expression
    right: Expression

@dataclass
class Rules:
    logic: str
    conditions: List[Condition]

# --- Mock indicators ---
@register_indicator("ema")
def mock_ema(candle: Dict[str, Any], historical_data: List[Dict[str, Any]], params: Dict[str, Any]) -> float:
    period = params.get("period", 20)
    # Just return period * 10 for testing
    return period * 10

@register_indicator("price")
def mock_price(candle: Dict[str, Any], historical_data: List[Dict[str, Any]], params: Dict[str, Any]) -> float:
    price_col = params.get("price", "close")
    return candle.get(price_col, 0)

# --- Dummy strategy implementation ---
class DummyStrategy:
    def __init__(self, entry_rules: Rules):
        self._entry_rules = entry_rules

    def get_entry_rules(self) -> Rules:
        return self._entry_rules

    def should_enter_trade(self, candle: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> bool:
        entry_rules = self.get_entry_rules()
        logic = entry_rules.logic.upper()
        results = [
            self._evaluate_condition(cond, candle, historical_data)
            for cond in entry_rules.conditions
        ]
        return all(results) if logic == "AND" else any(results)

    def _evaluate_condition(self, condition: Condition, candle, historical_data: List[Dict[str, Any]]) -> bool:
        left_value = self._evaluate_expression(condition.left, candle, historical_data)
        right_value = self._evaluate_expression(condition.right, candle, historical_data)
        if condition.operator == ">":
            return left_value > right_value
        elif condition.operator == "<":
            return left_value < right_value
        elif condition.operator == "==":
            return left_value == right_value
        else:
            raise ValueError(f"Unsupported operator: {condition.operator}")

    def _evaluate_expression(self, expression: Expression, candle, historical_data: List[Dict[str, Any]]) -> float:
        handler = IndicatorRegistry.get(expression.type.lower())
        return handler(candle, historical_data, expression.params)

# --- Test cases ---
def test_should_enter_trade_with_and_logic():
    # price = 105, ema20 = 200
    candle = {"close": 105}
    historical_data = []

    entry_rules = Rules(
        logic="AND",
        conditions=[
            Condition(
                operator=">",
                left=Expression(type="price", params={"price": "close"}),
                right=Expression(type="ema", params={"period": 5})  # returns 50
            ),
            Condition(
                operator="<",
                left=Expression(type="price", params={"price": "close"}),
                right=Expression(type="ema", params={"period": 20}) # returns 200
            )
        ]
    )

    strategy = DummyStrategy(entry_rules)
    assert strategy.should_enter_trade(candle, historical_data) is True

def test_should_enter_trade_with_or_logic():
    candle = {"close": 5}
    historical_data = []

    entry_rules = Rules(
        logic="OR",
        conditions=[
            Condition(
                operator=">",
                left=Expression(type="price", params={"price": "close"}),
                right=Expression(type="ema", params={"period": 20}) # returns 200
            ),
            Condition(
                operator="<",
                left=Expression(type="price", params={"price": "close"}),
                right=Expression(type="ema", params={"period": 1}) # returns 10
            )
        ]
    )

    strategy = DummyStrategy(entry_rules)
    assert strategy.should_enter_trade(candle, historical_data) is True
