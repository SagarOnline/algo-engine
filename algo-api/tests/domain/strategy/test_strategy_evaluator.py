import pytest
from datetime import datetime, date, timedelta, timezone
from unittest.mock import Mock, MagicMock, ANY, patch

from algo.domain.backtest import historical_data
from algo.domain.strategy.strategy_evaluator import StrategyEvaluator, TradeSignal, PositionAction
from algo.domain.strategy.strategy import Strategy, Instrument, Segment, Exchange, TradeAction, Type
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.strategy.tradable_instrument import TradableInstrument, TriggerType
from algo.domain.timeframe import Timeframe
from algo.domain.trading.trading_window import TradingWindow, TradingWindowType
from algo.domain.trading.trading_window_service import TradingWindowService


@pytest.fixture
def mock_strategy():
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_timeframe.return_value = "5min"
    strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013", type=Type.FUT)
    strategy.get_required_history_start_date.return_value = datetime(2025, 9, 10, 9, 15, 0)
    strategy.should_enter_trade.return_value = False
    strategy.should_exit_trade.return_value = False
    strategy.get_timeframe.return_value = Timeframe.FIVE_MINUTES
    
    # Mock position instrument
    position_instrument = Mock()
    position_instrument.action = TradeAction.BUY
    position_instrument.get_close_action.return_value = TradeAction.SELL
    strategy.get_position_instrument.return_value = position_instrument
    
    return strategy


@pytest.fixture
def mock_historical_data_repository():
    return Mock(spec=HistoricalDataRepository)


@pytest.fixture
def mock_tradable_instrument_repository():
    return Mock(spec=TradableInstrumentRepository)


@pytest.fixture
def mock_trading_window_service():
    """Real trading window service instance initialized with test data for year 2023."""
    # Test configuration data for NSE FNO segment for year 2023
    config_data = [
        {
            "exchange": "NSE",
            "segment": "FNO",
            "year": 2023,
            "default_trading_windows": [
                {
                    "effective_from": None,
                    "effective_to": None,
                    "open_time": "09:15",
                    "close_time": "15:30"
                }
            ],
            "weekly_holidays": [
                {
                    "day_of_week": "SATURDAY"
                },
                {
                    "day_of_week": "SUNDAY"
                }
            ],
            "special_days": [
            ],
            "holidays": [
            ]
        }
    ]
    
    # Create and return real TradingWindowService instance
    return TradingWindowService(config_data)


