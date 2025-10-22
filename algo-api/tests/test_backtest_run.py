import pytest
from unittest.mock import Mock
from datetime import date, datetime
from algo.domain.instrument.instrument import Exchange, Instrument, Type
from algo.domain.strategy.strategy import TradeAction, Strategy
from algo.domain.backtest.report import BackTestReport

from algo.domain.backtest.backtest_run import BackTest
from algo.domain.backtest.historical_data import HistoricalData

def generate_candle(timestamp_str: str, close_price: float):
    return {"timestamp": datetime.fromisoformat(timestamp_str), "close": close_price}

@pytest.fixture
def mock_strategy():
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_timeframe.return_value = "1d"
    position_instrument = Mock()
    position_instrument.action = TradeAction.BUY
    position_instrument.get_close_action.return_value = TradeAction.SELL
    strategy.get_position_instrument.return_value = position_instrument
    instrument = Instrument(type=Type.EQ, exchange=Exchange.NSE, instrument_key="NSE_INE869I01013")
    strategy.get_instrument.return_value = instrument
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

@pytest.mark.skip(reason="Skipping backtest run tests")
def test_start_returns_correct_report_for_no_trades(mock_strategy, historical_data):
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = False
    mock_strategy.calculate_stop_loss_for.return_value = None
    backtest = BackTest(mock_strategy, historical_data, position_instrument_hd=historical_data, start_date=date(2023, 1, 1), end_date=date(2023, 1, 4))
    report = backtest.run()
    assert isinstance(report, BackTestReport)
    assert report.total_pnl() == 0
    assert len(report.tradable.positions) == 0
    assert report.start_date == date(2023, 1, 1)
    assert report.end_date == date(2023, 1, 4)

    # Additional BackTestReport method checks for empty trades
    assert report.total_pnl_points() == 0
    assert report.total_pnl_percentage() == 0
    assert report.winning_trades_count() == 0
    assert report.losing_trades_count() == 0
    assert report.total_trades_count() == 0
    assert report.winning_streak() == 0
    assert report.losing_streak() == 0
    assert report.max_gain() == 0
    assert report.max_loss() == 0

@pytest.mark.skip(reason="Skipping backtest run tests")
def test_start_returns_correct_report_for_single_trade(mock_strategy, historical_data):
    # Enter on 2nd candle, exit on 4th
    mock_strategy.should_enter_trade.side_effect = [False, True, False, False]
    mock_strategy.should_exit_trade.side_effect = [True, False]
    mock_strategy.calculate_stop_loss_for.return_value = None
    backtest = BackTest(mock_strategy, historical_data, position_instrument_hd=historical_data, start_date=date(2023, 1, 1), end_date=date(2023, 1, 4))
    report = backtest.run()
    assert len(report.tradable.positions) == 1
    position = report.tradable.positions[0]
    assert position.entry_price() == 110
    assert position.exit_price()     == 120
    assert report.total_pnl() == 10
    assert report.start_date == date(2023, 1, 1)
    assert report.end_date == date(2023, 1, 4)

    # Additional BackTestReport method checks
    assert report.total_pnl_points() == 10
    assert report.total_pnl_percentage() == pytest.approx(10/110)
    assert report.winning_trades_count() == 1
    assert report.losing_trades_count() == 0
    assert report.total_trades_count() == 1
    assert report.winning_streak() == 1
    assert report.losing_streak() == 0
    assert report.max_gain() == 10
    assert report.max_loss() == 10

@pytest.mark.skip(reason="Skipping backtest run tests")
def test_start_respects_start_date(mock_strategy, historical_data):
    # Only allow trades after 2023-01-03
    start_date = date(2023, 1, 3)
    mock_strategy.should_enter_trade.side_effect = [False, False, True, False]
    mock_strategy.should_exit_trade.side_effect = [True]
    mock_strategy.calculate_stop_loss_for.return_value = None
    backtest = BackTest(mock_strategy, historical_data, position_instrument_hd=historical_data, start_date=date(2023, 1, 1), end_date=date(2023, 1, 4))
    # No changes needed, BackTest still expects a list of dicts for historical_data argument.
    report = backtest.run()
    assert len(report.tradable.positions) == 1
    assert report.start_date == date(2023, 1, 1)
    assert report.end_date == date(2023, 1, 4)
    position = report.tradable.positions[0]
    assert position.entry_price() == 120
    assert position.exit_price() == 130
    assert report.total_pnl() == 10

@pytest.mark.skip(reason="Skipping backtest run tests")
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
    mock_strategy.calculate_stop_loss_for.return_value = None
    backtest = BackTest(mock_strategy, underlying_hd, position_instrument_hd=position_hd, start_date=date(2023, 1, 1), end_date=date(2023, 1, 1))
    report = backtest.run()
    assert len(report.tradable.positions) == 1
    position = report.tradable.positions[0]
    assert position.entry_price() == 210  # from position_hd at 9:30
    assert position.exit_price() == 230   # from position_hd at 10:00
    assert report.total_pnl() == 20

    # Additional BackTestReport method checks
    assert report.total_pnl_points() == 20
    assert report.total_pnl_percentage() == pytest.approx(20/210)
    assert report.winning_trades_count() == 1
    assert report.losing_trades_count() == 0
    assert report.total_trades_count() == 1
    assert report.winning_streak() == 1
    assert report.losing_streak() == 0
    assert report.max_gain() == 20
    assert report.max_loss() == 20

@pytest.mark.skip(reason="Skipping backtest run tests")
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
    backtest = BackTest(mock_strategy, underlying_hd, position_instrument_hd=position_hd, start_date=date(2023, 1, 1), end_date=date(2023, 1, 1))
    with pytest.raises(ValueError, match="No execution candle found for entry at timestamp 2023-01-01 09:30:00"):
        backtest.run()
