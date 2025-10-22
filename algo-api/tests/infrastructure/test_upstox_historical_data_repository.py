import pytest
from algo.domain.instrument.instrument import Exchange, Type
from algo.infrastructure.upstox.upstox_historical_data_repository import parse_timeframe
from algo.domain.timeframe import Timeframe
from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from algo.infrastructure.upstox.upstox_historical_data_repository import UpstoxHistoricalDataRepository
from algo.domain.instrument.instrument import Instrument
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
    return Instrument(type=Type.EQ, exchange=Exchange.NSE, instrument_key="NSE_EQ|INE467B01029")

@pytest.fixture
def timeframe():
    class DummyTimeframe:
        value = "5min"
    return DummyTimeframe()

@pytest.fixture
def repo():
    return UpstoxHistoricalDataRepository()

@patch("algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance")
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

@patch("algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance")
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

@patch("algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance")
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

@patch("algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance")
def test_get_historical_data_unexpected_exception(mock_api_instance, repo, instrument, timeframe):
    mock_api = MagicMock()
    mock_api.get_historical_candle_data1.side_effect = Exception("Some error")
    mock_api_instance.return_value = mock_api

    start = date(2024, 1, 1)
    end = date(2024, 1, 1)
    with pytest.raises(RuntimeError) as excinfo:
        repo.get_historical_data(instrument, start, end, timeframe)
    assert "Unexpected error" in str(excinfo.value)

def test_get_max_days_for_timeframe_minutes(repo):
    """Test max days calculation for minute intervals."""
    assert repo._get_max_days_for_timeframe(Timeframe.FIVE_MINUTES) == 28
    assert repo._get_max_days_for_timeframe(Timeframe.FIFTEEN_MINUTES) == 28
    
    # Test string format timeframes
    class MockTimeframe:
        def __init__(self, value):
            self.value = value
    
    assert repo._get_max_days_for_timeframe(MockTimeframe("30min")) == 28
    assert repo._get_max_days_for_timeframe(MockTimeframe("60m")) == 28
    assert repo._get_max_days_for_timeframe(MockTimeframe("30")) == 28

def test_get_max_days_for_timeframe_hours(repo):
    """Test max days calculation for hour intervals."""
    class MockTimeframe:
        def __init__(self, value):
            self.value = value
    
    assert repo._get_max_days_for_timeframe(MockTimeframe("1h")) == 28

def test_get_max_days_for_timeframe_days(repo):
    """Test max days calculation for day intervals."""
    assert repo._get_max_days_for_timeframe(Timeframe.ONE_DAY) == 3287

def test_get_max_days_for_timeframe_weeks(repo):
    """Test max days calculation for week intervals (no limit)."""
    class MockTimeframe:
        def __init__(self, value):
            self.value = value
    
    assert repo._get_max_days_for_timeframe(MockTimeframe("1w")) == 999999

def test_split_date_range_no_split_needed(repo):
    """Test date range splitting when no split is needed."""
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 15)  # 15 days
    max_days = 28
    
    segments = repo._split_date_range(start_date, end_date, max_days)
    assert len(segments) == 1
    assert segments[0] == (start_date, end_date)

def test_split_date_range_split_needed(repo):
    """Test date range splitting when split is needed."""
    start_date = date(2023, 1, 1)
    end_date = date(2023, 2, 15)  # 45 days
    max_days = 28
    
    segments = repo._split_date_range(start_date, end_date, max_days)
    assert len(segments) == 2
    assert segments[0] == (date(2023, 1, 1), date(2023, 1, 28))
    assert segments[1] == (date(2023, 1, 29), date(2023, 2, 15))

