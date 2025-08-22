import pytest
from unittest.mock import Mock
from datetime import date, datetime
from algo_core.domain.strategy import Strategy
from algo_core.domain.backtest.report import BackTestReport

from algo_core.domain.backtest.backtest_run import BackTest
from algo_core.domain.backtest.historical_data import HistoricalData

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
    return HistoricalData([
        generate_candle("2023-01-01T09:15:00", 100),
        generate_candle("2023-01-02T09:15:00", 110),
        generate_candle("2023-01-03T09:15:00", 120),
        generate_candle("2023-01-04T09:15:00", 130),
    ])

def test_start_returns_correct_report_for_no_trades(mock_strategy, historical_data):
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = False
    backtest = BackTest(mock_strategy, historical_data, position_instrument_hd=historical_data, start_date=date(2023, 1, 1))
    report = backtest.run()
    assert isinstance(report, BackTestReport)
    assert report.pnl == 0
    assert len(report.trades) == 0

def test_start_returns_correct_report_for_single_trade(mock_strategy, historical_data):
    # Enter on 2nd candle, exit on 4th
    mock_strategy.should_enter_trade.side_effect = [False, True, False, False]
    mock_strategy.should_exit_trade.side_effect = [True, False]
    backtest = BackTest(mock_strategy, historical_data, position_instrument_hd=historical_data, start_date=date(2023, 1, 1))
    report = backtest.run()
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
    backtest = BackTest(mock_strategy, historical_data, position_instrument_hd=historical_data, start_date=date(2023, 1, 1))
    # No changes needed, BackTest still expects a list of dicts for historical_data argument.
    report = backtest.run()
    assert len(report.trades) == 1
    trade = report.trades[0]
    assert trade.entry_price == 120
    assert trade.exit_price == 130
    assert report.pnl == 10

def test_run_with_different_position_instrument_hd_entry_and_exit(mock_strategy):
    # Underlying instrument (for signals)
    underlying_data = [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 100},
        {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 110},  # Entry
        {"timestamp": datetime(2023, 1, 1, 9, 45), "close": 120},
        {"timestamp": datetime(2023, 1, 1, 10, 0), "close": 130},  # Exit
    ]
    underlying_hd = HistoricalData(underlying_data)

    # Position instrument (for execution)
    position_data = [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 200},
        {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 210},
        {"timestamp": datetime(2023, 1, 1, 9, 45), "close": 220},
        {"timestamp": datetime(2023, 1, 1, 10, 0), "close": 230},
    ]
    position_hd = HistoricalData(position_data)

    # Entry on 9:30, exit on 10:00
    mock_strategy.should_enter_trade.side_effect = [False, True, False, False]
    mock_strategy.should_exit_trade.side_effect = [False,True]
    backtest = BackTest(mock_strategy, underlying_hd, position_instrument_hd=position_hd, start_date=date(2023, 1, 1))
    report = backtest.run()
    assert len(report.trades) == 1
    trade = report.trades[0]
    assert trade.entry_price == 210  # from position_hd at 9:30
    assert trade.exit_price == 230   # from position_hd at 10:00
    assert report.pnl == 20

def test_run_with_missing_exec_candle_raises_error(mock_strategy):
    # Underlying instrument (for signals)
    underlying_data = [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 100},
        {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 110},  # Entry
    ]
    underlying_hd = HistoricalData(underlying_data)

    # Position instrument (for execution) missing 9:30 candle
    position_data = [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 200},
    ]
    position_hd = HistoricalData(position_data)

    mock_strategy.should_enter_trade.side_effect = [False, True]
    mock_strategy.should_exit_trade.side_effect = [False, False]
    backtest = BackTest(mock_strategy, underlying_hd, position_instrument_hd=position_hd, start_date=date(2023, 1, 1))
    with pytest.raises(ValueError, match="No execution candle found for entry at timestamp 2023-01-01 09:30:00"):
        backtest.run()