@pytest.fixture
def sample_historical_data():
    sample_data = [
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
    return HistoricalData(sample_data)


@pytest.fixture
def sample_tradable_instrument():
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013", type=Type.FUT)
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
def evaluator(mock_strategy, mock_historical_data_repository, mock_tradable_instrument_repository, mock_trading_window_service):
        return StrategyEvaluator(
            strategy=mock_strategy,
            historical_data_repository=mock_historical_data_repository,
            tradable_instrument_repository=mock_tradable_instrument_repository
        )

@pytest.fixture
def mock_trading_window_service():
    """Real trading window service instance initialized with test data for year 2023."""
    # Test configuration data for NSE FNO segment for year 2023
    config_data = [
        {
            "exchange": "NSE",
            "segment": "FNO",
            "year": 2023,
            "default_trading_windows": [
                {
                    "effective_from": None,
                    "effective_to": None,
                    "open_time": "09:15",
                    "close_time": "15:30"
                }
            ],
            "weekly_holidays": [
                {
                    "day_of_week": "SATURDAY"
                },
                {
                    "day_of_week": "SUNDAY"
                }
            ],
            "special_days": [
            ],
            "holidays": [
            ]
        }
    ]
    
    # Create and return real TradingWindowService instance
    return TradingWindowService(config_data)

@pytest.fixture
def patched_trading_window_service(mock_trading_window_service):
    with patch('algo.domain.services.get_trading_window_service', return_value=mock_trading_window_service):
        yield

def test_evaluator_initialization(evaluator, mock_strategy, mock_historical_data_repository, mock_tradable_instrument_repository):
    """Test that evaluator is properly initialized."""
    assert evaluator.strategy == mock_strategy
    assert evaluator.historical_data_repository == mock_historical_data_repository
    assert evaluator.tradable_instrument_repository == mock_tradable_instrument_repository


def test_evaluate_no_tradable_instruments_returns_empty_list(evaluator, sample_candle, sample_historical_data,
                                                      mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test evaluate returns empty list when no tradable instruments exist."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert result == []


def test_evaluate_no_entry_or_exit_signals_returns_empty_list(evaluator, sample_candle, sample_historical_data,
                                                       sample_tradable_instrument, mock_strategy,
                                                       mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test evaluate returns empty list when no entry or exit signals are generated."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = False
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert result == []


def test_evaluate_entry_signal_generated(evaluator, sample_candle, sample_historical_data,
                                        sample_tradable_instrument, mock_strategy,
                                        mock_tradable_instrument_repository, mock_historical_data_repository,
                                        patched_trading_window_service):
    """Test evaluate returns list with TradeSignal when entry condition is met."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = True
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert isinstance(result, list)
    assert len(result) == 1
    signal = result[0]
    assert isinstance(signal, TradeSignal)
    assert signal.instrument == sample_tradable_instrument.instrument
    assert signal.action == TradeAction.BUY
    assert signal.position_action == PositionAction.ADD
    assert signal.quantity == 1
    assert signal.timeframe == Timeframe.FIVE_MINUTES
    assert signal.trigger_type == TriggerType.ENTRY_RULES


def test_evaluate_exit_signal_generated(evaluator, sample_candle, sample_historical_data,
                                       mock_strategy, patched_trading_window_service,
                                       mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test evaluate returns list with TradeSignal when exit condition is met."""
     # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add an open position with stop loss
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=None)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]

    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_exit_trade.return_value = True
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert isinstance(result, list)
    assert len(result) == 1
    signal = result[0]
    assert isinstance(signal, TradeSignal)
    assert signal.instrument == tradable.instrument
    assert signal.action == TradeAction.SELL
    assert signal.position_action == PositionAction.EXIT
    assert signal.quantity == 1
    assert signal.timeframe == Timeframe.FIVE_MINUTES
    assert signal.trigger_type == TriggerType.EXIT_RULES


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
        mock_strategy.get_required_history_start_date().date(),
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


def test_evaluate_multiple_tradable_instruments_returns_all_signals(evaluator, sample_candle, sample_historical_data,
                                                                    mock_strategy, patched_trading_window_service, mock_tradable_instrument_repository,
                                                                    mock_historical_data_repository):
    """Test that evaluate returns signals from all matching tradable instruments."""
    # Create multiple tradable instruments
    instrument1 = Instrument(Segment.FNO, Exchange.NSE, "INSTRUMENT1", type=Type.FUT)
    instrument2 = Instrument(Segment.FNO, Exchange.NSE, "INSTRUMENT2", type=Type.FUT)
    
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
    
    # Verify signals from both instruments are returned
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0].instrument == instrument1
    assert result[1].instrument == instrument2


