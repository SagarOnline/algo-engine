import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, MagicMock, ANY

from algo.domain.strategy.strategy_evaluator import StrategyEvaluator, TradeSignal, PositionAction
from algo.domain.strategy.strategy import Strategy, Instrument, InstrumentType, Exchange, TradeAction
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.strategy.tradable_instrument import TradableInstrument, TriggerType
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
                                        mock_tradable_instrument_repository, mock_historical_data_repository):
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
                                       mock_strategy,
                                       mock_tradable_instrument_repository, mock_historical_data_repository):
    """Test evaluate returns list with TradeSignal when exit condition is met."""
     # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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


def test_evaluate_multiple_tradable_instruments_returns_all_signals(evaluator, sample_candle, sample_historical_data,
                                                                    mock_strategy, mock_tradable_instrument_repository,
                                                                    mock_historical_data_repository):
    """Test that evaluate returns signals from all matching tradable instruments."""
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
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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
    assert result == [] or (isinstance(result, list) and all(isinstance(item, TradeSignal) for item in result)), \
    "Result must be an empty list or a list of TradeSignal objects"


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
    assert result, "Result is not an empty list"
    assert result[0].action == TradeAction.BUY  # Entry action


def test_evaluate_stop_loss_hit_generates_stop_loss_signal(evaluator, sample_candle, sample_historical_data,
                                                          mock_strategy, mock_tradable_instrument_repository,
                                                          mock_historical_data_repository):
    """Test that evaluate generates stop loss signal when position hits stop loss."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Create a tradable instrument with an open position that will hit stop loss
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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
                                                               mock_strategy, mock_tradable_instrument_repository,
                                                               mock_historical_data_repository):
    """Test that evaluate generates multiple stop loss signals when multiple positions hit stop loss."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Create a tradable instrument with multiple open positions
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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
                                                     mock_strategy, mock_tradable_instrument_repository,
                                                     mock_historical_data_repository):
    """Test that stop loss signals take priority over entry rule signals."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = True  # Entry condition is met
    mock_strategy.should_exit_trade.return_value = False
    
    # Create a tradable instrument with an open position
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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
                                                    mock_strategy, mock_tradable_instrument_repository,
                                                    mock_historical_data_repository):
    """Test that stop loss signals take priority over exit rule signals."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    mock_strategy.should_enter_trade.return_value = False
    mock_strategy.should_exit_trade.return_value = True  # Exit condition is met
    
    # Create a tradable instrument with an open position
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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
                                          mock_strategy, mock_tradable_instrument_repository,
                                          mock_historical_data_repository):
    """Test that evaluate correctly handles stop loss for SHORT positions."""
    # Setup mocks
    mock_tradable_instrument_repository.get_tradable_instruments.return_value = []
    mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
    
    # Create a tradable instrument with a SHORT position
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
    tradable = TradableInstrument(instrument)
    
    # Add a SHORT position with stop loss (stop loss triggers when price goes up)
    tradable.add_position(datetime(2025, 9, 17, 9, 0), 100.0, TradeAction.SELL, 1, stop_loss=105.0)
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
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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


def test_evaluate_for_stop_loss_method_isolated(evaluator, sample_candle):
    """Test the _evaluate_for_stop_loss method in isolation."""
    # Create a tradable instrument with an open position
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
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
