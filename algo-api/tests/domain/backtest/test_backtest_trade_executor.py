import unittest
import pytest
from datetime import datetime, date
from unittest.mock import Mock, MagicMock

from algo.domain.backtest.backtest_trade_executor import BackTestTradeExecutor
from algo.domain.strategy.strategy_evaluator import TradeSignal
from algo.domain.strategy.strategy import Instrument, InstrumentType, Exchange, TradeAction
from algo.domain.backtest.report import TradableInstrument
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.timeframe import Timeframe


@pytest.fixture
def mock_tradable_instrument_repository():
    return Mock()


@pytest.fixture
def mock_historical_data_repository():
    return Mock()


@pytest.fixture
def sample_instrument():
    return Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")


@pytest.fixture
def sample_tradable_instrument(sample_instrument):
    return TradableInstrument(sample_instrument)


@pytest.fixture
def sample_trade_signal(sample_instrument):
    return TradeSignal(
        instrument=sample_instrument,
        action=TradeAction.BUY,
        quantity=10,
        timestamp=datetime(2025, 9, 17, 9, 15, 0),
        timeframe=Timeframe("5min")
    )


@pytest.fixture
def sample_candle():
    return {
        'timestamp': datetime(2025, 9, 17, 9, 15, 0),
        'open': 100.0,
        'high': 105.0,
        'low': 98.0,
        'close': 102.0,
        'volume': 1000
    }


@pytest.fixture
def sample_historical_data(sample_candle):
    historical_data = Mock(spec=HistoricalData)
    historical_data.getCandleBy.return_value = sample_candle
    return historical_data


@pytest.fixture
def executor(mock_tradable_instrument_repository, mock_historical_data_repository):
    return BackTestTradeExecutor(
        tradable_instrument_repository=mock_tradable_instrument_repository,
        historical_data_repository=mock_historical_data_repository,
        strategy_name="test_strategy"
    )


def test_executor_initialization(executor):
    """Test that executor is properly initialized."""
    assert executor.strategy_name == "test_strategy"
    assert executor.tradable_instrument_repository is not None
    assert executor.historical_data_repository is not None


