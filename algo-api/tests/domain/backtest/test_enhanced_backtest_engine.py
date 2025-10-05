import pytest
from unittest.mock import Mock, patch
from datetime import date
from algo.domain.backtest.engine import BacktestEngine
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.strategy.strategy import Strategy
from algo.domain.backtest.report import BackTestReport
from algo.domain.backtest.backtest import BackTest


@pytest.fixture
def mock_historical_data_repository():
    """Create a mock HistoricalDataRepository."""
    return Mock(spec=HistoricalDataRepository)


@pytest.fixture
def mock_tradable_instrument_repository():
    """Create a mock TradableInstrumentRepository."""
    return Mock(spec=TradableInstrumentRepository)


@pytest.fixture
def mock_strategy():
    """Create a mock Strategy."""
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "TestStrategy"
    strategy.get_display_name.return_value = "Test Trading Strategy"
    return strategy


@pytest.fixture
def backtest_engine(mock_historical_data_repository, mock_tradable_instrument_repository):
    """Create a BacktestEngine with mocked dependencies."""
    return BacktestEngine(mock_historical_data_repository, mock_tradable_instrument_repository)


class TestEnhancedBacktestEngine:
    """Test suite for enhanced BacktestEngine using the new BackTest class."""

    def test_backtest_engine_initialization(self, mock_historical_data_repository, mock_tradable_instrument_repository):
        """Test that BacktestEngine initializes correctly with both required repositories."""
        engine = BacktestEngine(mock_historical_data_repository, mock_tradable_instrument_repository)
        
        assert engine.historical_data_repository is mock_historical_data_repository
        assert engine.tradable_instrument_repository is mock_tradable_instrument_repository

    def test_start_method_creates_and_runs_backtest(self, backtest_engine, mock_strategy):
        """Test that start method creates BackTest instance and calls run method."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        expected_report = Mock(spec=BackTestReport)
        
        # Mock the BackTest class
        with patch('algo.domain.backtest.engine.BackTest') as mock_backtest_class:
            mock_backtest_instance = Mock()
            mock_backtest_instance.run.return_value = expected_report
            mock_backtest_class.return_value = mock_backtest_instance
            
            # Call the start method
            result = backtest_engine.start(mock_strategy, start_date, end_date)
            
            # Verify BackTest was created with correct parameters
            mock_backtest_class.assert_called_once_with(
                strategy=mock_strategy,
                historical_data_repository=backtest_engine.historical_data_repository,
                tradable_instrument_repository=backtest_engine.tradable_instrument_repository,
                start_date=start_date,
                end_date=end_date
            )
            
            # Verify run method was called
            mock_backtest_instance.run.assert_called_once()
            
            # Verify correct report was returned
            assert result is expected_report

    def test_start_method_integration(self, backtest_engine, mock_strategy):
        """Integration test for start method with minimal mocking."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        # Mock strategy methods that BackTest will call
        mock_strategy.get_name.return_value = "IntegrationTestStrategy"
        mock_strategy.get_display_name.return_value = "Integration Test Strategy"
        
        # Use a real BackTest instance with mocked run method
        with patch.object(BackTest, 'run') as mock_run:
            mock_report = Mock(spec=BackTestReport)
            mock_run.return_value = mock_report
            
            # Call the start method
            result = backtest_engine.start(mock_strategy, start_date, end_date)
            
            # Verify run was called
            mock_run.assert_called_once()
            
            # Verify result
            assert result is mock_report

    def test_engine_passes_correct_repositories_to_backtest(self, mock_historical_data_repository, 
                                                          mock_tradable_instrument_repository, mock_strategy):
        """Test that the engine passes the correct repository instances to BackTest."""
        engine = BacktestEngine(mock_historical_data_repository, mock_tradable_instrument_repository)
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        with patch('algo.domain.backtest.engine.BackTest') as mock_backtest_class:
            mock_backtest_instance = Mock()
            mock_backtest_instance.run.return_value = Mock(spec=BackTestReport)
            mock_backtest_class.return_value = mock_backtest_instance
            
            # Call start method
            engine.start(mock_strategy, start_date, end_date)
            
            # Verify the repositories passed are the exact same instances
            call_kwargs = mock_backtest_class.call_args.kwargs
            assert call_kwargs['historical_data_repository'] is mock_historical_data_repository
            assert call_kwargs['tradable_instrument_repository'] is mock_tradable_instrument_repository

    def test_engine_handles_different_date_ranges(self, backtest_engine, mock_strategy):
        """Test that the engine correctly passes different date ranges to BackTest."""
        test_cases = [
            (date(2024, 1, 1), date(2024, 1, 31)),
            (date(2023, 12, 1), date(2024, 2, 28)),
            (date(2024, 6, 15), date(2024, 6, 15))  # Single day
        ]
        
        for start_date, end_date in test_cases:
            with patch('algo.domain.backtest.engine.BackTest') as mock_backtest_class:
                mock_backtest_instance = Mock()
                mock_backtest_instance.run.return_value = Mock(spec=BackTestReport)
                mock_backtest_class.return_value = mock_backtest_instance
                
                # Call start method
                backtest_engine.start(mock_strategy, start_date, end_date)
                
                # Verify correct dates were passed
                call_kwargs = mock_backtest_class.call_args.kwargs
                assert call_kwargs['start_date'] == start_date
                assert call_kwargs['end_date'] == end_date
