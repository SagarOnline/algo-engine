import pytest
from unittest.mock import MagicMock, ANY
from algo_core.application.run_backtest_usecase import RunBacktestUseCase
from algo_core.application.run_backtest_usecase import RunBacktestInput

@pytest.fixture
def mock_historical_data_repository():
    return MagicMock()

@pytest.fixture
def mock_strategy_repository():
    return MagicMock()

@pytest.fixture
def usecase(mock_historical_data_repository, mock_strategy_repository):
    return RunBacktestUseCase(
        historical_data_repository=mock_historical_data_repository,
        strategy_repository=mock_strategy_repository
    )

def test_execute_success(usecase, mock_strategy_repository, mock_historical_data_repository):
    strategy_name = "test_strategy"
    payload = {
        "strategy_name": strategy_name
    }
    mock_strategy = MagicMock()
    mock_strategy_repository.get_strategy.return_value = mock_strategy
    mock_report = MagicMock()
    mock_report.to_dict.return_value = {"result": "success"}
    usecase.engine.start = MagicMock(return_value=mock_report)
    input_obj = RunBacktestInput(
        strategy_name=strategy_name,
        start_date="2023-01-01",
        end_date="2023-01-10"
    )
    result = usecase.execute(input_obj)
    mock_strategy_repository.get_strategy.assert_called_once_with(strategy_name)
    usecase.engine.start.assert_called_once_with(mock_strategy, ANY, ANY)
    assert result == {"result": "success"}

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
