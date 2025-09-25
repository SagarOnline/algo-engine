import pytest
from algo.infrastructure.upstox_historical_data_repository import parse_timeframe
from algo.domain.timeframe import Timeframe
from unittest.mock import patch, MagicMock
from datetime import date
from algo.infrastructure.upstox_historical_data_repository import UpstoxHistoricalDataRepository
from algo.domain.strategy.strategy import Exchange, Instrument, InstrumentType
from algo.domain.timeframe import Timeframe
from algo.domain.backtest.historical_data import HistoricalData



def test_parse_timeframe_min():
    assert parse_timeframe(Timeframe.FIFTEEN_MINUTES) == ("15", "minutes")
    assert parse_timeframe(Timeframe.FIVE_MINUTES) == ("5", "minutes")
    assert parse_timeframe("30min") == ("30", "minutes")
    assert parse_timeframe("1m") == ("1", "minutes")
    assert parse_timeframe("60m") == ("60", "minutes")
    assert parse_timeframe("120") == ("120", "minutes")

def test_parse_timeframe_hour():
    assert parse_timeframe("1h") == ("60", "minutes")
    assert parse_timeframe("2h") == ("120", "minutes")

def test_parse_timeframe_day_week():
    assert parse_timeframe("1d") == ("1", "days")
    assert parse_timeframe("2d") == ("2", "days")
    assert parse_timeframe("1w") == ("1", "weeks")
    assert parse_timeframe("3w") == ("3", "weeks")

def test_parse_timeframe_invalid():
    with pytest.raises(ValueError):
        parse_timeframe("foo")
    with pytest.raises(ValueError):
        parse_timeframe("")
        
@pytest.fixture
def instrument():
    return Instrument(InstrumentType.STOCK,Exchange.NSE, instrument_key="NSE_EQ|INE467B01029")

@pytest.fixture
def timeframe():
    class DummyTimeframe:
        value = "5min"
    return DummyTimeframe()

@pytest.fixture
def repo():
    return UpstoxHistoricalDataRepository()

@patch("algo.infrastructure.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance")
def test_get_historical_data_success(mock_api_instance, repo, instrument, timeframe):
    mock_api = MagicMock()
    mock_response = MagicMock()
    mock_response.data.candles = [
         ["2024-01-01T09:20:00+05:30", 105, 115, 100, 110, 1200, 12],
        ["2024-01-01T09:15:00+05:30", 100, 110, 95, 105, 1000, 10]
       
    ]
    mock_api.get_historical_candle_data1.return_value = mock_response
    mock_api_instance.return_value = mock_api

    start = date(2024, 1, 1)
    end = date(2024, 1, 1)
    result = repo.get_historical_data(instrument, start, end, timeframe)
    assert isinstance(result, HistoricalData)
    assert len(result.data) == 2
    assert result.data[0]["open"] == 100
    assert result.data[1]["close"] == 110

@patch("algo.infrastructure.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance")
def test_get_historical_data_empty(mock_api_instance, repo, instrument, timeframe):
    mock_api = MagicMock()
    mock_response = MagicMock()
    mock_response.data.candles = []
    mock_api.get_historical_candle_data1.return_value = mock_response
    mock_api_instance.return_value = mock_api

    start = date(2024, 1, 1)
    end = date(2024, 1, 1)
    result = repo.get_historical_data(instrument, start, end, timeframe)
    assert isinstance(result, HistoricalData)
    assert result.data == []

@patch("algo.infrastructure.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance")
def test_get_historical_data_api_exception(mock_api_instance, repo, instrument, timeframe):
    mock_api = MagicMock()
    from upstox_client.rest import ApiException
    mock_api.get_historical_candle_data1.side_effect = ApiException("API error")
    mock_api_instance.return_value = mock_api

    start = date(2024, 1, 1)
    end = date(2024, 1, 1)
    with pytest.raises(RuntimeError) as excinfo:
        repo.get_historical_data(instrument, start, end, timeframe)
    assert "Exception when calling Upstox API" in str(excinfo.value)

@patch("algo.infrastructure.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance")
def test_get_historical_data_unexpected_exception(mock_api_instance, repo, instrument, timeframe):
    mock_api = MagicMock()
    mock_api.get_historical_candle_data1.side_effect = Exception("Some error")
    mock_api_instance.return_value = mock_api

    start = date(2024, 1, 1)
    end = date(2024, 1, 1)
    with pytest.raises(RuntimeError) as excinfo:
        repo.get_historical_data(instrument, start, end, timeframe)
    assert "Unexpected error" in str(excinfo.value)

