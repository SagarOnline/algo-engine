from datetime import date, datetime
from typing import Dict, Tuple, List, Optional
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.instrument.instrument import Instrument
from algo.domain.timeframe import Timeframe
from algo.infrastructure.upstox.upstox_historical_data_repository import UpstoxHistoricalDataRepository


class CachedUpstoxHistoricalDataRepository(HistoricalDataRepository):
    """
    A cached wrapper around UpstoxHistoricalDataRepository that stores complete historical data
    in memory and returns subsets without making additional API calls when requested date ranges
    fall within the cached data range.
    """
    
    def __init__(self, upstox_repository: UpstoxHistoricalDataRepository = None):
        """
        Initialize the cached repository with an optional Upstox repository instance.
        
        Args:
            upstox_repository: The underlying Upstox repository. If None, creates a new instance.
        """
        self._upstox_repository = upstox_repository or UpstoxHistoricalDataRepository()
        # Cache structure: {(instrument_key, timeframe): (start_date, end_date, HistoricalData)}
        self._cache: Dict[Tuple[str, str], Tuple[date, date, HistoricalData]] = {}
    
    def get_historical_data(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> HistoricalData:
        """
        Get historical data for an instrument. If a superset of the requested data is already cached,
        returns the subset from memory. Otherwise, fetches from Upstox API and caches the result.
        
        Args:
            instrument: The trading instrument
            start_date: Start date for historical data
            end_date: End date for historical data
            timeframe: The timeframe for the data
            
        Returns:
            HistoricalData: The cached subset or freshly retrieved historical data
        """
        cache_key = self._generate_cache_key(instrument, timeframe)
        
        # Check if we have cached data for this instrument and timeframe
        if cache_key in self._cache:
            cached_start, cached_end, cached_data = self._cache[cache_key]
            
            # Check if requested range is within cached range
            if start_date >= cached_start and end_date <= cached_end:
                # Return subset from cached data
                return self._extract_subset(cached_data, start_date, end_date)
            
            # Check if we need to extend the cached range
            extended_start = min(start_date, cached_start)
            extended_end = max(end_date, cached_end)
            
            # If the gap is significant, fetch the extended range
            if (start_date < cached_start) or (end_date > cached_end):
                # Fetch extended range and update cache
                extended_data = self._upstox_repository.get_historical_data(
                    instrument, extended_start, extended_end, timeframe
                )
                self._cache[cache_key] = (extended_start, extended_end, extended_data)
                return self._extract_subset(extended_data, start_date, end_date)
        
        # No cached data or need fresh data - fetch from Upstox API
        historical_data = self._upstox_repository.get_historical_data(instrument, start_date, end_date, timeframe)
        self._cache[cache_key] = (start_date, end_date, historical_data)
        
        return historical_data
    
    def _generate_cache_key(self, instrument: Instrument, timeframe: Timeframe) -> Tuple[str, str]:
        """
        Generate a cache key for the given instrument and timeframe.
        
        Args:
            instrument: The trading instrument
            timeframe: The timeframe for the data
            
        Returns:
            Tuple[str, str]: A cache key tuple (instrument_key, timeframe_str)
        """
        timeframe_str = timeframe.value if hasattr(timeframe, 'value') else str(timeframe)
        return (instrument.instrument_key, timeframe_str)
    
    def _extract_subset(self, historical_data: HistoricalData, start_date: date, end_date: date) -> HistoricalData:
        """
        Extract a subset of historical data based on the requested date range.
        
        Args:
            historical_data: The complete historical data
            start_date: Start date for the subset
            end_date: End date for the subset
            
        Returns:
            HistoricalData: The filtered subset of data
        """
        if not historical_data.data:
            return HistoricalData([])
        
        filtered_data = []
        for record in historical_data.data:
            record_date = record["timestamp"]
            # Handle both datetime and string timestamps
            if isinstance(record_date, str):
                record_date = datetime.fromisoformat(record_date).date()
            elif isinstance(record_date, datetime):
                record_date = record_date.date()
            
            if start_date <= record_date <= end_date:
                filtered_data.append(record)
        
        return HistoricalData(filtered_data)
    
    def clear_cache(self) -> None:
        """Clear all cached historical data."""
        self._cache.clear()
    
    def remove_from_cache(self, instrument: Instrument, timeframe: Timeframe) -> bool:
        """
        Remove cached historical data for a specific instrument and timeframe.
        
        Args:
            instrument: The trading instrument
            timeframe: The timeframe for the data
            
        Returns:
            bool: True if item was removed, False if it wasn't in cache
        """
        cache_key = self._generate_cache_key(instrument, timeframe)
        if cache_key in self._cache:
            del self._cache[cache_key]
            return True
        return False
    
    def get_cache_size(self) -> int:
        """Get the number of cached instrument-timeframe combinations."""
        return len(self._cache)
    
    def is_cached(self, instrument: Instrument, timeframe: Timeframe) -> bool:
        """
        Check if historical data for given instrument and timeframe is cached.
        
        Args:
            instrument: The trading instrument
            timeframe: The timeframe for the data
            
        Returns:
            bool: True if data is cached, False otherwise
        """
        cache_key = self._generate_cache_key(instrument, timeframe)
        return cache_key in self._cache
    
    def get_cached_date_range(self, instrument: Instrument, timeframe: Timeframe) -> Optional[Tuple[date, date]]:
        """
        Get the cached date range for a specific instrument and timeframe.
        
        Args:
            instrument: The trading instrument
            timeframe: The timeframe for the data
            
        Returns:
            Optional[Tuple[date, date]]: The cached date range (start_date, end_date) or None if not cached
        """
        cache_key = self._generate_cache_key(instrument, timeframe)
        if cache_key in self._cache:
            cached_start, cached_end, _ = self._cache[cache_key]
            return (cached_start, cached_end)
        return None
    
    def can_serve_from_cache(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> bool:
        """
        Check if the requested date range can be served from cache without API call.
        
        Args:
            instrument: The trading instrument
            start_date: Start date for historical data
            end_date: End date for historical data
            timeframe: The timeframe for the data
            
        Returns:
            bool: True if request can be served from cache, False otherwise
        """
        cache_key = self._generate_cache_key(instrument, timeframe)
        if cache_key in self._cache:
            cached_start, cached_end, _ = self._cache[cache_key]
            return start_date >= cached_start and end_date <= cached_end
        return False
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, int]: Dictionary containing cache statistics
        """
        total_records = 0
        for _, _, historical_data in self._cache.values():
            total_records += len(historical_data.data) if historical_data.data else 0
            
        return {
            "cached_combinations": self.get_cache_size(),
            "total_instruments": len(set(key[0] for key in self._cache.keys())),
            "total_timeframes": len(set(key[1] for key in self._cache.keys())),
            "total_records": total_records
        }
    
    def preload_cache(self, requests: List[Tuple[Instrument, date, date, Timeframe]]) -> None:
        """
        Preload cache with multiple historical data requests.
        
        Args:
            requests: List of tuples (instrument, start_date, end_date, timeframe)
        """
        for instrument, start_date, end_date, timeframe in requests:
            self.get_historical_data(instrument, start_date, end_date, timeframe)
    
    def get_cache_info(self) -> Dict[str, List[Dict]]:
        """
        Get detailed information about cached data.
        
        Returns:
            Dict containing detailed cache information
        """
        cache_info = []
        for (instrument_key, timeframe_str), (start_date, end_date, historical_data) in self._cache.items():
            cache_info.append({
                "instrument_key": instrument_key,
                "timeframe": timeframe_str,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "record_count": len(historical_data.data) if historical_data.data else 0
            })
        
        return {"cached_data": cache_info}