def test_split_date_range_multiple_splits(repo):
    """Test date range splitting with multiple segments."""
    start_date = date(2023, 1, 1)
    end_date = date(2023, 3, 30)  # ~88 days
    max_days = 28
    
    segments = repo._split_date_range(start_date, end_date, max_days)
    assert len(segments) == 4
    assert segments[0] == (date(2023, 1, 1), date(2023, 1, 28))
    assert segments[1] == (date(2023, 1, 29), date(2023, 2, 25))
    assert segments[2] == (date(2023, 2, 26), date(2023, 3, 25))
    assert segments[3] == (date(2023, 3, 26), date(2023, 3, 30))

def test_split_date_range_no_limit(repo):
    """Test date range splitting when there's no limit."""
    start_date = date(2023, 1, 1)
    end_date = date(2024, 1, 1)  # 1 year
    max_days = 999999  # No limit
    
    segments = repo._split_date_range(start_date, end_date, max_days)
    assert len(segments) == 1
    assert segments[0] == (start_date, end_date)

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_get_historical_data_single_segment(mock_api_instance, repo, instrument):
    """Test get_historical_data when only single API call is needed."""
    # Mock API response
    mock_response = MagicMock()
    mock_response.data.candles = [
        ["2023-01-01T09:15:00", 100, 105, 95, 102, 1000, 50],
        ["2023-01-01T09:30:00", 102, 108, 98, 105, 1200, 55]
    ]
    
    mock_api = MagicMock()
    mock_api.get_historical_candle_data1.return_value = mock_response
    mock_api_instance.return_value = mock_api
    
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 15)  # 15 days, within 28-day limit
    timeframe = Timeframe.FIVE_MINUTES
    
    result = repo.get_historical_data(instrument, start_date, end_date, timeframe)
    
    # Should make only one API call
    assert mock_api.get_historical_candle_data1.call_count == 1
    assert isinstance(result, HistoricalData)
    assert len(result.data) == 2

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_get_historical_data_multiple_segments(mock_api_instance, repo, instrument):
    """Test get_historical_data when multiple API calls are needed."""
    # Mock API responses for multiple segments
    mock_response1 = MagicMock()
    mock_response1.data.candles = [
        ["2023-01-01T09:15:00", 100, 105, 95, 102, 1000, 50]
    ]
    
    mock_response2 = MagicMock()
    mock_response2.data.candles = [
        ["2023-02-01T09:15:00", 105, 110, 100, 108, 1200, 55]
    ]
    
    mock_api = MagicMock()
    mock_api.get_historical_candle_data1.side_effect = [mock_response1, mock_response2]
    mock_api_instance.return_value = mock_api
    
    start_date = date(2023, 1, 1)
    end_date = date(2023, 2, 15)  # 45 days, exceeds 28-day limit
    timeframe = Timeframe.FIVE_MINUTES
    
    result = repo.get_historical_data(instrument, start_date, end_date, timeframe)
    
    # Should make two API calls
    assert mock_api.get_historical_candle_data1.call_count == 2
    assert isinstance(result, HistoricalData)
    assert len(result.data) == 2
    
    # Verify data is sorted chronologically
    assert result.data[0]["timestamp"].strftime("%Y-%m-%d") == "2023-01-01"
    assert result.data[1]["timestamp"].strftime("%Y-%m-%d") == "2023-02-01"

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_get_historical_data_parallel_execution(mock_api_instance, repo, instrument):
    """Test get_historical_data with parallel execution for multiple segments."""
    # Mock API responses for multiple segments
    mock_response1 = MagicMock()
    mock_response1.data.candles = [
        ["2023-01-01T09:15:00", 100, 105, 95, 102, 1000, 50],
        ["2023-01-01T09:30:00", 102, 108, 98, 105, 1200, 55]
    ]
    
    mock_response2 = MagicMock()
    mock_response2.data.candles = [
        ["2023-02-01T09:15:00", 105, 110, 100, 108, 1200, 55],
        ["2023-02-01T09:30:00", 108, 112, 104, 110, 1300, 60]
    ]
    
    mock_response3 = MagicMock()
    mock_response3.data.candles = [
        ["2023-03-01T09:15:00", 110, 115, 105, 112, 1400, 65]
    ]
    
    mock_api = MagicMock()
    mock_api.get_historical_candle_data1.side_effect = [mock_response1, mock_response2, mock_response3]
    mock_api_instance.return_value = mock_api
    
    start_date = date(2023, 1, 1)
    end_date = date(2023, 3, 15)  # ~73 days, requires 3 segments (28 days each)
    timeframe = Timeframe.FIVE_MINUTES
    
    result = repo.get_historical_data(instrument, start_date, end_date, timeframe)
    
    # Should make three API calls (one for each segment)
    assert mock_api.get_historical_candle_data1.call_count == 3
    assert isinstance(result, HistoricalData)
    assert len(result.data) == 5  # Total of 5 candles across all segments
    
    # Verify data is sorted chronologically
    timestamps = [item["timestamp"] for item in result.data]
    assert timestamps == sorted(timestamps)
    
    # Verify first and last timestamps
    assert result.data[0]["timestamp"].strftime("%Y-%m-%d") == "2023-01-01"
    assert result.data[-1]["timestamp"].strftime("%Y-%m-%d") == "2023-03-01"

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_get_historical_data_parallel_execution_with_exception(mock_api_instance, repo, instrument):
    """Test get_historical_data handles exceptions in parallel execution with retry logic."""
    from upstox_client.rest import ApiException
    
    # Mock one successful response and one that fails even after retries
    mock_response1 = MagicMock()
    mock_response1.data.candles = [
        ["2023-01-01T09:15:00", 100, 105, 95, 102, 1000, 50]
    ]
    
    mock_api = MagicMock()
    call_count = 0
    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_response1  # First segment succeeds
        else:
            # Second segment fails (will be retried 3 times)
            raise ApiException("Persistent API Error")
    
    mock_api.get_historical_candle_data1.side_effect = side_effect
    mock_api_instance.return_value = mock_api
    
    start_date = date(2023, 1, 1)
    end_date = date(2023, 2, 15)  # 45 days, requires 2 segments
    timeframe = Timeframe.FIVE_MINUTES
    
    # Should raise RuntimeError with new detailed error message format
    with pytest.raises(RuntimeError, match="Failed to fetch 1 out of 2 segments"):
        repo.get_historical_data(instrument, start_date, end_date, timeframe)

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_fetch_segment_with_metadata(mock_api_instance, repo, instrument):
    """Test the _fetch_segment_with_metadata wrapper method."""
    with patch.object(repo, '_fetch_historical_data_segment') as mock_fetch:
        mock_fetch.return_value = [{"test": "data"}]
        
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 15)
        timeframe = Timeframe.FIVE_MINUTES
        args = (instrument, start_date, end_date, timeframe)
        
        result_start_date, result_data = repo._fetch_segment_with_metadata(args)
        
        assert result_start_date == start_date
        assert result_data == [{"test": "data"}]
        mock_fetch.assert_called_once_with(instrument, start_date, end_date, timeframe)

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.time.sleep')
@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_fetch_segment_with_retry_success_after_failure(mock_api_instance, mock_sleep, repo, instrument):
    """Test _fetch_segment_with_retry succeeds after initial failures."""
    from upstox_client.rest import ApiException
    
    # Mock API responses: fail twice, then succeed
    mock_response = MagicMock()
    mock_response.data.candles = [
        ["2023-01-01T09:15:00", 100, 105, 95, 102, 1000, 50]
    ]
    
    mock_api = MagicMock()
    mock_api.get_historical_candle_data1.side_effect = [
        ApiException("Temporary API Error"),
        ApiException("Another Temporary Error"),
        mock_response  # Success on third attempt
    ]
    mock_api_instance.return_value = mock_api
    
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 15)
    timeframe = Timeframe.FIVE_MINUTES
    args = (instrument, start_date, end_date, timeframe)
    
    result_start_date, result_data = repo._fetch_segment_with_retry(args)
    
    # Should have made 3 API calls (2 failures + 1 success)
    assert mock_api.get_historical_candle_data1.call_count == 3
    assert result_start_date == start_date
    assert len(result_data) == 1
    
    # Should have slept twice (after first and second failures)
    assert mock_sleep.call_count == 2
    mock_sleep.assert_any_call(1)  # First retry wait
    mock_sleep.assert_any_call(2)  # Second retry wait

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.time.sleep')
@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_fetch_segment_with_retry_fails_after_max_attempts(mock_api_instance, mock_sleep, repo, instrument):
    """Test _fetch_segment_with_retry fails after maximum retry attempts."""
    from upstox_client.rest import ApiException
    
    mock_api = MagicMock()
    mock_api.get_historical_candle_data1.side_effect = ApiException("Persistent API Error")
    mock_api_instance.return_value = mock_api
    
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 15)
    timeframe = Timeframe.FIVE_MINUTES
    args = (instrument, start_date, end_date, timeframe)
    
    with pytest.raises(RuntimeError, match="Failed to fetch segment.*after 3 attempts"):
        repo._fetch_segment_with_retry(args)
    
    # Should have made 3 API calls (max retries)
    assert mock_api.get_historical_candle_data1.call_count == 3
    
    # Should have slept twice (after first and second failures, not after third)
    assert mock_sleep.call_count == 2

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_get_historical_data_parallel_with_retry_some_segments_fail(mock_api_instance, repo, instrument):
    """Test get_historical_data handles mixed success/failure scenarios with retry."""
    from upstox_client.rest import ApiException
    
    # Mock successful response for first segment
    mock_response1 = MagicMock()
    mock_response1.data.candles = [
        ["2023-01-01T09:15:00", 100, 105, 95, 102, 1000, 50]
    ]
    
    # Mock responses: first segment succeeds, second segment fails even after retries
    mock_api = MagicMock()
    call_count = 0
    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_response1  # First segment succeeds
        else:
            raise ApiException("Persistent Error")  # Second segment fails
    
    mock_api.get_historical_candle_data1.side_effect = side_effect
    mock_api_instance.return_value = mock_api
    
    start_date = date(2023, 1, 1)
    end_date = date(2023, 2, 15)  # 45 days, requires 2 segments
    timeframe = Timeframe.FIVE_MINUTES
    
    with pytest.raises(RuntimeError, match="Failed to fetch 1 out of 2 segments"):
        repo.get_historical_data(instrument, start_date, end_date, timeframe)

