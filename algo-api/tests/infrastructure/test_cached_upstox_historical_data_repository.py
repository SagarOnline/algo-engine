import pytest
from unittest.mock import Mock, MagicMock
from datetime import date, datetime
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.strategy.strategy import Instrument
from algo.domain.timeframe import Timeframe
from algo.infrastructure.cached_upstox_historical_data_repository import CachedUpstoxHistoricalDataRepository
from algo.infrastructure.upstox_historical_data_repository import UpstoxHistoricalDataRepository


@pytest.fixture
def mock_upstox_repository():
    """Create a mock UpstoxHistoricalDataRepository."""
    return Mock(spec=UpstoxHistoricalDataRepository)


@pytest.fixture
def sample_instrument():
    """Create a sample instrument for testing."""
    instrument = Mock(spec=Instrument)
    instrument.instrument_key = "NSE_EQ|INE002A01018"
    return instrument


@pytest.fixture
def sample_historical_data():
    """Create sample historical data for testing with date range Jan 1-31, 2024."""
    data = []
    for day in range(1, 32):  # Jan 1-31
        data.append({
            "timestamp": datetime(2024, 1, day, 9, 15),
            "open": 100.0 + day,
            "high": 105.0 + day,
            "low": 99.0 + day,
            "close": 103.0 + day,
            "volume": 1000 + day * 10,
            "oi": None
        })
    return HistoricalData(data)


@pytest.fixture
def extended_historical_data():
    """Create extended historical data for testing with date range Dec 15, 2023 - Feb 15, 2024."""
    data = []
    # December 2023 data (15-31)
    for day in range(15, 32):
        data.append({
            "timestamp": datetime(2023, 12, day, 9, 15),
            "open": 80.0 + day,
            "high": 85.0 + day,
            "low": 79.0 + day,
            "close": 83.0 + day,
            "volume": 800 + day * 10,
            "oi": None
        })
    
    # January 2024 data (1-31)
    for day in range(1, 32):
        data.append({
            "timestamp": datetime(2024, 1, day, 9, 15),
            "open": 100.0 + day,
            "high": 105.0 + day,
            "low": 99.0 + day,
            "close": 103.0 + day,
            "volume": 1000 + day * 10,
            "oi": None
        })
    
    # February 2024 data (1-15)
    for day in range(1, 16):
        data.append({
            "timestamp": datetime(2024, 2, day, 9, 15),
            "open": 120.0 + day,
            "high": 125.0 + day,
            "low": 119.0 + day,
            "close": 123.0 + day,
            "volume": 1200 + day * 10,
            "oi": None
        })
    
    return HistoricalData(data)


@pytest.fixture
def cached_repository(mock_upstox_repository):
    """Create a CachedUpstoxHistoricalDataRepository with mock dependency."""
    return CachedUpstoxHistoricalDataRepository(mock_upstox_repository)