def test_evaluate_position_open_but_no_exit_signal_returns_empty_list(evaluator, sample_candle, sample_historical_data,
                                                              mock_strategy,
                                                              mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that evaluate returns empty list when position is open but no exit signal."""
    
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add an open position with stop loss
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=None)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_exit_trade.return_value = False
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify
    assert result == []


def test_get_historical_data_calls_strategy_methods(evaluator, mock_strategy, mock_historical_data_repository):
    """Test that _get_historical_data calls strategy methods correctly."""
    # Setup
    end_date = datetime(2025, 9, 17, 9, 15, 0)
    mock_historical_data = HistoricalData([])
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
    assert result == mock_historical_data.data


def test_trade_signal_creation_with_timestamp(evaluator, sample_candle, sample_historical_data,
                                             sample_tradable_instrument, mock_strategy,patched_trading_window_service,
                                             mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test that TradeSignal is created with correct timestamp."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = True
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify TradeSignal has timestamp and timeframe
    assert result, "Result is  not an empty list"
    assert hasattr(result[0], 'timestamp')
    assert result[0].timestamp is not None
    assert hasattr(result[0], 'timeframe')
    assert result[0].timeframe == Timeframe.FIVE_MINUTES


def test_evaluate_handles_empty_historical_data(evaluator, sample_candle, sample_tradable_instrument,
                                               mock_strategy, mock_tradable_instrument_repository,
                                               mock_historical_data_repository):
    """Test that evaluate handles empty historical data gracefully."""
    # Setup mocks with empty historical data
    empty_historical_data = HistoricalData([])
    
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [sample_tradable_instrument]
    mock_historical_data_repository.get_historical_data.return_value = empty_historical_data
    sample_tradable_instrument.is_any_position_open.return_value = False
    
    # Execute - should not raise exception
    result = evaluator.evaluate(sample_candle)
    
    # Verify strategy was called with empty data
    mock_strategy.should_enter_trade.assert_called_once_with([])
    
    # Result can be None or a signal depending on strategy logic
    assert result == [] or (isinstance(result, list) and all(isinstance(item, TradeSignal) for item in result)), \
    "Result must be an empty list or a list of TradeSignal objects"


def test_evaluate_entry_and_exit_priority(evaluator, sample_candle, sample_historical_data,
                                         sample_tradable_instrument, mock_strategy,patched_trading_window_service,
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
    assert result, "Result is not an empty list"
    assert result[0].action == TradeAction.BUY  # Entry action


def test_evaluate_stop_loss_hit_generates_stop_loss_signal(evaluator, sample_candle, sample_historical_data,
                                                          mock_strategy, patched_trading_window_service,mock_tradable_instrument_repository,
                                                          mock_historical_data_repository):
    """Test that evaluate generates stop loss signal when position hits stop loss."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Create a tradable instrument with an open position that will hit stop loss
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add an open position with stop loss
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=95.0)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    # Set candle close price below stop loss to trigger it
    test_candle = sample_candle.copy()
    test_candle['close'] = 94.0  # Below stop loss of 95.0
    
    # Execute
    result = evaluator.evaluate(test_candle)
    
    # Verify stop loss signal is generated
    assert isinstance(result, list)
    assert len(result) == 1
    signal = result[0]
    assert isinstance(signal, TradeSignal)
    assert signal.trigger_type == TriggerType.STOP_LOSS
    assert signal.position_action == PositionAction.EXIT
    assert signal.action == TradeAction.SELL
    assert signal.quantity == 1
    assert signal.instrument == instrument


def test_evaluate_stop_loss_not_hit_no_signal_generated(evaluator, sample_candle, sample_historical_data,
                                                       mock_strategy, mock_tradable_instrument_repository,
                                                       mock_historical_data_repository):
    """Test that evaluate does not generate stop loss signal when stop loss is not hit."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = False
    
    # Create a tradable instrument with an open position
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add an open position with stop loss
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=95.0)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    # Set candle close price above stop loss (no trigger)
    test_candle = sample_candle.copy()
    test_candle['close'] = 98.0  # Above stop loss of 95.0
    
    # Execute
    result = evaluator.evaluate(test_candle)
    
    # Verify no signals are generated
    assert result == []


def test_evaluate_stop_loss_multiple_positions_multiple_signals(evaluator, sample_candle, sample_historical_data,
                                                               mock_strategy, patched_trading_window_service,mock_tradable_instrument_repository,
                                                               mock_historical_data_repository):
    """Test that evaluate generates multiple stop loss signals when multiple positions hit stop loss."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Create a tradable instrument with multiple open positions
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add multiple open positions with different stop losses
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=95.0)
    tradable.add_position(datetime(2025, 9, 17, 9, 5), 110.0, TradeAction.BUY, 2, stop_loss=105.0)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    # Set candle close price that triggers both stop losses
    test_candle = sample_candle.copy()
    test_candle['close'] = 90.0  # Below both stop losses
    
    # Execute
    result = evaluator.evaluate(test_candle)
    
    # Verify multiple stop loss signals are generated
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Check both signals are stop loss signals
    for signal in result:
        assert signal.trigger_type == TriggerType.STOP_LOSS
        assert signal.position_action == PositionAction.EXIT
        assert signal.action == TradeAction.SELL


