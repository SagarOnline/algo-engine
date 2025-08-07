import pytest
from domain.market import Candle
from domain.strategy import Strategy
from infrastructure.jsonstrategy import JsonStrategy

SAMPLE_STRATEGY = {
    "strategy_name": "test_strategy",
    "symbol": "TEST",
    "exchange": "NSE",
    "timeframe": "15m",
    "indicators": [
        {"name": "sma_fast", "type": "SMA", "params": {"period": 50}},
        {"name": "rsi_14", "type": "RSI", "params": {"period": 14}},
    ],
    "entry_rules": {
        "logic": "AND",
        "conditions": [
            {"condition": "crossover", "left": "sma_fast", "right": "close"},
            {"condition": "less_than", "left": "rsi_14", "right": 70},
        ],
    },
    "exit_rules": {
        "logic": "OR",
        "conditions": [{"condition": "crossunder", "left": "sma_fast", "right": "close"}]
    },
    "risk_management": {
        "capital": 100000,
        "order_type": "MIS",
        "position_size": {"type": "fixed", "value": 100},
        "stop_loss_percent": 1.5,
        "take_profit_percent": 3,
    },
    "metadata": {"created_by": "tester", "created_at": "2025-08-03T00:00:00Z"},
}


@pytest.fixture
def strategy_instance():
    return JsonStrategy(SAMPLE_STRATEGY)


def test_hold_when_no_rules_match(strategy_instance: Strategy):
    candle = Candle(
        open=100,
        high=105,
        low=99,
        close=101,
        volume=1000,
        indicators={"sma_fast": 100, "rsi_14": 60},
    )
    # sma_fast (100) is not > close (101) -> crossover is false
    action = strategy_instance.evaluate_for_entry(candle)
    assert action == "HOLD"


def test_entry_when_rules_match(strategy_instance: Strategy):
    candle = Candle(
        open=100,
        high=105,
        low=99,
        close=101,
        volume=1000,
        indicators={"sma_fast": 102, "rsi_14": 60},
    )
    # sma_fast (102) > close (101) -> crossover is true
    # rsi_14 (60) < 70 -> less_than is true
    # AND -> true
    action = strategy_instance.evaluate_for_entry(candle)
    assert action == "ENTRY"


def test_exit_when_rules_match(strategy_instance: Strategy):
    # Now, provide a candle that triggers an exit
    exit_candle = Candle(
        open=110,
        high=112,
        low=108,
        close=109,
        volume=1200,
        indicators={"sma_fast": 108, "rsi_14": 75},
    )
    # sma_fast (108) < close (109) -> crossunder is true
    action = strategy_instance.evaluate_for_exit(exit_candle)
    assert action == "EXIT"


def test_hold_when_in_market_and_no_exit_rules_match(strategy_instance: Strategy):
    # Now, provide a candle that does NOT trigger an exit
    hold_candle = Candle(
        open=110,
        high=112,
        low=108,
        close=110,
        volume=1200,
        indicators={"sma_fast": 111, "rsi_14": 65},
    )
    # sma_fast (111) is not < close (110) -> crossunder is false
    action = strategy_instance.evaluate_for_exit(hold_candle)
    assert action == "HOLD"
