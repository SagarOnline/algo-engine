import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock, ANY

from algo.domain.strategy.strategy_evaluator import StrategyEvaluator, TradeSignal
from algo.domain.strategy.strategy import Strategy, Instrument, InstrumentType, Exchange, PositionAction
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.backtest.report import TradableInstrument
from algo.domain.timeframe import Timeframe


@pytest.fixture
def mock_strategy():
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_timeframe.return_value = "5min"
    strategy.get_instrument.return_value = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
    strategy.get_required_history_start_date.return_value = date(2025, 9, 10)
    strategy.should_enter_trade.return_value = False
    strategy.should_exit_trade.return_value = False
    strategy.get_timeframe.return_value = Timeframe.FIVE_MINUTES
    
    # Mock position instrument
    position_instrument = Mock()
    position_instrument.action = PositionAction.BUY
    position_instrument.get_close_action.return_value = PositionAction.SELL
    strategy.get_position_instrument.return_value = position_instrument
    
    return strategy


@pytest.fixture
def mock_historical_data_repository():
    return Mock(spec=HistoricalDataRepository)


@pytest.fixture
def mock_tradable_instrument_repository():
    return Mock(spec=TradableInstrumentRepository)


@pytest.fixture
def sample_historical_data():
    historical_data = Mock(spec=HistoricalData)
    historical_data.data = [
        {
            'timestamp': datetime(2025, 9, 17, 9, 0, 0),
            'open': 100.0,
            'high': 105.0,
            'low': 98.0,
            'close': 102.0,
            'volume': 1000
        },
        {
            'timestamp': datetime(2025, 9, 17, 9, 5, 0),
            'open': 102.0,
            'high': 108.0,
            'low': 101.0,
            'close': 106.0,
            'volume': 1200
        }
    ]
    return historical_data


@pytest.fixture
def sample_tradable_instrument():
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
    tradable = Mock(spec=TradableInstrument)
    tradable.instrument = instrument
    tradable.is_any_position_open.return_value = False
    return tradable


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
def evaluator(mock_strategy, mock_historical_data_repository, mock_tradable_instrument_repository):
    return StrategyEvaluator(
        strategy=mock_strategy,
        historical_data_repository=mock_historical_data_repository,
        tradable_instrument_repository=mock_tradable_instrument_repository
    )


def test_evaluator_initialization(evaluator, mock_strategy, mock_historical_data_repository, mock_tradable_instrument_repository):
    """Test that evaluator is properly initialized."""
    assert evaluator.strategy == mock_strategy
    assert evaluator.historical_data_repository == mock_historical_data_repository
    assert evaluator.tradable_instrument_repository == mock_tradable_instrument_repository