def test_evaluate_stop_loss_priority_over_entry_rules(evaluator, sample_candle, sample_historical_data,
                                                     mock_strategy,patched_trading_window_service, mock_tradable_instrument_repository,
                                                     mock_historical_data_repository):
    """Test that stop loss signals take priority over entry rule signals."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = True  # Entry condition is met
    mock_strategy.should_exit_trade.return_value = False
    
    # Create a tradable instrument with an open position
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add an open position with stop loss
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=95.0)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    # Set candle close price that triggers stop loss
    test_candle = sample_candle.copy()
    test_candle['close'] = 94.0  # Below stop loss
    
    # Execute
    result = evaluator.evaluate(test_candle)
    
    # Verify only stop loss signal is generated (not entry signal)
    assert isinstance(result, list)
    assert len(result) == 1
    signal = result[0]
    assert signal.trigger_type == TriggerType.STOP_LOSS
    assert signal.position_action == PositionAction.EXIT


def test_evaluate_stop_loss_priority_over_exit_rules(evaluator, sample_candle, sample_historical_data,
                                                    mock_strategy,patched_trading_window_service, mock_tradable_instrument_repository,
                                                    mock_historical_data_repository):
    """Test that stop loss signals take priority over exit rule signals."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = True  # Exit condition is met
    
    # Create a tradable instrument with an open position
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add an open position with stop loss
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=95.0)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    # Set candle close price that triggers stop loss
    test_candle = sample_candle.copy()
    test_candle['close'] = 94.0  # Below stop loss
    
    # Execute
    result = evaluator.evaluate(test_candle)
    
    # Verify only stop loss signal is generated (not exit rule signal)
    assert isinstance(result, list)
    assert len(result) == 1
    signal = result[0]
    assert signal.trigger_type == TriggerType.STOP_LOSS
    assert signal.position_action == PositionAction.EXIT


def test_evaluate_stop_loss_short_position(evaluator, sample_candle, sample_historical_data,
                                          mock_strategy, patched_trading_window_service,mock_tradable_instrument_repository,
                                          mock_historical_data_repository):
    """Test that evaluate correctly handles stop loss for SHORT positions."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Create a tradable instrument with a SHORT position
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add a SHORT position with stop loss (stop loss triggers when price goes up)
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.SELL, 1, stop_loss=5.0)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    # Set candle close price above stop loss to trigger it for SHORT position
    test_candle = sample_candle.copy()
    test_candle['close'] = 106.0  # Above stop loss of 105.0
    
    # Execute
    result = evaluator.evaluate(test_candle)
    
    # Verify stop loss signal is generated for SHORT position
    assert isinstance(result, list)
    assert len(result) == 1
    signal = result[0]
    assert signal.trigger_type == TriggerType.STOP_LOSS
    assert signal.position_action == PositionAction.EXIT
    assert signal.action == TradeAction.SELL  # Close action for SHORT position
    assert signal.quantity == 1


def test_evaluate_stop_loss_no_open_positions(evaluator, sample_candle, sample_historical_data,
                                             mock_strategy, mock_tradable_instrument_repository,
                                             mock_historical_data_repository):
    """Test that evaluate handles tradables with no open positions correctly."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = False
    
    # Create a tradable instrument with no positions
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    # Execute
    result = evaluator.evaluate(sample_candle)
    
    # Verify no signals are generated
    assert result == []