class TestCachedUpstoxHistoricalDataRepository:
    """Test suite for CachedUpstoxHistoricalDataRepository with intelligent subset caching."""

    def test_initialization_with_provided_repository(self, mock_upstox_repository):
        """Test that the cached repository initializes with provided repository."""
        cached_repo = CachedUpstoxHistoricalDataRepository(mock_upstox_repository)
        
        assert cached_repo._upstox_repository is mock_upstox_repository
        assert cached_repo._cache == {}

    def test_initialization_without_repository(self):
        """Test that the cached repository creates its own repository when none provided."""
        cached_repo = CachedUpstoxHistoricalDataRepository()
        
        assert isinstance(cached_repo._upstox_repository, UpstoxHistoricalDataRepository)
        assert cached_repo._cache == {}

    def test_get_historical_data_cache_miss(self, cached_repository, mock_upstox_repository, 
                                          sample_instrument, sample_historical_data):
        """Test getting historical data when not in cache (cache miss)."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        timeframe = Timeframe.FIFTEEN_MINUTES
        
        # Setup mock to return sample data
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        # Call the method
        result = cached_repository.get_historical_data(sample_instrument, start_date, end_date, timeframe)
        
        # Verify the upstox repository was called
        mock_upstox_repository.get_historical_data.assert_called_once_with(
            sample_instrument, start_date, end_date, timeframe
        )
        
        # Verify the result is correct
        assert result is sample_historical_data
        
        # Verify data was cached
        assert cached_repository.get_cache_size() == 1
        assert cached_repository.is_cached(sample_instrument, timeframe)

    def test_get_historical_data_subset_from_cache(self, cached_repository, mock_upstox_repository,
                                                 sample_instrument, sample_historical_data):
        """Test getting subset of historical data from cache."""
        # First request: Jan 1-31
        full_start_date = date(2024, 1, 1)
        full_end_date = date(2024, 1, 31)
        timeframe = Timeframe.FIFTEEN_MINUTES
        
        # Setup mock to return sample data
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        # First call to populate cache
        first_result = cached_repository.get_historical_data(sample_instrument, full_start_date, full_end_date, timeframe)
        
        # Second call for subset: Jan 10-20 (should be served from cache)
        subset_start_date = date(2024, 1, 10)
        subset_end_date = date(2024, 1, 20)
        second_result = cached_repository.get_historical_data(sample_instrument, subset_start_date, subset_end_date, timeframe)
        
        # Verify the upstox repository was called only once
        assert mock_upstox_repository.get_historical_data.call_count == 1
        
        # Verify subset contains only data within the requested range
        subset_dates = [record["timestamp"].date() for record in second_result.data]
        assert all(subset_start_date <= date_val <= subset_end_date for date_val in subset_dates)

    def test_get_historical_data_extend_cache_range(self, cached_repository, mock_upstox_repository,
                                                   sample_instrument, sample_historical_data, extended_historical_data):
        """Test extending cached range when requested range exceeds cached range."""
        # First request: Jan 1-31
        initial_start_date = date(2024, 1, 1)
        initial_end_date = date(2024, 1, 31)
        timeframe = Timeframe.FIFTEEN_MINUTES

        # Setup mock to return sample data for first call
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        # First call to populate cache
        cached_repository.get_historical_data(sample_instrument, initial_start_date, initial_end_date, timeframe)
        
        # Second call requesting extended range: Dec 15, 2023 - Feb 15, 2024
        extended_start_date = date(2023, 12, 15)
        extended_end_date = date(2024, 2, 15)
        
        # Setup mock to return extended data for second call
        mock_upstox_repository.get_historical_data.return_value = extended_historical_data
        
        result = cached_repository.get_historical_data(sample_instrument, extended_start_date, extended_end_date, timeframe)
        
        # Verify the upstox repository was called twice (initial + extension)
        assert mock_upstox_repository.get_historical_data.call_count == 2
        
        # Verify the second call was made with extended range
        second_call_args = mock_upstox_repository.get_historical_data.call_args_list[1]
        assert second_call_args[0][1] == extended_start_date  # start_date
        assert second_call_args[0][2] == extended_end_date    # end_date

    def test_can_serve_from_cache(self, cached_repository, mock_upstox_repository,
                                 sample_instrument, sample_historical_data):
        """Test can_serve_from_cache method."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        timeframe = Timeframe.FIFTEEN_MINUTES
        
        # Initially cannot serve from cache
        assert not cached_repository.can_serve_from_cache(sample_instrument, start_date, end_date, timeframe)
        
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        # After caching, can serve exact range
        cached_repository.get_historical_data(sample_instrument, start_date, end_date, timeframe)
        assert cached_repository.can_serve_from_cache(sample_instrument, start_date, end_date, timeframe)
        
        # Can serve subset
        subset_start = date(2024, 1, 10)
        subset_end = date(2024, 1, 20)
        assert cached_repository.can_serve_from_cache(sample_instrument, subset_start, subset_end, timeframe)
        
        # Cannot serve extended range
        extended_start = date(2023, 12, 1)
        extended_end = date(2024, 2, 28)
        assert not cached_repository.can_serve_from_cache(sample_instrument, extended_start, extended_end, timeframe)

    def test_get_cached_date_range(self, cached_repository, mock_upstox_repository,
                                  sample_instrument, sample_historical_data):
        """Test get_cached_date_range method."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        timeframe = Timeframe.FIFTEEN_MINUTES
        
        # Initially no cached range
        assert cached_repository.get_cached_date_range(sample_instrument, timeframe) is None
        
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        # After caching, should return cached range
        cached_repository.get_historical_data(sample_instrument, start_date, end_date, timeframe)
        cached_range = cached_repository.get_cached_date_range(sample_instrument, timeframe)
        assert cached_range == (start_date, end_date)

    def test_different_timeframes_separate_cache(self, cached_repository, mock_upstox_repository,
                                               sample_instrument, sample_historical_data):
        """Test that different timeframes are cached separately."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        timeframe_15min = Timeframe.FIFTEEN_MINUTES
        timeframe_5min = Timeframe.FIVE_MINUTES
        
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        # Get data for both timeframes
        cached_repository.get_historical_data(sample_instrument, start_date, end_date, timeframe_15min)
        cached_repository.get_historical_data(sample_instrument, start_date, end_date, timeframe_5min)
        
        # Should have called upstox repository twice (different cache entries)
        assert mock_upstox_repository.get_historical_data.call_count == 2
        assert cached_repository.get_cache_size() == 2

    def test_remove_from_cache(self, cached_repository, mock_upstox_repository,
                              sample_instrument, sample_historical_data):
        """Test removing specific instrument-timeframe from cache."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        timeframe = Timeframe.FIFTEEN_MINUTES
        
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        # Populate cache
        cached_repository.get_historical_data(sample_instrument, start_date, end_date, timeframe)
        assert cached_repository.get_cache_size() == 1
        
        # Remove from cache
        removed = cached_repository.remove_from_cache(sample_instrument, timeframe)
        assert removed is True
        assert cached_repository.get_cache_size() == 0
        assert not cached_repository.is_cached(sample_instrument, timeframe)

    def test_get_cache_stats(self, cached_repository, mock_upstox_repository,
                           sample_instrument, sample_historical_data):
        """Test get_cache_stats method."""
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        initial_stats = cached_repository.get_cache_stats()
        assert initial_stats["cached_combinations"] == 0
        assert initial_stats["total_instruments"] == 0
        
        # Add one entry
        cached_repository.get_historical_data(sample_instrument, date(2024, 1, 1), 
                                            date(2024, 1, 31), Timeframe.FIFTEEN_MINUTES)
        
        stats = cached_repository.get_cache_stats()
        assert stats["cached_combinations"] == 1
        assert stats["total_instruments"] == 1
        assert stats["total_timeframes"] == 1
        assert stats["total_records"] == len(sample_historical_data.data)

    def test_extract_subset_with_datetime_objects(self, cached_repository):
        """Test _extract_subset method with datetime objects."""
        # Create test data with datetime objects
        test_data = HistoricalData([
            {"timestamp": datetime(2024, 1, 10, 9, 15), "open": 100, "high": 105, "low": 99, "close": 103, "volume": 1000},
            {"timestamp": datetime(2024, 1, 15, 9, 15), "open": 101, "high": 106, "low": 100, "close": 104, "volume": 1100},
            {"timestamp": datetime(2024, 1, 20, 9, 15), "open": 102, "high": 107, "low": 101, "close": 105, "volume": 1200},
        ])
        
        # Extract subset for Jan 12-18
        subset = cached_repository._extract_subset(test_data, date(2024, 1, 12), date(2024, 1, 18))
        
        # Should only contain the Jan 15 record
        assert len(subset.data) == 1
        assert subset.data[0]["timestamp"] == datetime(2024, 1, 15, 9, 15)

    def test_get_cache_info(self, cached_repository, mock_upstox_repository,
                           sample_instrument, sample_historical_data):
        """Test get_cache_info method."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        timeframe = Timeframe.FIFTEEN_MINUTES
        
        mock_upstox_repository.get_historical_data.return_value = sample_historical_data
        
        # Populate cache
        cached_repository.get_historical_data(sample_instrument, start_date, end_date, timeframe)
        
        cache_info = cached_repository.get_cache_info()
        assert "cached_data" in cache_info
        assert len(cache_info["cached_data"]) == 1
        
        cache_entry = cache_info["cached_data"][0]
        assert cache_entry["instrument_key"] == sample_instrument.instrument_key
        assert cache_entry["start_date"] == start_date.isoformat()
        assert cache_entry["end_date"] == end_date.isoformat()
        assert cache_entry["record_count"] == len(sample_historical_data.data)