@patch('algo.infrastructure.upstox.upstox_historical_data_repository.UpstoxHistoricalDataRepository.api_instance')
def test_get_historical_data_parallel_with_retry_all_segments_succeed(mock_api_instance, repo, instrument):
    """Test get_historical_data succeeds when all segments succeed after retries."""
    from upstox_client.rest import ApiException
    
    # Mock responses for multiple segments
    mock_response1 = MagicMock()
    mock_response1.data.candles = [
        ["2023-01-01T09:15:00", 100, 105, 95, 102, 1000, 50]
    ]
    
    mock_response2 = MagicMock()
    mock_response2.data.candles = [
        ["2023-02-01T09:15:00", 105, 110, 100, 108, 1200, 55]
    ]
    
    mock_api = MagicMock()
    call_count = 0
    def side_effect(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return mock_response1  # First segment succeeds immediately
        elif call_count == 2:
            raise ApiException("Temporary Error")  # Second segment fails first time
        elif call_count == 3:
            return mock_response2  # Second segment succeeds on retry
    
    mock_api.get_historical_candle_data1.side_effect = side_effect
    mock_api_instance.return_value = mock_api
    
    start_date = date(2023, 1, 1)
    end_date = date(2023, 2, 15)  # 45 days, requires 2 segments
    timeframe = Timeframe.FIVE_MINUTES
    
    result = repo.get_historical_data(instrument, start_date, end_date, timeframe)
    
    # Should succeed and return combined data
    assert isinstance(result, HistoricalData)
    assert len(result.data) == 2