def test_evaluate_stop_loss_position_without_stop_loss(evaluator, sample_candle, sample_historical_data,
                                                      mock_strategy, mock_tradable_instrument_repository,
                                                      mock_historical_data_repository):
    """Test that evaluate handles positions without stop loss correctly."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = False
    
    # Create a tradable instrument with an open position but no stop loss
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add position without stop loss (stop_loss=None)
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=None)
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = [tradable]
    
    # Set any candle price
    test_candle = sample_candle.copy()
    test_candle['close'] = 50.0  # Very low price, but no stop loss set
    
    # Execute
    result = evaluator.evaluate(test_candle)
    
    # Verify no stop loss signals are generated
    assert result == []


def test_evaluate_for_stop_loss_method_isolated(evaluator, sample_candle, patched_trading_window_service):
    """Test the _evaluate_for_stop_loss method in isolation."""
    # Create a tradable instrument with an open position
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add an open position with stop loss
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.BUY, 1, stop_loss=95.0)
    
    # Set candle close price to trigger stop loss
    test_candle = sample_candle.copy()
    test_candle['close'] = 94.0
    
    # Execute the isolated method
    result = evaluator._evaluate_for_stop_loss(test_candle, Timeframe.FIVE_MINUTES, tradable)
    
    # Verify the result
    assert isinstance(result, list)
    assert len(result) == 1
    signal = result[0]
    assert signal.trigger_type == TriggerType.STOP_LOSS
    assert signal.position_action == PositionAction.EXIT
    assert signal.quantity == 1


# Tests for _get_next_candle_timestamp method

@patch('algo.domain.services.get_trading_window_service')
def test_get_next_candle_timestamp_intraday_within_trading_hours(mock_get_service):
    """Test that next candle timestamp is calculated correctly within trading hours and preserves timezone"""
    # Setup mock trading window service
    mock_service = Mock()
    
    def get_trading_window(target_date, exchange, segment):
        return TradingWindow(
            date=target_date,
            exchange=Exchange(exchange) if isinstance(exchange, str) else exchange,
            segment=Segment(segment) if isinstance(segment, str) else segment,
            window_type=TradingWindowType.DEFAULT,
            open_time=datetime.strptime("09:15", "%H:%M").time(),
            close_time=datetime.strptime("15:30", "%H:%M").time(),
            description="Regular trading day"
        )
    
    mock_service.get_trading_window.side_effect = get_trading_window
    mock_get_service.return_value = mock_service
    
    # Create evaluator with mock strategy
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test 5-minute timeframe within trading hours with IST timezone
    ist = timezone(timedelta(hours=5, minutes=30))
    current_time = datetime(2023, 10, 9, 10, 30, tzinfo=ist)  # Monday 10:30 AM IST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.FIVE_MINUTES)
    expected_time = datetime(2023, 10, 9, 10, 35, tzinfo=ist)  # 10:35 AM IST
    assert next_time == expected_time
    assert next_time.tzinfo == ist



def test_get_next_candle_timestamp_last_candle_of_day(patched_trading_window_service):
    """Test that next candle timestamp moves to next trading day at 9:15 AM when current is last candle and preserves timezone"""
    # Create evaluator with mock strategy
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test 5-minute timeframe at 3:25 PM (last candle before 3:30 PM close) with UTC timezone
    current_time = datetime(2023, 10, 9, 15, 25, tzinfo=timezone.utc)  # Monday 3:25 PM UTC
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.FIVE_MINUTES)
    expected_time = datetime(2023, 10, 10, 9, 15, tzinfo=timezone.utc)  # Tuesday 9:15 AM UTC
    assert next_time == expected_time
    assert next_time.tzinfo == timezone.utc


@patch('algo.domain.services.get_trading_window_service')
def test_get_next_candle_timestamp_after_trading_hours(mock_get_service):
    """Test that timestamps after trading hours move to next trading day and preserve timezone"""
    # Setup mock trading window service
    mock_service = Mock()
    
    def get_trading_window(target_date, exchange, segment):
        return TradingWindow(
            date=target_date,
            exchange=Exchange(exchange) if isinstance(exchange, str) else exchange,
            segment=Segment(segment) if isinstance(segment, str) else segment,
            window_type=TradingWindowType.DEFAULT,
            open_time=datetime.strptime("09:15", "%H:%M").time(),
            close_time=datetime.strptime("15:30", "%H:%M").time(),
            description="Regular trading day"
        )
    
    mock_service.get_trading_window.side_effect = get_trading_window
    mock_get_service.return_value = mock_service
    
    # Create evaluator with mock strategy
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test timestamp at 4:00 PM (after market close) with UTC timezone
    current_time = datetime(2023, 10, 9, 16, 0, tzinfo=timezone.utc)  # Monday 4:00 PM UTC
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.ONE_MINUTE)
    expected_time = datetime(2023, 10, 10, 9, 15, tzinfo=timezone.utc)  # Tuesday 9:15 AM UTC
    assert next_time == expected_time
    assert next_time.tzinfo == timezone.utc



def test_get_next_candle_timestamp_friday_to_monday(patched_trading_window_service):
    """Test that Friday's last candle moves to Monday 9:15 AM (skipping weekend) and preserves timezone"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test Friday 3:25 PM (last candle) with UTC timezone
    current_time = datetime(2023, 10, 6, 15, 25, tzinfo=timezone.utc)  # Friday 3:25 PM UTC
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.FIVE_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=timezone.utc)  # Monday 9:15 AM UTC
    assert next_time == expected_time
    assert next_time.tzinfo == timezone.utc


