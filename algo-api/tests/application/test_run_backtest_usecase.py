from datetime import datetime
import pytest
from unittest.mock import MagicMock, ANY
from algo.application.run_backtest_usecase import RunBacktestUseCase
from algo.application.run_backtest_usecase import RunBacktestInput
from algo.application.util import fmt_currency, fmt_percent

@pytest.fixture
def mock_historical_data_repository():
    return MagicMock()

@pytest.fixture
def mock_tradable_instrument_repository():
    return MagicMock()

@pytest.fixture
def mock_strategy_repository():
    return MagicMock()

@pytest.fixture
def usecase(mock_historical_data_repository, mock_tradable_instrument_repository, mock_strategy_repository):
    return RunBacktestUseCase(
        historical_data_repository=mock_historical_data_repository,
        tradable_instrument_repository=mock_tradable_instrument_repository,
        strategy_repository=mock_strategy_repository
    )

def test_execute_success(usecase, mock_strategy_repository, mock_historical_data_repository, mock_tradable_instrument_repository):
    strategy_name = "test_strategy"
    payload = {
        "strategy_name": strategy_name
    }
    mock_strategy = MagicMock()
    mock_strategy_repository.get_strategy.return_value = mock_strategy
    # Prepare mock_report with expected DTO fields
    mock_report = MagicMock()
    mock_report.start_date = datetime.strptime("2023-01-01", "%Y-%m-%d")
    mock_report.end_date = datetime.strptime("2023-01-10", "%Y-%m-%d")
    mock_report.strategy_name = strategy_name
    mock_report.total_trades_count.return_value = 5
    mock_report.winning_trades_count.return_value = 3
    mock_report.losing_trades_count.return_value = 2
    mock_report.winning_streak.return_value = 2
    mock_report.losing_streak.return_value = 1
    mock_report.max_gain.return_value = 100.0
    mock_report.max_loss.return_value = -50.0
    mock_report.total_pnl_points.return_value = 150.0
    mock_report.total_pnl_percentage.return_value = 0.15
    mock_report.tradable = MagicMock()
    usecase.engine.start = MagicMock(return_value=mock_report)
    input_obj = RunBacktestInput(
        strategy_name=strategy_name,
        start_date="2023-01-01",
        end_date="2023-01-10"
    )
    result = usecase.execute(input_obj)
    summary = result["summary"]
    mock_strategy_repository.get_strategy.assert_called_once_with(strategy_name)
    usecase.engine.start.assert_called_once_with(mock_strategy, ANY, ANY)
    # Assert result is a dict with expected keys and formatted dates
    assert summary["start_date"] == "01-Jan-2023"
    assert summary["end_date"] == "10-Jan-2023"
    assert summary["strategy_name"] == strategy_name
    assert summary["total_trades_count"] == 5
    assert summary["winning_trades_count"] == 3
    assert summary["losing_trades_count"] == 2
    assert summary["winning_streak"] == 2
    assert summary["max_gain"] == fmt_currency(100.0)
    assert summary["max_loss"] == fmt_currency(-50.0)
    assert summary["total_pnl_points"] == fmt_currency(150.0)
    assert summary["total_pnl_percentage"] == fmt_percent(0.15)

def test_execute_missing_fields(usecase):
    input_obj = RunBacktestInput(strategy_name=None, start_date="2023-01-01", end_date="2023-01-10")
    with pytest.raises(ValueError) as excinfo:
        usecase.execute(input_obj)
    assert "Missing required fields" in str(excinfo.value)

def test_execute_invalid_start_date_format(usecase, mock_strategy_repository):
    input_obj = RunBacktestInput(strategy_name="test", start_date="invalid", end_date="2023-01-10")
    mock_strategy_repository.get_strategy.return_value = MagicMock()
    with pytest.raises(ValueError) as excinfo:
        usecase.execute(input_obj)
    assert "Invalid start_date format" in str(excinfo.value)

def test_execute_invalid_end_date_format(usecase, mock_strategy_repository):
    input_obj = RunBacktestInput(strategy_name="test", start_date="2023-01-01", end_date="bad-date")
    mock_strategy_repository.get_strategy.return_value = MagicMock()
    with pytest.raises(ValueError) as excinfo:
        usecase.execute(input_obj)
    assert "Invalid end_date format" in str(excinfo.value)

def test_execute_start_date_later_than_end_date(usecase, mock_strategy_repository):
    input_obj = RunBacktestInput(strategy_name="test", start_date="2023-01-10", end_date="2023-01-01")
    mock_strategy_repository.get_strategy.return_value = MagicMock()
    with pytest.raises(ValueError) as excinfo:
        usecase.execute(input_obj)
    assert "start_date cannot be later than end_date" in str(excinfo.value)

def test_execute_strategy_not_found(usecase, mock_strategy_repository):
    input_obj = RunBacktestInput(strategy_name="not_found", start_date="2023-01-01", end_date="2023-01-10")
    mock_strategy_repository.get_strategy.side_effect = FileNotFoundError("not found")
    with pytest.raises(FileNotFoundError):
        usecase.execute(input_obj)