def test_execute_buy_signal_success(executor, sample_trade_signal, sample_tradable_instrument, 
                                   sample_historical_data, sample_candle,
                                   mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test successful execution of a BUY trade signal."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Add spy to tradable instrument
    sample_tradable_instrument.add_position = Mock()
    
    # Execute the trade signal
    executor.execute(sample_trade_signal)
    
    # Verify historical data repository was called correctly
    mock_historical_data_repository.get_historical_data.assert_called_once_with(
        sample_trade_signal.instrument,
        sample_trade_signal.timestamp.date(),
        sample_trade_signal.timestamp.date(),
        unittest.mock.ANY  # Timeframe object
    )
    
    # Verify candle was retrieved
    sample_historical_data.getCandleBy.assert_called_once_with(sample_trade_signal.timestamp.isoformat())
    
    # Verify add_position was called with correct parameters
    sample_tradable_instrument.add_position.assert_called_once_with(
        sample_trade_signal.timestamp, sample_candle['open'], sample_trade_signal.action, sample_trade_signal.quantity
    )
    
    # Verify tradable instrument repository was called to save
    mock_tradable_instrument_repository.save_tradable_instrument.assert_called_once_with(
        "test_strategy", sample_tradable_instrument
    )


def test_execute_sell_signal_success(executor, sample_instrument, sample_tradable_instrument, 
                                    sample_historical_data, sample_candle,
                                    mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test successful execution of a SELL trade signal."""
    # Create a SELL trade signal
    sell_signal = TradeSignal(
        instrument=sample_instrument,
        action=TradeAction.SELL,
        quantity=10,
        timestamp=datetime(2025, 9, 17, 9, 15, 0),
        timeframe=Timeframe("5min")
    )
    
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Add a spy to the tradable instrument
    sample_tradable_instrument.exit_position = Mock()
    
    # Execute the trade signal
    executor.execute(sell_signal)
    
    # Verify exit_position was called
    sample_tradable_instrument.exit_position.assert_called_once_with(
        sell_signal.timestamp, sample_candle['open'], sell_signal.action, sell_signal.quantity
    )


def test_execute_no_candle_found_raises_error(executor, sample_trade_signal, sample_tradable_instrument,
                                             mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that ValueError is raised when no candle is found for the timestamp."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    
    historical_data = Mock(spec=HistoricalData)
    historical_data.getCandleBy.return_value = None
    mock_historical_data_repository.get_historical_data.return_value = historical_data
    
    # Execute and expect ValueError
    with pytest.raises(ValueError, match=f"No candle found for timestamp {sample_trade_signal.timestamp}"):
        executor.execute(sample_trade_signal)


def test_execute_no_matching_tradable_instrument(executor, sample_trade_signal, sample_historical_data,
                                                mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test execution when no matching tradable instrument is found."""
    # Create a different instrument
    different_instrument = Instrument(InstrumentType.FUTURE, Exchange.NSE, "DIFFERENT_INSTRUMENT")
    different_tradable = TradableInstrument(different_instrument)
    
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [different_tradable]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Execute the trade signal
    executor.execute(sample_trade_signal)
    
    # Verify that save was not called since no matching instrument was found
    mock_tradable_instrument_repository.save_tradable_instrument.assert_not_called()


def test_execute_empty_tradable_instruments_list(executor, sample_trade_signal, sample_historical_data,
                                                mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test execution when tradable instruments list is empty."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Execute the trade signal
    executor.execute(sample_trade_signal)
    
    # Verify that save was not called since no instruments exist
    mock_tradable_instrument_repository.save_tradable_instrument.assert_not_called()


def test_execute_uses_correct_timeframe(executor, sample_trade_signal, sample_tradable_instrument,
                                       sample_historical_data, mock_tradable_instrument_repository,
                                       mock_historical_data_repository):
    """Test that executor uses the correct timeframe when fetching historical data."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Execute the trade signal
    executor.execute(sample_trade_signal)
    
    # Verify the timeframe used
    call_args = mock_historical_data_repository.get_historical_data.call_args
    timeframe_arg = call_args[0][3]  # Fourth argument (index 3)
    assert isinstance(timeframe_arg, Timeframe)
    assert timeframe_arg.value == "5min"


def test_execute_multiple_matching_instruments(executor, sample_trade_signal, sample_instrument,
                                              sample_historical_data, mock_tradable_instrument_repository,
                                              mock_historical_data_repository):
    """Test execution when multiple tradable instruments match."""
    # Create multiple tradable instruments with the same instrument
    tradable1 = TradableInstrument(sample_instrument)
    tradable2 = TradableInstrument(sample_instrument)
    
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable1, tradable2]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Add spies
    tradable1.add_position = Mock()
    tradable2.add_position = Mock()
    
    # Execute the trade signal
    executor.execute(sample_trade_signal)
    
    # Verify only the first matching instrument was used
    tradable1.add_position.assert_called_once()
    tradable2.add_position.assert_not_called()
    
    # Verify save was called for the first instrument only
    mock_tradable_instrument_repository.save_tradable_instrument.assert_called_once_with(
        "test_strategy", tradable1
    )


def test_execute_instrument_comparison_uses_object_equality(executor, sample_trade_signal, sample_historical_data,
                                                           mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that instrument comparison uses object equality correctly."""
    # Create an instrument with same properties but different object
    similar_instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
    similar_tradable = TradableInstrument(similar_instrument)
    
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [similar_tradable]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Add spy
    similar_tradable.add_position = Mock()
    
    # Execute the trade signal
    executor.execute(sample_trade_signal)
    
    # Verify that the instrument was matched (since they should be equal by value)
    similar_tradable.add_position.assert_called_once()
    mock_tradable_instrument_repository.save_tradable_instrument.assert_called_once_with(
        "test_strategy", similar_tradable
    )


def test_execute_with_string_actions(executor, sample_instrument, sample_tradable_instrument,
                                    sample_historical_data, mock_tradable_instrument_repository,
                                    mock_historical_data_repository):
    """Test execution with string action values (as used in the actual code)."""
    # Create trade signals with string actions (as the code checks for "buy" and "sell" strings)
    buy_signal = TradeSignal(
        instrument=sample_instrument,
        action=TradeAction.BUY,  # String instead of enum
        quantity=10,
        timestamp=datetime(2025, 9, 17, 9, 15, 0),
        timeframe=Timeframe("5min")
    )
    
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Add spy
    sample_tradable_instrument.add_position = Mock()
    
    # Execute the trade signal
    executor.execute(buy_signal)
    
    # Verify add_position was called
    sample_tradable_instrument.add_position.assert_called_once()