def test_get_next_candle_timestamp_weekend_to_monday(patched_trading_window_service):
    """Test that weekend timestamps move to Monday 9:15 AM and preserve timezone"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test Saturday timestamp with EST timezone
    est = timezone(timedelta(hours=-5))
    current_time = datetime(2023, 10, 7, 12, 0, tzinfo=est)  # Saturday 12:00 PM EST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.FIVE_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=est)  # Monday 9:15 AM EST
    assert next_time == expected_time
    assert next_time.tzinfo == est
    
    # Test Sunday timestamp with PST timezone
    pst = timezone(timedelta(hours=-8))
    current_time = datetime(2023, 10, 8, 14, 30, tzinfo=pst)  # Sunday 2:30 PM PST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.FIFTEEN_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=pst)  # Monday 9:15 AM PST
    assert next_time == expected_time
    assert next_time.tzinfo == pst


def test_get_next_candle_timestamp_daily_timeframe(patched_trading_window_service):
    """Test daily timeframe moves to next trading day at 9:15 AM and preserves timezone"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test Monday to Tuesday with IST timezone
    ist = timezone(timedelta(hours=5, minutes=30))
    current_time = datetime(2023, 10, 9, 15, 30, tzinfo=ist)  # Monday market close IST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.ONE_DAY)
    expected_time = datetime(2023, 10, 10, 9, 15, tzinfo=ist)  # Tuesday 9:15 AM IST
    assert next_time == expected_time
    assert next_time.tzinfo == ist
    
    # Test Friday to Monday (skip weekend) with UTC timezone
    utc_time = datetime(2023, 10, 6, 15, 30, tzinfo=timezone.utc)  # Friday market close UTC
    next_time = evaluator._get_next_candle_timestamp(utc_time, Timeframe.ONE_DAY)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=timezone.utc)  # Monday 9:15 AM UTC
    assert next_time == expected_time
    assert next_time.tzinfo == timezone.utc


