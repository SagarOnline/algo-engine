import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, datetime
from algo.domain.backtest.backtest import BackTest
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.backtest.report import BackTestReport
from algo.domain.strategy.strategy import Strategy, Instrument, TradeAction, PositionInstrument, Exchange, Type
from algo.domain.strategy.strategy_evaluator import StrategyEvaluator, TradeSignal, PositionAction
from algo.domain.backtest.backtest_trade_executor import BackTestTradeExecutor
from algo.domain.strategy.tradable_instrument import TradableInstrument, TriggerType
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.timeframe import Timeframe


def create_test_instrument():
    """Create a real Instrument object for testing."""
    return Instrument(
        type=Type.EQ,
        exchange=Exchange.NSE,
        instrument_key="NSE_EQ|INE002A01018"
    )


def create_test_position_instrument():
    """Create a real PositionInstrument object for testing."""
    instrument = create_test_instrument()
    return PositionInstrument(TradeAction.BUY, instrument)


def create_test_tradable_instrument():
    """Create a real TradableInstrument object for testing."""
    position_instrument = create_test_position_instrument()
    return TradableInstrument(position_instrument.instrument)


@pytest.fixture
def mock_strategy():
    """Create a mock Strategy with required methods and real domain objects."""
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "TestStrategy"
    strategy.get_display_name.return_value = "Test Trading Strategy"
    strategy.get_timeframe.return_value = "5min"
    
    # Use real domain objects instead of mocks
    instrument = create_test_instrument()
    position_instrument = create_test_position_instrument()
    
    strategy.get_instrument.return_value = instrument
    strategy.get_position_instrument.return_value = position_instrument
    
    # Mock required history start date method
    strategy.get_required_history_start_date.return_value = date(2024, 1, 1)
    
    return strategy


@pytest.fixture
def mock_historical_data_repository():
    """Create a mock HistoricalDataRepository."""
    return Mock(spec=HistoricalDataRepository)


@pytest.fixture
def mock_tradable_instrument_repository():
    """Create a mock TradableInstrumentRepository."""
    return Mock(spec=TradableInstrumentRepository)


@pytest.fixture
def sample_historical_data():
    """Create sample historical data for testing."""
    data = []
    # Create 10 days of historical data (Jan 1-10, 2024)
    for day in range(1, 11):
        for hour in [9, 10, 11, 12, 13, 14, 15]:  # Trading hours
            data.append({
                "timestamp": datetime(2024, 1, day, hour, 0),
                "open": 100.0 + day + hour * 0.1,
                "high": 105.0 + day + hour * 0.1,
                "low": 99.0 + day + hour * 0.1,
                "close": 103.0 + day + hour * 0.1,
                "volume": 1000 + day * 100,
                "oi": None
            })
    return HistoricalData(data)


@pytest.fixture
def backtest_instance(mock_strategy, mock_historical_data_repository, mock_tradable_instrument_repository):
    """Create a BackTest instance with mocked dependencies."""
    start_date = date(2024, 1, 5)
    end_date = date(2024, 1, 8)
    
    return BackTest(
        strategy=mock_strategy,
        historical_data_repository=mock_historical_data_repository,
        tradable_instrument_repository=mock_tradable_instrument_repository,
        start_date=start_date,
        end_date=end_date
    )


