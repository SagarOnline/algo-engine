import pytest
from unittest.mock import Mock
from datetime import date, datetime
from algo_core.domain.backtest.engine import BacktestEngine
from algo_core.domain.strategy import Strategy
from algo_core.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo_core.domain.backtest.report_repository import BacktestReportRepository
from algo_core.domain.timeframe import Timeframe

@pytest.fixture
def mock_strategy():
    return Mock(spec=Strategy)

@pytest.fixture
def mock_historical_data_repository():
    from algo_core.domain.backtest.historical_data import HistoricalData
    repo = Mock(spec=HistoricalDataRepository)
    repo.get_historical_data.return_value = HistoricalData([])
    return repo

@pytest.fixture
def mock_report_repository():
    return Mock(spec=BacktestReportRepository)

@pytest.fixture
def backtest_engine(mock_historical_data_repository, mock_report_repository):
    return BacktestEngine(mock_historical_data_repository, mock_report_repository)

def test_run_delegates_to_historical_data_repository(backtest_engine, mock_strategy, mock_historical_data_repository):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 2)
    mock_strategy.get_instrument.return_value = 'instrument'
    mock_strategy.get_timeframe.return_value = Timeframe.ONE_DAY.value
    mock_strategy.get_required_history_start_date.return_value = start_date
    from algo_core.domain.backtest.historical_data import HistoricalData
    mock_historical_data_repository.get_historical_data.return_value = HistoricalData([])
    backtest_engine.start(mock_strategy, start_date, end_date)
    mock_historical_data_repository.get_historical_data.assert_called_once()

def test_run_saves_report(backtest_engine, mock_strategy, mock_report_repository, mock_historical_data_repository):
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 2)
    mock_strategy.get_instrument.return_value = 'instrument'
    mock_strategy.get_timeframe.return_value = Timeframe.ONE_DAY.value
    mock_strategy.get_required_history_start_date.return_value = start_date
    from algo_core.domain.backtest.historical_data import HistoricalData
    mock_historical_data_repository.get_historical_data.return_value = HistoricalData([])
    backtest_engine.start(mock_strategy, start_date, end_date)
    mock_report_repository.save.assert_called_once()