def test_get_next_candle_timestamp_weekly_timeframe(patched_trading_window_service):
    """Test weekly timeframe moves to next week's first trading day at 9:15 AM and preserves timezone"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test current week Monday to next week Monday with JST timezone
    jst = timezone(timedelta(hours=9))
    current_time = datetime(2023, 10, 9, 9, 15, tzinfo=jst)  # Monday market close JST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.ONE_WEEK)
    expected_time = datetime(2023, 10, 16, 9, 15, tzinfo=jst)  # Next Monday 9:15 AM JST
    assert next_time == expected_time
    assert next_time.tzinfo == jst
    
    # Test current week Friday to next week Monday with custom timezone
    custom_tz = timezone(timedelta(hours=-3))
    current_time = datetime(2023, 10, 6, 9, 15, tzinfo=custom_tz)  # Friday market close
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.ONE_WEEK)
    expected_time = datetime(2023, 10, 13, 9, 15, tzinfo=custom_tz)  # Next Friday 9:15 AM (one week later)
    assert next_time == expected_time
    assert next_time.tzinfo == custom_tz


def test_get_next_candle_timestamp_different_minute_timeframes(patched_trading_window_service):
    """Test different minute-based timeframes and timezone preservation"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test 1-minute timeframe within trading hours with UTC timezone
    current_time = datetime(2023, 10, 9, 10, 30, tzinfo=timezone.utc)  # Monday 10:30 AM UTC
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.ONE_MINUTE)
    expected_time = datetime(2023, 10, 9, 10, 31, tzinfo=timezone.utc)  # 10:31 AM UTC
    assert next_time == expected_time
    assert next_time.tzinfo == timezone.utc
    
    # Test 30-minute timeframe within trading hours with IST timezone
    ist = timezone(timedelta(hours=5, minutes=30))
    current_time = datetime(2023, 10, 9, 14, 0, tzinfo=ist)  # Monday 2:00 PM IST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.THIRTY_MINUTES)
    expected_time = datetime(2023, 10, 9, 14, 30, tzinfo=ist)  # 2:30 PM IST
    assert next_time == expected_time
    assert next_time.tzinfo == ist
    
    # Test 60-minute timeframe within trading hours with EST timezone
    est = timezone(timedelta(hours=-5))
    current_time = datetime(2023, 10, 9, 13, 0, tzinfo=est)  # Monday 1:00 PM EST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.SIXTY_MINUTES)
    expected_time = datetime(2023, 10, 9, 14, 0, tzinfo=est)  # 2:00 PM EST
    assert next_time == expected_time
    assert next_time.tzinfo == est


def test_get_next_candle_timestamp_exactly_at_market_close(patched_trading_window_service):
    """Test timestamp exactly at market close time (3:30 PM) and timezone preservation"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test exactly at 3:30 PM with IST timezone
    ist = timezone(timedelta(hours=5, minutes=30))
    current_time = datetime(2023, 10, 9, 15, 30, tzinfo=ist)  # Monday 3:30 PM IST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.ONE_MINUTE)
    expected_time = datetime(2023, 10, 10, 9, 15, tzinfo=ist)  # Tuesday 9:15 AM IST
    assert next_time == expected_time
    assert next_time.tzinfo == ist
    
    # Test exactly at 3:30 PM with UTC timezone
    utc_time = datetime(2023, 10, 9, 15, 30, tzinfo=timezone.utc)  # Monday 3:30 PM UTC
    next_time = evaluator._get_next_candle_timestamp(utc_time, Timeframe.ONE_MINUTE)
    expected_time = datetime(2023, 10, 10, 9, 15, tzinfo=timezone.utc)  # Tuesday 9:15 AM UTC
    assert next_time == expected_time
    assert next_time.tzinfo == timezone.utc


def test_get_next_candle_timestamp_early_morning(patched_trading_window_service):
    """Test timestamps in early morning within trading hours and timezone preservation"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Test at 9:15 AM (market open) with EST timezone
    est = timezone(timedelta(hours=-5))
    current_time = datetime(2023, 10, 9, 9, 15, tzinfo=est)  # Monday 9:15 AM EST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.FIVE_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 20, tzinfo=est)  # 9:20 AM EST
    assert next_time == expected_time
    assert next_time.tzinfo == est
    
    # Test at 9:20 AM with JST timezone
    jst = timezone(timedelta(hours=9))
    current_time = datetime(2023, 10, 9, 9, 20, tzinfo=jst)  # Monday 9:20 AM JST
    next_time = evaluator._get_next_candle_timestamp(current_time, Timeframe.FIFTEEN_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 35, tzinfo=jst)  # 9:35 AM JST
    assert next_time == expected_time
    assert next_time.tzinfo == jst


