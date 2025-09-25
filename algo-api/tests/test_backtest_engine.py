import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from typing import Dict, Any, List

from algo.domain.backtest.engine import BacktestEngine
from algo.domain.strategy.strategy import InstrumentType, Strategy,Instrument,Exchange,PositionInstrument,PositionAction
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
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
def backtest_engine(mock_historical_data_repository):
    return BacktestEngine(mock_historical_data_repository)


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


def test_run_respects_start_date(backtest_engine: BacktestEngine, mock_strategy: Mock, mock_historical_data_repository: Mock):
    start_date = date(2023, 1, 3)
    end_date = date(2023, 1, 5)
    
    # required_start_date will be earlier
    required_start_date = date(2023, 1, 1)
    mock_strategy.get_required_history_start_date.return_value = required_start_date

    from algo.domain.backtest.historical_data import HistoricalData
    historical_data = [
        generate_candle("2023-01-01T09:15:00", 100), # Should be ignored for trading
        generate_candle("2023-01-02T09:15:00", 110), # Should be ignored for trading
        generate_candle("2023-01-03T09:15:00", 120), # Entry signal
        generate_candle("2023-01-04T09:15:00", 130), # Exit signal
    ]
    mock_historical_data_repository.get_historical_data.return_value = HistoricalData(historical_data)
    
    # Only generate entry signal on 2023-01-03
    mock_strategy.should_enter_trade.side_effect = [True, False] # Corresponds to 3rd and 4th candle
    mock_strategy.should_exit_trade.side_effect = [True]
    mock_strategy.calculate_stop_loss_for.return_value = None
    report = backtest_engine.start(mock_strategy, start_date, end_date)
    
    
    # should_enter_trade is called for each candle after the first one
    # but the engine's logic should prevent entering a trade before start_date
    assert len(report.tradable.positions) == 1
    
    # The first call to should_enter_trade corresponds to the candle on 2023-01-03
    # as the loop inside `run` starts trading after `start_date`
    first_call_args = mock_strategy.should_enter_trade.call_args_list[0][0][0]
    assert first_call_args[len(first_call_args)-1]['timestamp'].date() == date(2023, 1, 3)
    
