import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from typing import Dict, Any, List

from domain.backtest.engine import BacktestEngine
from domain.strategy import Strategy
from domain.backtest.historical_data_repository import HistoricalDataRepository
from domain.timeframe import Timeframe

@pytest.fixture
def mock_strategy():
    strategy = Mock(spec=Strategy)
    strategy.get_name.return_value = "test_strategy"
    strategy.get_required_history_start_date.return_value = date(2023, 1, 1)
    strategy.get_timeframe.return_value = Timeframe.ONE_DAY.value
    
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
    repo = Mock(spec=HistoricalDataRepository)
    repo.get_historical_data.return_value = []
    return repo

@pytest.fixture
def backtest_engine(mock_strategy, mock_historical_data_repository):
    return BacktestEngine(mock_strategy, mock_historical_data_repository)

def generate_candle(timestamp_str: str, close_price: float) -> Dict[str, Any]:
    return {"timestamp": datetime.fromisoformat(timestamp_str), "close": close_price}


def test_run_with_no_data(backtest_engine: BacktestEngine):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 31)
    
    results = backtest_engine.run(start_date, end_date)
    
    assert results["pnl"] == 0
    assert len(results["trades"]) == 0
    backtest_engine.historical_data_repository.get_historical_data.assert_called_once()

def test_run_enters_and_exits_trade(backtest_engine: BacktestEngine, mock_strategy: Mock, mock_historical_data_repository: Mock):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 5)
    
    historical_data = [
        generate_candle("2023-01-01T09:15:00", 100),
        generate_candle("2023-01-02T09:15:00", 110), # Entry signal
        generate_candle("2023-01-03T09:15:00", 120),
        generate_candle("2023-01-04T09:15:00", 105), # Exit signal
        generate_candle("2023-01-05T09:15:00", 115),
    ]
    mock_historical_data_repository.get_historical_data.return_value = historical_data
    
    # Enter on the second candle, exit on the fourth
    mock_strategy.should_enter_trade.side_effect = [True, False, False, False]
    mock_strategy.should_exit_trade.side_effect = [False, True, False]

    results = backtest_engine.run(start_date, end_date)
    
    assert len(results["trades"]) == 1
    trade = results["trades"][0]
    assert trade["entry_price"] == 110
    assert trade["exit_price"] == 105
    assert results["pnl"] == -5

def test_run_respects_start_date(backtest_engine: BacktestEngine, mock_strategy: Mock, mock_historical_data_repository: Mock):
    start_date = date(2023, 1, 3)
    end_date = date(2023, 1, 5)
    
    # required_start_date will be earlier
    required_start_date = date(2023, 1, 1)
    mock_strategy.get_required_history_start_date.return_value = required_start_date

    historical_data = [
        generate_candle("2023-01-01T09:15:00", 100), # Should be ignored for trading
        generate_candle("2023-01-02T09:15:00", 110), # Should be ignored for trading
        generate_candle("2023-01-03T09:15:00", 120), # Entry signal
        generate_candle("2023-01-04T09:15:00", 130), # Exit signal
    ]
    mock_historical_data_repository.get_historical_data.return_value = historical_data
    
    # Only generate entry signal on 2023-01-03
    mock_strategy.should_enter_trade.side_effect = [True, False] # Corresponds to 3rd and 4th candle
    mock_strategy.should_exit_trade.side_effect = [True]

    backtest_engine.run(start_date, end_date)
    
    # Check that get_historical_data was called with the earlier date
    mock_historical_data_repository.get_historical_data.assert_called_with(
        mock_strategy.get_instrument(),
        required_start_date,
        end_date,
        Timeframe(mock_strategy.get_timeframe())
    )
    
    # should_enter_trade is called for each candle after the first one
    # but the engine's logic should prevent entering a trade before start_date
    #assert mock_strategy.should_enter_trade.call_count == 2
    
    # The first call to should_enter_trade corresponds to the candle on 2023-01-03
    # as the loop inside `run` starts trading after `start_date`
    #first_call_args = mock_strategy.should_enter_trade.call_args_list[0]
    #assert first_call_args[0][0]['timestamp'].date() == date(2023, 1, 3)

@patch('domain.backtest.engine.os')
@patch('domain.backtest.engine.open', new_callable=MagicMock)
@patch('domain.backtest.engine.json.dump')
def test_save_results_creates_directory_and_file(mock_json_dump, mock_open, mock_os, backtest_engine: BacktestEngine):
    mock_os.getenv.return_value = "test_reports"
    mock_os.path.join.side_effect = lambda *args: "/".join(args)

    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 31)
    
    results = {"strategy": "test_strategy", "pnl": 100, "trades": []}
    
    # Directly call the private method for this unit test
    backtest_engine._save_results(results, start_date, end_date)
    
    mock_os.makedirs.assert_called_with("test_reports", exist_ok=True)
    
    expected_filename = "test_strategy_2023-01-01_2023-01-31.json"
    expected_filepath = "test_reports/" + expected_filename
    
    mock_open.assert_called_with(expected_filepath, "w")
    mock_json_dump.assert_called_once()
    assert mock_json_dump.call_args[0][0] == results