def test_get_next_candle_timestamp_weekend_during_trading_hours(patched_trading_window_service):
    """Test that weekend timestamps during trading hours move to Monday 9:15 AM and preserve timezone"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Saturday 11:00 AM (during what would be trading hours) with UTC timezone
    saturday_timestamp = datetime(2023, 10, 7, 11, 0, tzinfo=timezone.utc)  # Saturday UTC
    next_time = evaluator._get_next_candle_timestamp(saturday_timestamp, Timeframe.FIVE_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=timezone.utc)  # Monday 9:15 AM UTC
    assert next_time == expected_time
    assert next_time.tzinfo == timezone.utc
    
    # Sunday 2:00 PM (during what would be trading hours) with Pacific timezone
    pacific = timezone(timedelta(hours=-8))
    sunday_timestamp = datetime(2023, 10, 8, 14, 0, tzinfo=pacific)  # Sunday PST
    next_time = evaluator._get_next_candle_timestamp(sunday_timestamp, Timeframe.ONE_MINUTE)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=pacific)  # Monday 9:15 AM PST
    assert next_time == expected_time
    assert next_time.tzinfo == pacific


def test_get_next_candle_timestamp_friday_crossing_to_weekend(patched_trading_window_service):
    """Test that Friday timestamps that would result in weekend move to Monday and preserve timezone"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Friday 3:25 PM + 5 minutes = Friday 3:30 PM (end of trading) with IST timezone
    ist = timezone(timedelta(hours=5, minutes=30))
    friday_timestamp = datetime(2023, 10, 6, 15, 25, tzinfo=ist)  # Friday IST
    next_time = evaluator._get_next_candle_timestamp(friday_timestamp, Timeframe.FIVE_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=ist)  # Monday 9:15 AM IST
    assert next_time == expected_time
    assert next_time.tzinfo == ist
    
    # Friday with timezone crossing to Monday
    mountain = timezone(timedelta(hours=-7))
    friday_timestamp = datetime(2023, 10, 6, 15, 25, tzinfo=mountain)  # Friday MST
    next_time = evaluator._get_next_candle_timestamp(friday_timestamp, Timeframe.FIVE_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=mountain)  # Monday 9:15 AM MST
    assert next_time == expected_time
    assert next_time.tzinfo == mountain


def test_get_next_candle_timestamp_weekend_after_hours(patched_trading_window_service):
    """Test that weekend timestamps after trading hours move to Monday 9:15 AM and preserve timezone"""
    mock_strategy = Mock()
    mock_strategy.get_instrument.return_value = Instrument(Segment.FNO, Exchange.NSE, "TEST")
    evaluator = StrategyEvaluator(mock_strategy, Mock(), Mock())
    
    # Saturday 6:00 PM (after trading hours) with JST timezone
    jst = timezone(timedelta(hours=9))
    saturday_timestamp = datetime(2023, 10, 7, 18, 0, tzinfo=jst)  # Saturday JST
    next_time = evaluator._get_next_candle_timestamp(saturday_timestamp, Timeframe.FIFTEEN_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=jst)  # Monday 9:15 AM JST
    assert next_time == expected_time
    assert next_time.tzinfo == jst
    
    # Saturday 6:00 PM with Central timezone
    central = timezone(timedelta(hours=-6))
    saturday_timestamp = datetime(2023, 10, 7, 18, 0, tzinfo=central)  # Saturday CST
    next_time = evaluator._get_next_candle_timestamp(saturday_timestamp, Timeframe.FIFTEEN_MINUTES)
    expected_time = datetime(2023, 10, 9, 9, 15, tzinfo=central)  # Monday 9:15 AM CST
    assert next_time == expected_time
    assert next_time.tzinfo == central


# Remove the separate timezone tests since they are now integrated into existing tests
