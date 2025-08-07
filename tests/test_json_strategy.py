import pytest
from infrastructure.jsonstrategy import JsonStrategy
from domain.strategy import Indicator, RiskManagement, RuleGroup

SAMPLE_STRATEGY = {
    "strategy_name": "test_strategy",
    "symbol": "TEST",
    "exchange": "NSE",
    "timeframe": "15m",
    "indicators": [
        {"name": "sma_fast", "type": "SMA", "params": {"period": 50}},
        {"name": "rsi_14", "type": "RSI", "params": {"period": 14}}
    ],
    "entry_rules": {
        "logic": "AND",
        "conditions": [
            {"condition": "crossover", "left": "sma_fast", "right": "close"},
            {"condition": "less_than", "left": "rsi_14", "right": 70}
        ]
    },
    "exit_rules": {
        "logic": "OR",
        "conditions": [
            {"condition": "crossunder", "left": "sma_fast", "right": "close"}
        ]
    },
    "risk_management": {
        "capital": 100000,
        "order_type": "MIS",
        "position_size": {"type": "fixed", "value": 100},
        "stop_loss_percent": 1.5,
        "take_profit_percent": 3
    },
    "active_time": {
        "days": ["Monday", "Tuesday"],
        "start_time": "09:15",
        "end_time": "15:25"
    },
    "metadata": {
        "created_by": "tester",
        "created_at": "2025-08-03T00:00:00Z"
    }
}


def test_get_indicators():
    strategy = JsonStrategy(SAMPLE_STRATEGY)
    indicators = strategy.get_indicators()
    assert len(indicators) == 2
    assert indicators[0].name == "sma_fast"
    assert indicators[1].type == "RSI"

def test_get_entry_rules():
    strategy = JsonStrategy(SAMPLE_STRATEGY)
    rules = strategy.get_entry_rules()
    assert isinstance(rules, RuleGroup)
    assert rules.logic == "AND"
    assert len(rules.conditions) == 2

def test_get_exit_rules():
    strategy = JsonStrategy(SAMPLE_STRATEGY)
    rules = strategy.get_exit_rules()
    assert rules.logic == "OR"
    assert len(rules.conditions) == 1

def test_get_risk_management():
    strategy = JsonStrategy(SAMPLE_STRATEGY)
    rm = strategy.get_risk_management()
    assert rm.capital == 100000
    assert rm.position_size.type == "fixed"
    assert rm.position_size.value == 100

def test_get_active_time_window():
    strategy = JsonStrategy(SAMPLE_STRATEGY)
    window = strategy.get_active_time_window()
    assert "Monday" in window.days
    assert window.start_time == "09:15"

def test_get_metadata():
    strategy = JsonStrategy(SAMPLE_STRATEGY)
    metadata = strategy.get_metadata()
    assert metadata.created_by == "tester"
