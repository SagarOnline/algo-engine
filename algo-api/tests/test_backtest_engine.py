import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from typing import Dict, Any, List

from algo.domain.backtest.engine import BacktestEngine
from algo.domain.strategy.strategy import Segment, Strategy,Instrument,Exchange,PositionInstrument,TradeAction,Type
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.tradable_instrument_repository import TradableInstrumentRepository
from algo.domain.timeframe import Timeframe
from algo.domain.trading.trading_window_service import TradingWindowService

@pytest.fixture
def mock_strategy():
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_required_history_start_date.return_value = datetime(2023, 1, 1, 9, 15, 0)
    strategy.get_timeframe.return_value = Timeframe.ONE_DAY.value

    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013", type=Type.FUT)
    strategy.get_instrument.return_value = instrument
    position= PositionInstrument(TradeAction.BUY,instrument)
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
    from algo.domain.strategy.tradable_instrument import TradableInstrument
    repo = Mock(spec=TradableInstrumentRepository)
    
    # Create a real TradableInstrument using the same instrument from mock_strategy
    instrument = Instrument(Segment.EQ, Exchange.NSE, "NSE_INE869I01013", type=Type.EQ)
    real_tradable_instrument = TradableInstrument(instrument)
    
    # Mock the repository to return the saved instrument
    repo.get_tradable_instruments.return_value = [real_tradable_instrument]
    
    return repo

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

@pytest.fixture
def backtest_engine(mock_historical_data_repository, mock_tradable_instrument_repository):
    return BacktestEngine(mock_historical_data_repository, mock_tradable_instrument_repository)


def generate_candle(timestamp_str: str, open_price: float, close_price: float) -> Dict[str, Any]:
    return {"timestamp": datetime.fromisoformat(timestamp_str), "open": open_price, "close": close_price}



def test_run_with_no_data(mock_strategy: Strategy, backtest_engine: BacktestEngine):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 31)
    
    report = backtest_engine.start(mock_strategy, start_date, end_date)
    assert report.total_pnl() == 0
    assert len(report.tradable.positions) == 0
    


def test_run_enters_and_exits_trade(backtest_engine: BacktestEngine, mock_strategy: Mock, mock_historical_data_repository: Mock, patched_trading_window_service: Mock):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 5)
    
    from algo.domain.backtest.historical_data import HistoricalData
    historical_data = [
        generate_candle("2023-01-01T09:15:00", 100, 100),
        generate_candle("2023-01-02T09:15:00", 105, 110), # Entry signal
        generate_candle("2023-01-03T09:15:00", 110, 120), # Entry executed at open=110
        generate_candle("2023-01-04T09:15:00", 120, 105), # Exit signal  
        generate_candle("2023-01-05T09:15:00", 105, 115), # Exit executed at open=105
    ]
    mock_historical_data_repository.get_historical_data.return_value = HistoricalData(historical_data)
    
    # Enter on the second candle, exit on the fourth
    mock_strategy.should_enter_trade.side_effect = [False, True, False, False, False]
    mock_strategy.should_exit_trade.side_effect = [False, False, False, True, False]
    mock_strategy.calculate_stop_loss_for.return_value = None

    report = backtest_engine.start(mock_strategy, start_date, end_date)
    
    assert len(report.tradable.positions) == 1
    position = report.tradable.positions[0]
    assert position.entry_price() == 110  # Open of next candle after entry signal
    assert position.exit_price() == 105   # Open of next candle after exit signal
    assert report.total_pnl() == -5


def test_run_respects_start_date(patched_trading_window_service: Mock):
    """Test using real objects instead of mocks for better debugging."""
    from algo.domain.backtest.historical_data import HistoricalData
    from algo.domain.strategy.tradable_instrument import TradableInstrument
    from algo.infrastructure.in_memory_tradable_instrument_repository import InMemoryTradableInstrumentRepository
    
    start_date = date(2023, 1, 3)
    end_date = date(2023, 1, 5)  # Extended to include exit execution
    
    # Create real strategy with required methods
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_timeframe.return_value = Timeframe.ONE_DAY.value
    
    # required_start_date will be earlier
    required_start_date = datetime(2023, 1, 1, 9, 15, 0)
    strategy.get_required_history_start_date.return_value = required_start_date
    
    # Use real domain objects
    instrument = Instrument(Segment.FNO, Exchange.NSE, "NSE_INE869I01013", type=Type.FUT)
    strategy.get_instrument.return_value = instrument
    position = PositionInstrument(TradeAction.BUY, instrument)
    strategy.get_position_instrument.return_value = position
    
    # Trading signal behavior
    strategy.should_enter_trade.side_effect = [True, False, False]  # Entry signal on 3rd candle
    strategy.should_exit_trade.side_effect = [False, True, False]          # Exit signal on 4th candle
    strategy.calculate_stop_loss_for.return_value = None
    
    # Create real historical data repository
    class TestHistoricalDataRepository(HistoricalDataRepository):
        def __init__(self, test_data):
            self.test_data = test_data
            
        def get_historical_data(self, instrument, start_date, end_date, timeframe):
            return HistoricalData(self.test_data)
    
    historical_data = [
        generate_candle("2023-01-01T09:15:00", 100, 100), # Should be ignored for trading
        generate_candle("2023-01-02T09:15:00", 110, 110), # Should be ignored for trading  
        generate_candle("2023-01-03T09:15:00", 120, 120), # Entry signal
        generate_candle("2023-01-04T09:15:00", 120, 130), # Entry executed at open=120, Exit signal
        generate_candle("2023-01-05T09:15:00", 130, 135), # Exit executed at open=130
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
    
    # Verify entry details - should enter on 2023-01-04 at open price 120 (next day after entry signal on 2023-01-03)
    assert position.entry_time().date() == date(2023, 1, 4)
    assert position.entry_price() == 120
    
    # Verify exit details - should exit on 2023-01-05 at open price 130 (next day after exit signal on 2023-01-04)  
    assert position.exit_time().date() == date(2023, 1, 5)
    assert position.exit_price() == 130
    
    # Verify PnL - should be profitable (130 - 120 = 10 points profit)
    assert position.pnl() == 10
    assert report.total_pnl() == 10
    
