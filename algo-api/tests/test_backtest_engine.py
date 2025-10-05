import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from typing import Dict, Any, List

from algo.domain.backtest.engine import BacktestEngine
from algo.domain.strategy.strategy import InstrumentType, Strategy,Instrument,Exchange,PositionInstrument,PositionAction
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.timeframe import Timeframe

@pytest.fixture
def mock_strategy():
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_required_history_start_date.return_value = date(2023, 1, 1)
    strategy.get_timeframe.return_value = Timeframe.ONE_DAY.value
    
    instrument = Instrument(InstrumentType.STOCK,Exchange.NSE, "NSE_INE869I01013")
    strategy.get_instrument.return_value = instrument
    position= PositionInstrument(PositionAction.BUY,instrument)
    strategy.get_position_instrument.return_value = position

    # Default behavior: no trading signals
    strategy.should_enter_trade.return_value = False
    strategy.should_exit_trade.return_value = False
    
    return strategy

@pytest.fixture
def mock_strategy_for_respect_start_date():
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_timeframe.return_value = Timeframe.ONE_DAY.value
    
    # Default behavior: no trading signals
    strategy.should_enter_trade.return_value = False
    strategy.should_exit_trade.return_value = False
    
    return strategy

@pytest.fixture
def mock_historical_data_repository():
    from algo.domain.backtest.historical_data import HistoricalData
    repo = Mock(spec=HistoricalDataRepository)
    repo.get_historical_data.return_value = HistoricalData([])
    return repo

@pytest.fixture
def mock_tradable_instrument_repository():
    from algo.domain.backtest.report import TradableInstrument
    repo = Mock(spec=TradableInstrumentRepository)
    
    # Create a real TradableInstrument using the same instrument from mock_strategy
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
    real_tradable_instrument = TradableInstrument(instrument)
    
    # Mock the repository to return the saved instrument
    repo.get_tradable_instruments.return_value = [real_tradable_instrument]
    
    return repo



@pytest.fixture
def backtest_engine(mock_historical_data_repository, mock_tradable_instrument_repository):
    return BacktestEngine(mock_historical_data_repository, mock_tradable_instrument_repository)


def generate_candle(timestamp_str: str, close_price: float) -> Dict[str, Any]:
    return {"timestamp": datetime.fromisoformat(timestamp_str), "close": close_price}



def test_run_with_no_data(mock_strategy: Strategy, backtest_engine: BacktestEngine):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 31)
    
    report = backtest_engine.start(mock_strategy, start_date, end_date)
    assert report.total_pnl() == 0
    assert len(report.tradable.positions) == 0
    


def test_run_enters_and_exits_trade(backtest_engine: BacktestEngine, mock_strategy: Mock, mock_historical_data_repository: Mock):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 5)
    
    from algo.domain.backtest.historical_data import HistoricalData
    historical_data = [
        generate_candle("2023-01-01T09:15:00", 100),
        generate_candle("2023-01-02T09:15:00", 110), # Entry signal
        generate_candle("2023-01-03T09:15:00", 120),
        generate_candle("2023-01-04T09:15:00", 105), # Exit signal
        generate_candle("2023-01-05T09:15:00", 115),
    ]
    mock_historical_data_repository.get_historical_data.return_value = HistoricalData(historical_data)
    
    # Enter on the second candle, exit on the fourth
    mock_strategy.should_enter_trade.side_effect = [False, True, False, False, False]
    mock_strategy.should_exit_trade.side_effect = [False, True, False]
    mock_strategy.calculate_stop_loss_for.return_value = None

    report = backtest_engine.start(mock_strategy, start_date, end_date)
    
    assert len(report.tradable.positions) == 1
    position = report.tradable.positions[0]
    assert position.entry_price() == 110
    assert position.exit_price() == 105
    assert report.total_pnl() == -5


def test_run_respects_start_date():
    """Test using real objects instead of mocks for better debugging."""
    from algo.domain.backtest.historical_data import HistoricalData
    from algo.domain.backtest.report import TradableInstrument
    from algo.infrastructure.in_memory_tradable_instrument_repository import InMemoryTradableInstrumentRepository
    
    start_date = date(2023, 1, 3)
    end_date = date(2023, 1, 5)
    
    # Create real strategy with required methods
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_timeframe.return_value = Timeframe.ONE_DAY.value
    
    # required_start_date will be earlier
    required_start_date = date(2023, 1, 1)
    strategy.get_required_history_start_date.return_value = required_start_date
    
    # Use real domain objects
    instrument = Instrument(InstrumentType.STOCK, Exchange.NSE, "NSE_INE869I01013")
    strategy.get_instrument.return_value = instrument
    position = PositionInstrument(PositionAction.BUY, instrument)
    strategy.get_position_instrument.return_value = position
    
    # Trading signal behavior
    strategy.should_enter_trade.side_effect = [True, False]  # Corresponds to 3rd and 4th candle
    strategy.should_exit_trade.side_effect = [True]
    strategy.calculate_stop_loss_for.return_value = None
    
    # Create real historical data repository
    class TestHistoricalDataRepository(HistoricalDataRepository):
        def __init__(self, test_data):
            self.test_data = test_data
            
        def get_historical_data(self, instrument, start_date, end_date, timeframe):
            return HistoricalData(self.test_data)
    
    historical_data = [
        generate_candle("2023-01-01T09:15:00", 100), # Should be ignored for trading
        generate_candle("2023-01-02T09:15:00", 110), # Should be ignored for trading
        generate_candle("2023-01-03T09:15:00", 120), # Entry signal
        generate_candle("2023-01-04T09:15:00", 130), # Exit signal
    ]
    
    # Use real repositories
    historical_repo = TestHistoricalDataRepository(historical_data)
    tradable_repo = InMemoryTradableInstrumentRepository()
    
    # Create real backtest engine
    backtest_engine = BacktestEngine(historical_repo, tradable_repo)
    
    # This should now step into properly during debugging
    report = backtest_engine.start(strategy, start_date, end_date)
    
    # Verify the results - should have exactly one position
    assert len(report.tradable.positions) == 1
    
    # Get the position and verify trade execution details
    position = report.tradable.positions[0]
    
    # Verify entry details - should enter on 2023-01-03 at price 120
    assert position.entry_time().date() == date(2023, 1, 3)
    assert position.entry_price() == 120
    
    # Verify exit details - should exit on 2023-01-04 at price 130
    assert position.exit_time().date() == date(2023, 1, 4)
    assert position.exit_price() == 130
    
    # Verify PnL - should be profitable (130 - 120 = 10 points profit)
    assert position.pnl() == 10
    assert report.total_pnl() == 10
    