def test_evaluate_no_tradable_instruments_returns_none(evaluator, sample_candle, sample_historical_data,
                                                      mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test evaluate returns None when no tradable instruments exist."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert result is None


def test_evaluate_no_entry_or_exit_signals_returns_none(evaluator, sample_candle, sample_historical_data,
                                                       sample_tradable_instrument, mock_strategy,
                                                       mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test evaluate returns None when no entry or exit signals are generated."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = False
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert result is None


def test_evaluate_entry_signal_generated(evaluator, sample_candle, sample_historical_data,
                                        sample_tradable_instrument, mock_strategy,
                                        mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test evaluate returns TradeSignal when entry condition is met."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = True
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert result is not None
    assert isinstance(result, TradeSignal)
    assert result.instrument == sample_tradable_instrument.instrument
    assert result.action == PositionAction.BUY
    assert result.quantity == 1


def test_evaluate_exit_signal_generated(evaluator, sample_candle, sample_historical_data,
                                       sample_tradable_instrument, mock_strategy,
                                       mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test evaluate returns TradeSignal when exit condition is met."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_exit_trade.return_value = True
    sample_tradable_instrument.is_any_position_open.return_value = True
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert result is not None
    assert isinstance(result, TradeSignal)
    assert result.instrument == sample_tradable_instrument.instrument
    assert result.action == PositionAction.SELL
    assert result.quantity == 1


def test_evaluate_calls_strategy_methods_correctly(evaluator, sample_candle, sample_historical_data,
                                                  sample_tradable_instrument, mock_strategy,
                                                  mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that evaluate calls strategy methods with correct parameters."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute
    evaluator.evaluate(sample_candle)
    
    # Verify strategy methods were called correctly
    mock_strategy.should_enter_trade.assert_called_once_with(sample_historical_data.data)


def test_evaluate_calls_historical_data_repository_correctly(evaluator, sample_candle, sample_historical_data,
                                                           sample_tradable_instrument, mock_strategy,
                                                           mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that evaluate calls historical data repository with correct parameters."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Execute
    evaluator.evaluate(sample_candle)
    
    # Verify historical data repository was called correctly
    mock_historical_data_repository.get_historical_data.assert_called_once_with(
        mock_strategy.get_instrument.return_value,
        mock_strategy.get_required_history_start_date.return_value,
        sample_candle['timestamp'].date(),
        ANY  # Timeframe object
    )


def test_evaluate_calls_tradable_instrument_repository_correctly(evaluator, sample_candle, sample_historical_data,
                                                               sample_tradable_instrument, mock_strategy,
                                                               mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that evaluate calls tradable instrument repository with correct parameters."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Execute
    evaluator.evaluate(sample_candle)
    
    # Verify tradable instrument repository was called correctly
    mock_tradable_instrument_repository.get_tradable_instruments.assert_called_once_with("test_strategy")


def test_evaluate_multiple_tradable_instruments_returns_first_signal(evaluator, sample_candle, sample_historical_data,
                                                                    mock_strategy, mock_tradable_instrument_repository,
                                                                    mock_historical_data_repository):
    """Test that evaluate returns signal from first matching tradable instrument."""
    # Create multiple tradable instruments
    instrument1 = Instrument(InstrumentType.STOCK, Exchange.NSE, "INSTRUMENT1")
    instrument2 = Instrument(InstrumentType.STOCK, Exchange.NSE, "INSTRUMENT2")
    
    tradable1 = Mock(spec=TradableInstrument)
    tradable1.instrument = instrument1
    tradable1.is_any_position_open.return_value = False
    
    tradable2 = Mock(spec=TradableInstrument)
    tradable2.instrument = instrument2
    tradable2.is_any_position_open.return_value = False
    
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable1, tradable2]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = True
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify first instrument's signal is returned
    assert result is not None
    assert result.instrument == instrument1


def test_evaluate_position_open_but_no_exit_signal_returns_none(evaluator, sample_candle, sample_historical_data,
                                                              sample_tradable_instrument, mock_strategy,
                                                              mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that evaluate returns None when position is open but no exit signal."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_exit_trade.return_value = False
    sample_tradable_instrument.is_any_position_open.return_value = True
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert result is None


def test_get_historical_data_calls_strategy_methods(evaluator, mock_strategy, mock_historical_data_repository):
    """Test that _get_historical_data calls strategy methods correctly."""
    # Setup
    end_date = date(2025, 9, 17)
    mock_historical_data = Mock(spec=HistoricalData)
    mock_historical_data_repository.get_historical_data.return_value = mock_historical_data
    
    # Execute
    result = evaluator._get_historical_data(mock_strategy, end_date)
    
    # Verify strategy methods were called
    mock_strategy.get_instrument.assert_called_once()
    mock_strategy.get_timeframe.assert_called_once()
    mock_strategy.get_required_history_start_date.assert_called_once_with(end_date)
    
    # Verify historical data repository was called
    mock_historical_data_repository.get_historical_data.assert_called_once()
    
    # Verify result
    assert result == mock_historical_data


def test_trade_signal_creation_with_timestamp(evaluator, sample_candle, sample_historical_data,
                                             sample_tradable_instrument, mock_strategy,
                                             mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that TradeSignal is created with correct timestamp."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = True
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify TradeSignal has timestamp
    assert result is not None
    assert hasattr(result, 'timestamp')
    assert result.timestamp is not None


def test_evaluate_handles_empty_historical_data(evaluator, sample_candle, sample_tradable_instrument,
                                               mock_strategy, mock_tradable_instrument_repository,
                                               mock_historical_data_repository):
    """Test that evaluate handles empty historical data gracefully."""
    # Setup mocks with empty historical data
    empty_historical_data = Mock(spec=HistoricalData)
    empty_historical_data.data = []
    
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = empty_historical_data
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute - should not raise exception
    result = evaluator.evaluate(sample_candle)
    
    # Verify strategy was called with empty data
    mock_strategy.should_enter_trade.assert_called_once_with([])
    
    # Result can be None or a signal depending on strategy logic
    assert result is None or isinstance(result, TradeSignal)


def test_evaluate_entry_and_exit_priority(evaluator, sample_candle, sample_historical_data,
                                         sample_tradable_instrument, mock_strategy,
                                         mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that entry signals take priority when position is closed."""
    # Setup mocks - both entry and exit conditions true, but position is closed
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = True
    mock_strategy.should_exit_trade.return_value = True
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify entry signal is returned (not exit signal)
    assert result is not None
    assert result.action == PositionAction.BUY  # Entry action
