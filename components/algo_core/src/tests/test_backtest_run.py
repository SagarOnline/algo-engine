import pytest
from unittest.mock import Mock
from datetime import date, datetime
from algo_core.domain.strategy import Strategy
from algo_core.domain.backtest.report import BacktestReport

# Assuming BacktestRun is implemented in algo_core.domain.backtest.backtest_run
from algo_core.domain.backtest.backtest_run import BacktestRun

def generate_candle(timestamp_str: str, close_price: float):
    return {"timestamp": datetime.fromisoformat(timestamp_str), "close": close_price}

@pytest.fixture
def mock_strategy():
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_timeframe.return_value = "1d"
    strategy.get_instrument.return_value = "instrument"
    strategy.get_required_history_start_date.return_value = date(2023, 1, 1)
    return strategy

@pytest.fixture
def historical_data():
    return [
        generate_candle("2023-01-01T09:15:00", 100),
        generate_candle("2023-01-02T09:15:00", 110),
        generate_candle("2023-01-03T09:15:00", 120),
        generate_candle("2023-01-04T09:15:00", 130),
    ]

def test_start_returns_correct_report_for_no_trades(mock_strategy, historical_data):
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = False
    backtest_run = BacktestRun(mock_strategy, historical_data, date(2023, 1, 1))
    report = backtest_run.start()
    assert isinstance(report, BacktestReport)
    assert report.pnl == 0
    assert len(report.trades) == 0

def test_start_returns_correct_report_for_single_trade(mock_strategy, historical_data):
    # Enter on 2nd candle, exit on 4th
    mock_strategy.should_enter_trade.side_effect = [False, True, False, False]
    mock_strategy.should_exit_trade.side_effect = [True, False]
    backtest_run = BacktestRun(mock_strategy, historical_data, date(2023, 1, 1))
    report = backtest_run.start()
    assert len(report.trades) == 1
    trade = report.trades[0]
    assert trade.entry_price == 110
    assert trade.exit_price == 120
    assert report.pnl == 10

def test_start_respects_start_date(mock_strategy, historical_data):
    # Only allow trades after 2023-01-03
    start_date = date(2023, 1, 3)
    mock_strategy.should_enter_trade.side_effect = [False, False, True, False]
    mock_strategy.should_exit_trade.side_effect = [True]
    backtest_run = BacktestRun(mock_strategy, historical_data, date(2023, 1, 1))
    report = backtest_run.start()
    assert len(report.trades) == 1
    trade = report.trades[0]
    assert trade.entry_price == 120
    assert trade.exit_price == 130
    assert report.pnl == 10