class TestBackTestRun:
    """Test suite for BackTest.run method."""

    def test_backtest_initialization(self, mock_strategy, mock_historical_data_repository, 
                                   mock_tradable_instrument_repository):
        """Test that BackTest initializes correctly with required dependencies."""
        start_date = date(2024, 1, 5)
        end_date = date(2024, 1, 8)
        
        backtest = BackTest(
            strategy=mock_strategy,
            historical_data_repository=mock_historical_data_repository,
            tradable_instrument_repository=mock_tradable_instrument_repository,
            start_date=start_date,
            end_date=end_date
        )
        
        assert backtest.strategy is mock_strategy
        assert backtest.historical_data_repository is mock_historical_data_repository
        assert backtest.tradable_instrument_repository is mock_tradable_instrument_repository
        assert backtest.start_date == start_date
        assert backtest.end_date == end_date

    def test_run_basic_workflow_no_signals(self, backtest_instance, mock_strategy, 
                                         mock_historical_data_repository, mock_tradable_instrument_repository,
                                         sample_historical_data):
        """Test the basic workflow of BackTest.run method with no trade signals."""
        # Setup mocks
        mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
        
        # Create a real TradableInstrument that will be returned after being saved
        real_tradable_instrument = create_test_tradable_instrument()
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [real_tradable_instrument]
        
        # Mock StrategyEvaluator to return no signals
        with patch.object(StrategyEvaluator, '__init__', return_value=None) as mock_init:
            with patch.object(StrategyEvaluator, 'evaluate', return_value=[]) as mock_evaluate:
                # Mock BackTestTradeExecutor
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None):
                    with patch.object(BackTestTradeExecutor, 'execute') as mock_execute:
                        
                        # Run backtest
                        result = backtest_instance.run()
        
        # Verify the result
        assert isinstance(result, BackTestReport)
        assert result.strategy_name == "Test Trading Strategy"
        assert result.start_date == date(2024, 1, 5)
        assert result.end_date == date(2024, 1, 8)
        
        # Verify historical data was fetched with extended date range
        mock_historical_data_repository.get_historical_data.assert_called_once()
        call_args = mock_historical_data_repository.get_historical_data.call_args[0]
        assert call_args[1] == date(2024, 1, 1)  # extended start date from strategy
        assert call_args[2] == date(2024, 1, 8)  # backtest end date
        
        # Verify StrategyEvaluator was initialized correctly
        mock_init.assert_called_once_with(
            mock_strategy,
            mock_historical_data_repository,
            mock_tradable_instrument_repository
        )
        
        # Verify evaluate was called for each candle in date range
        # Should be called for dates 5,6,7,8 January (4 days * 7 hours = 28 times)
        assert mock_evaluate.call_count == 28
        
        # Verify execute was never called (no signals)
        mock_execute.assert_not_called()

    def test_run_with_trade_signals(self, backtest_instance, mock_strategy, 
                                  mock_historical_data_repository, mock_tradable_instrument_repository,
                                  sample_historical_data):
        """Test BackTest.run with trade signals being generated and executed."""
        # Setup mocks
        mock_historical_data_repository.get_historical_data.return_value = sample_historical_data
        
        # Create a real TradableInstrument that will be returned after being saved
        real_tradable_instrument = create_test_tradable_instrument()
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [real_tradable_instrument]
        
        # Create sample trade signals
        sample_instrument = mock_strategy.get_instrument.return_value
        buy_signal = TradeSignal(sample_instrument, TradeAction.BUY, 1, datetime(2024, 1, 5, 10, 0), Timeframe("5min"), PositionAction.ADD, trigger_type=TriggerType.ENTRY_RULES)
        sell_signal = TradeSignal(sample_instrument, TradeAction.SELL, 1, datetime(2024, 1, 7, 12, 0), Timeframe("5min"), PositionAction.EXIT, trigger_type=TriggerType.EXIT_RULES)

        # Mock StrategyEvaluator to return trade signals alternately
        signal_sequence = [[buy_signal], [], [], [sell_signal]] + [[]] * 24  # Fill remaining calls with empty lists
        
        with patch.object(StrategyEvaluator, '__init__', return_value=None):
            with patch.object(StrategyEvaluator, 'evaluate', side_effect=signal_sequence) as mock_evaluate:
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None):
                    with patch.object(BackTestTradeExecutor, 'execute') as mock_execute:
                        
                        # Run backtest
                        result = backtest_instance.run()
        
        # Verify trade executor was called with the signals that were generated
        assert mock_execute.call_count == 2
        mock_execute.assert_any_call(buy_signal)
        mock_execute.assert_any_call(sell_signal)
        
        # Verify the result is still a proper BackTestReport
        assert isinstance(result, BackTestReport)

    def test_run_skips_candles_outside_date_range(self, backtest_instance, mock_strategy,
                                                mock_historical_data_repository, mock_tradable_instrument_repository):
        """Test that candles outside the backtest date range are skipped for evaluation."""
        # Create historical data with dates both inside and outside the backtest range
        extended_data = []
        
        # Data before start date (Jan 1-4) - should be skipped for evaluation
        for day in range(1, 5):
            extended_data.append({
                "timestamp": datetime(2024, 1, day, 10, 0),
                "open": 100.0, "high": 105.0, "low": 99.0, "close": 103.0, "volume": 1000, "oi": None
            })
        
        # Data in backtest range (Jan 5-8) - should be evaluated
        for day in range(5, 9):
            extended_data.append({
                "timestamp": datetime(2024, 1, day, 10, 0),
                "open": 100.0, "high": 105.0, "low": 99.0, "close": 103.0, "volume": 1000, "oi": None
            })
        
        # Data after end date (Jan 9-12) - should be skipped
        for day in range(9, 13):
            extended_data.append({
                "timestamp": datetime(2024, 1, day, 10, 0),
                "open": 100.0, "high": 105.0, "low": 99.0, "close": 103.0, "volume": 1000, "oi": None
            })
        
        historical_data = HistoricalData(extended_data)
        mock_historical_data_repository.get_historical_data.return_value = historical_data
        
        # Create a real TradableInstrument that will be returned after being saved
        real_tradable_instrument = create_test_tradable_instrument()
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [real_tradable_instrument]
        
        with patch.object(StrategyEvaluator, '__init__', return_value=None):
            with patch.object(StrategyEvaluator, 'evaluate', return_value=[]) as mock_evaluate:
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None):
                    
                    # Run backtest
                    result = backtest_instance.run()
        
        # Should only evaluate candles within the backtest date range (Jan 5-8 = 4 days)
        assert mock_evaluate.call_count == 4

    def test_run_handles_extended_historical_data_request(self, backtest_instance, mock_strategy,
                                                        mock_historical_data_repository, mock_tradable_instrument_repository):
        """Test that backtest requests extended historical data based on strategy requirements."""
        mock_historical_data_repository.get_historical_data.return_value = HistoricalData([])
        
        # Create a real TradableInstrument that will be returned after being saved
        real_tradable_instrument = create_test_tradable_instrument()
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [real_tradable_instrument]
        
        # Set up strategy to require historical data starting earlier than backtest start date
        mock_strategy.get_required_history_start_date.return_value = date(2023, 12, 1)
        
        with patch.object(StrategyEvaluator, '__init__', return_value=None):
            with patch.object(StrategyEvaluator, 'evaluate', return_value=[]):
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None):
                    
                    # Run backtest
                    backtest_instance.run()
        
        # Verify that historical data was requested from the strategy's required start date
        mock_historical_data_repository.get_historical_data.assert_called_once()
        call_args = mock_historical_data_repository.get_historical_data.call_args[0]
        
        assert call_args[0] == mock_strategy.get_instrument.return_value  # instrument
        assert call_args[1] == date(2023, 12, 1)  # extended start date
        assert call_args[2] == date(2024, 1, 8)   # backtest end date
        assert isinstance(call_args[3], Timeframe)  # timeframe

    def test_run_creates_correct_components(self, backtest_instance, mock_strategy,
                                          mock_historical_data_repository, mock_tradable_instrument_repository):
        """Test that BackTest.run creates StrategyEvaluator and BackTestTradeExecutor with correct parameters."""
        mock_historical_data_repository.get_historical_data.return_value = HistoricalData([])
        
        # Create a real TradableInstrument that will be returned after being saved
        real_tradable_instrument = create_test_tradable_instrument()
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [real_tradable_instrument]
        
        with patch.object(StrategyEvaluator, '__init__', return_value=None) as mock_evaluator_init:
            with patch.object(StrategyEvaluator, 'evaluate', return_value=[]):
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None) as mock_executor_init:
                    
                    # Run backtest
                    backtest_instance.run()
        
        # Verify StrategyEvaluator was created with correct parameters
        mock_evaluator_init.assert_called_once_with(
            mock_strategy,
            mock_historical_data_repository,
            mock_tradable_instrument_repository
        )
        
        # Verify BackTestTradeExecutor was created with correct parameters
        mock_executor_init.assert_called_once_with(
            mock_tradable_instrument_repository,
            mock_historical_data_repository,
            mock_strategy
        )

    def test_run_handles_timeframe_conversion(self, backtest_instance, mock_strategy,
                                            mock_historical_data_repository, mock_tradable_instrument_repository):
        """Test that BackTest.run correctly converts strategy timeframe to Timeframe object."""
        mock_historical_data_repository.get_historical_data.return_value = HistoricalData([])
        
        # Create a mock TradableInstrument that will be returned after being saved
        mock_tradable_instrument = Mock(spec=TradableInstrument)
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [mock_tradable_instrument]
        
        # Set different timeframe values
        mock_strategy.get_timeframe.return_value = "15min"
        
        with patch.object(StrategyEvaluator, '__init__', return_value=None):
            with patch.object(StrategyEvaluator, 'evaluate', return_value=[]):
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None):
                    
                    # Run backtest
                    backtest_instance.run()
        
        # Verify that Timeframe object was created and used
        call_args = mock_historical_data_repository.get_historical_data.call_args[0]
        timeframe_arg = call_args[3]
        assert isinstance(timeframe_arg, Timeframe)

    def test_run_returns_correct_backtest_report(self, backtest_instance, mock_strategy,
                                               mock_historical_data_repository, mock_tradable_instrument_repository):
        """Test that BackTest.run returns a properly configured BackTestReport."""
        mock_historical_data_repository.get_historical_data.return_value = HistoricalData([])
        
        # Mock final tradable instrument from repository
        mock_tradable = Mock(spec=TradableInstrument)
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [mock_tradable]
        
        with patch.object(StrategyEvaluator, '__init__', return_value=None):
            with patch.object(StrategyEvaluator, 'evaluate', return_value=[]):
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None):
                    
                    # Run backtest
                    result = backtest_instance.run()
        
        # Verify the returned report has correct properties
        assert isinstance(result, BackTestReport)
        assert result.strategy_name == mock_strategy.get_display_name.return_value
        assert result.start_date == backtest_instance.start_date
        assert result.end_date == backtest_instance.end_date

    def test_run_handles_no_tradable_instruments(self, backtest_instance, mock_strategy,
                                               mock_historical_data_repository, mock_tradable_instrument_repository):
        """Test that BackTest.run creates and saves a TradableInstrument at the start."""
        mock_historical_data_repository.get_historical_data.return_value = HistoricalData([])
        
        # Create a mock TradableInstrument that will be returned after being saved
        mock_tradable_instrument = Mock(spec=TradableInstrument)
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [mock_tradable_instrument]
        
        with patch.object(StrategyEvaluator, '__init__', return_value=None):
            with patch.object(StrategyEvaluator, 'evaluate', return_value=[]):
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None):
                    
                    # Run backtest
                    result = backtest_instance.run()
        
        # Verify that save_tradable_instrument was called to create the TradableInstrument
        mock_tradable_instrument_repository.save_tradable_instrument.assert_called_once()
        call_args = mock_tradable_instrument_repository.save_tradable_instrument.call_args[0]
        assert call_args[0] == mock_strategy.get_name.return_value  # strategy name
        assert isinstance(call_args[1], TradableInstrument)  # TradableInstrument instance
        
        # Verify that the report is created with the tradable instrument
        assert isinstance(result, BackTestReport)
        # The tradable parameter should be None when no instruments are found

    def test_run_processes_candles_in_correct_order(self, backtest_instance, mock_strategy,
                                                  mock_historical_data_repository, mock_tradable_instrument_repository):
        """Test that BackTest.run processes candles in chronological order within date range."""
        # Create historical data with specific timestamps
        ordered_data = []
        expected_timestamps = []
        
        for day in [5, 6, 7, 8]:  # Within backtest range
            for hour in [9, 12, 15]:
                timestamp = datetime(2024, 1, day, hour, 0)
                ordered_data.append({
                    "timestamp": timestamp,
                    "open": 100.0, "high": 105.0, "low": 99.0, "close": 103.0, "volume": 1000, "oi": None
                })
                expected_timestamps.append(timestamp)
        
        historical_data = HistoricalData(ordered_data)
        mock_historical_data_repository.get_historical_data.return_value = historical_data
        
        # Create a mock TradableInstrument that will be returned after being saved
        mock_tradable_instrument = Mock(spec=TradableInstrument)
        mock_tradable_instrument_repository.get_tradable_instruments.return_value = [mock_tradable_instrument]
        
        actual_timestamps = []
        
        def capture_timestamp(candle):
            actual_timestamps.append(candle['timestamp'])
            return []
        
        with patch.object(StrategyEvaluator, '__init__', return_value=None):
            with patch.object(StrategyEvaluator, 'evaluate', side_effect=capture_timestamp) as mock_evaluate:
                with patch.object(BackTestTradeExecutor, '__init__', return_value=None):
                    
                    # Run backtest
                    backtest_instance.run()
        
        # Verify candles were processed in correct order
        assert actual_timestamps == expected_timestamps
        assert len(actual_timestamps) == 12  # 4 days * 3 hours per day
