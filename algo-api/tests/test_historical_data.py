import pytest
from datetime import datetime
from algo.domain.backtest.historical_data import HistoricalData

def test_getCandleBy_returns_candle_when_exists():
    data = [
        {"timestamp": "2023-01-01T09:15:00", "close": 100},
        {"timestamp": "2023-01-01T09:30:00", "close": 110},
    ]
    hd = HistoricalData(data)
    result = hd.getCandleBy("2023-01-01T09:30:00")
    assert result == {"timestamp": "2023-01-01T09:30:00", "close": 110}

def test_getCandleBy_returns_candle_when_exists_datetime():
    data = [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 100},
        {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 110},
    ]
    hd = HistoricalData(data)
    result = hd.getCandleBy("2023-01-01T09:30:00")
    assert result == {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 110}

def test_getCandleBy_returns_none_when_not_exists():
    data = [
        {"timestamp": "2023-01-01T09:15:00", "close": 100},
        {"timestamp": "2023-01-01T09:30:00", "close": 110},
    ]
    hd = HistoricalData(data)
    result = hd.getCandleBy("2023-01-01T10:00:00")
    assert result is None


# Tests for filter() function

@pytest.fixture
def sample_data():
    """Sample historical data with datetime timestamps for testing filter function"""
    return [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 100, "open": 98},
        {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 110, "open": 105},
        {"timestamp": datetime(2023, 1, 1, 9, 45), "close": 105, "open": 108},
        {"timestamp": datetime(2023, 1, 1, 10, 0), "close": 115, "open": 107},
        {"timestamp": datetime(2023, 1, 1, 10, 15), "close": 120, "open": 115},
    ]


def test_filter_both_none_returns_all_data(sample_data):
    """Test that filter returns all data when both start and end are None"""
    hd = HistoricalData(sample_data)
    result = hd.filter(start=None, end=None)
    assert result == sample_data
    assert len(result) == 5


def test_filter_start_none_filters_by_end(sample_data):
    """Test that filter returns data <= end when start is None"""
    hd = HistoricalData(sample_data)
    end_time = datetime(2023, 1, 1, 9, 45)
    result = hd.filter(start=None, end=end_time)
    
    assert len(result) == 3
    assert result[0]["timestamp"] == datetime(2023, 1, 1, 9, 15)
    assert result[1]["timestamp"] == datetime(2023, 1, 1, 9, 30)
    assert result[2]["timestamp"] == datetime(2023, 1, 1, 9, 45)


def test_filter_end_none_filters_by_start(sample_data):
    """Test that filter returns data >= start when end is None"""
    hd = HistoricalData(sample_data)
    start_time = datetime(2023, 1, 1, 9, 45)
    result = hd.filter(start=start_time, end=None)
    
    assert len(result) == 3
    assert result[0]["timestamp"] == datetime(2023, 1, 1, 9, 45)
    assert result[1]["timestamp"] == datetime(2023, 1, 1, 10, 0)
    assert result[2]["timestamp"] == datetime(2023, 1, 1, 10, 15)


def test_filter_both_provided_filters_range_inclusive(sample_data):
    """Test that filter returns data in range [start, end] when both are provided"""
    hd = HistoricalData(sample_data)
    start_time = datetime(2023, 1, 1, 9, 30)
    end_time = datetime(2023, 1, 1, 10, 0)
    result = hd.filter(start=start_time, end=end_time)
    
    assert len(result) == 3
    assert result[0]["timestamp"] == datetime(2023, 1, 1, 9, 30)
    assert result[1]["timestamp"] == datetime(2023, 1, 1, 9, 45)
    assert result[2]["timestamp"] == datetime(2023, 1, 1, 10, 0)


def test_filter_exact_boundary_times(sample_data):
    """Test that filter includes exact boundary times (inclusive)"""
    hd = HistoricalData(sample_data)
    start_time = datetime(2023, 1, 1, 9, 30)
    end_time = datetime(2023, 1, 1, 9, 30)
    result = hd.filter(start=start_time, end=end_time)
    
    assert len(result) == 1
    assert result[0]["timestamp"] == datetime(2023, 1, 1, 9, 30)
    assert result[0]["close"] == 110


def test_filter_no_matches_returns_empty_list(sample_data):
    """Test that filter returns empty list when no data matches criteria"""
    hd = HistoricalData(sample_data)
    start_time = datetime(2023, 1, 1, 11, 0)  # After all data
    end_time = datetime(2023, 1, 1, 11, 30)
    result = hd.filter(start=start_time, end=end_time)
    
    assert result == []
    assert len(result) == 0


def test_filter_handles_missing_timestamps():
    """Test that filter handles missing timestamps gracefully"""
    data = [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 100},
        {"close": 110},  # Missing timestamp
        {"timestamp": datetime(2023, 1, 1, 9, 45), "close": 105},
        {"timestamp": None, "close": 115},  # None timestamp
    ]
    hd = HistoricalData(data)
    start_time = datetime(2023, 1, 1, 9, 0)
    end_time = datetime(2023, 1, 1, 10, 0)
    result = hd.filter(start=start_time, end=end_time)
    
    # Should only include records with valid timestamps
    assert len(result) == 2
    assert result[0]["timestamp"] == datetime(2023, 1, 1, 9, 15)
    assert result[1]["timestamp"] == datetime(2023, 1, 1, 9, 45)


def test_filter_empty_data():
    """Test that filter handles empty data gracefully"""
    hd = HistoricalData([])
    start_time = datetime(2023, 1, 1, 9, 0)
    end_time = datetime(2023, 1, 1, 10, 0)
    result = hd.filter(start=start_time, end=end_time)
    
    assert result == []
    assert len(result) == 0


def test_filter_preserves_original_data_structure(sample_data):
    """Test that filter preserves all fields in the original data"""
    hd = HistoricalData(sample_data)
    start_time = datetime(2023, 1, 1, 9, 30)
    end_time = datetime(2023, 1, 1, 9, 30)
    result = hd.filter(start=start_time, end=end_time)
    
    assert len(result) == 1
    candle = result[0]
    assert "timestamp" in candle
    assert "close" in candle
    assert "open" in candle
    assert candle["timestamp"] == datetime(2023, 1, 1, 9, 30)
    assert candle["close"] == 110
    assert candle["open"] == 105


def test_filter_does_not_modify_original_data(sample_data):
    """Test that filter does not modify the original data"""
    original_length = len(sample_data)
    hd = HistoricalData(sample_data)
    
    # Filter to get subset
    start_time = datetime(2023, 1, 1, 9, 30)
    end_time = datetime(2023, 1, 1, 9, 45)
    result = hd.filter(start=start_time, end=end_time)
    
    # Original data should be unchanged
    assert len(hd.data) == original_length
    assert hd.data == sample_data
    assert len(result) == 2  # Filtered result


def test_filter_inverted_range_returns_empty():
    """Test that filter returns empty list when start > end"""
    data = [
        {"timestamp": datetime(2023, 1, 1, 9, 15), "close": 100},
        {"timestamp": datetime(2023, 1, 1, 9, 30), "close": 110},
    ]
    hd = HistoricalData(data)
    start_time = datetime(2023, 1, 1, 10, 0)  # After end time
    end_time = datetime(2023, 1, 1, 9, 0)     # Before start time
    result = hd.filter(start=start_time, end=end_time)
    
    assert result == []
    assert len(result) == 0
