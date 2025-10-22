"""
Example usage of CachedUpstoxHistoricalDataRepository with Intelligent Subset Caching

This file demonstrates how to use the cached repository to avoid redundant API calls
by caching complete historical data and serving subsets from memory.
"""

from datetime import date
from algo.infrastructure.upstox.cached_upstox_historical_data_repository import CachedUpstoxHistoricalDataRepository
from algo.infrastructure.upstox.upstox_historical_data_repository import UpstoxHistoricalDataRepository
from algo.domain.strategy.strategy import Instrument
from algo.domain.timeframe import Timeframe


def example_intelligent_caching():
    """Demonstrate intelligent subset caching functionality."""
    
    cached_repo = CachedUpstoxHistoricalDataRepository()
    
    # Create a sample instrument
    instrument = Instrument(
        instrument_key="NSE_EQ|INE002A01018",  # Example: Reliance
        name="RELIANCE",
        exchange="NSE",
        instrument_type="EQ"
    )
    
    timeframe = Timeframe.MINUTE_15
    
    print("=== Intelligent Subset Caching Demo ===")
    
    # 1. First request: Get data for entire January 2024
    print("\n1. First request - Full month (Jan 1-31, 2024)")
    jan_start = date(2024, 1, 1)
    jan_end = date(2024, 1, 31)
    
    print(f"Cache size before: {cached_repo.get_cache_size()}")
    print(f"Can serve from cache: {cached_repo.can_serve_from_cache(instrument, jan_start, jan_end, timeframe)}")
    
    # This will make an API call and cache the entire month's data
    data_full_month = cached_repo.get_historical_data(instrument, jan_start, jan_end, timeframe)
    print(f"✓ Fetched {len(data_full_month.data)} records from API")
    print(f"Cache size after: {cached_repo.get_cache_size()}")
    
    cached_range = cached_repo.get_cached_date_range(instrument, timeframe)
    print(f"Cached date range: {cached_range}")
    
    # 2. Second request: Get subset data for mid-January (Jan 10-20, 2024)
    print("\n2. Second request - Subset (Jan 10-20, 2024)")
    subset_start = date(2024, 1, 10)
    subset_end = date(2024, 1, 20)
    
    print(f"Can serve from cache: {cached_repo.can_serve_from_cache(instrument, subset_start, subset_end, timeframe)}")
    
    # This will be served from cache - NO API call
    data_subset = cached_repo.get_historical_data(instrument, subset_start, subset_end, timeframe)
    print(f"✓ Served {len(data_subset.data)} records from CACHE")
    print(f"Cache size (unchanged): {cached_repo.get_cache_size()}")
    
    # 3. Third request: Get another subset for early January (Jan 5-15, 2024)
    print("\n3. Third request - Another subset (Jan 5-15, 2024)")
    another_subset_start = date(2024, 1, 5)
    another_subset_end = date(2024, 1, 15)
    
    print(f"Can serve from cache: {cached_repo.can_serve_from_cache(instrument, another_subset_start, another_subset_end, timeframe)}")
    
    # This will also be served from cache - NO API call
    data_another_subset = cached_repo.get_historical_data(instrument, another_subset_start, another_subset_end, timeframe)
    print(f"✓ Served {len(data_another_subset.data)} records from CACHE")


def example_cache_extension():
    """Demonstrate cache extension when requesting data beyond cached range."""
    
    cached_repo = CachedUpstoxHistoricalDataRepository()
    
    instrument = Instrument(
        instrument_key="NSE_EQ|INE001A01018",  # Example: TCS
        name="TCS",
        exchange="NSE",
        instrument_type="EQ"
    )
    
    timeframe = Timeframe.MINUTE_15
    
    print("\n=== Cache Extension Demo ===")
    
    # 1. First request: Get data for January 2024
    print("\n1. Initial request - January 2024")
    jan_start = date(2024, 1, 1)
    jan_end = date(2024, 1, 31)
    
    data_jan = cached_repo.get_historical_data(instrument, jan_start, jan_end, timeframe)
    print(f"✓ Cached January data: {len(data_jan.data)} records")
    print(f"Cached range: {cached_repo.get_cached_date_range(instrument, timeframe)}")
    
    # 2. Second request: Get data for Dec 2023 - Feb 2024 (extends cache in both directions)
    print("\n2. Extended request - Dec 2023 to Feb 2024")
    extended_start = date(2023, 12, 1)
    extended_end = date(2024, 2, 29)
    
    print(f"Can serve from cache: {cached_repo.can_serve_from_cache(instrument, extended_start, extended_end, timeframe)}")
    
    # This will extend the cache by making a new API call
    data_extended = cached_repo.get_historical_data(instrument, extended_start, extended_end, timeframe)
    print(f"✓ Extended cache with {len(data_extended.data)} records")
    print(f"New cached range: {cached_repo.get_cached_date_range(instrument, timeframe)}")
    
    # 3. Third request: Get subset within extended range - should be served from cache
    print("\n3. Subset request within extended range - January 15-25, 2024")
    subset_start = date(2024, 1, 15)
    subset_end = date(2024, 1, 25)
    
    print(f"Can serve from cache: {cached_repo.can_serve_from_cache(instrument, subset_start, subset_end, timeframe)}")
    
    data_subset = cached_repo.get_historical_data(instrument, subset_start, subset_end, timeframe)
    print(f"✓ Served {len(data_subset.data)} records from CACHE")


def example_multiple_instruments_and_timeframes():
    """Demonstrate caching with multiple instruments and timeframes."""
    
    cached_repo = CachedUpstoxHistoricalDataRepository()
    
    # Create multiple instruments
    reliance = Instrument(instrument_key="NSE_EQ|INE002A01018", name="RELIANCE")
    tcs = Instrument(instrument_key="NSE_EQ|INE001A01018", name="TCS")
    hdfc = Instrument(instrument_key="NSE_EQ|INE040A01034", name="HDFC")
    
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    print("\n=== Multiple Instruments & Timeframes Demo ===")
    
    # Cache data for different instruments and timeframes
    instruments = [reliance, tcs, hdfc]
    timeframes = [Timeframe.MINUTE_5, Timeframe.MINUTE_15, Timeframe.HOUR_1]
    
    print(f"\nCaching data for {len(instruments)} instruments x {len(timeframes)} timeframes...")
    
    for instrument in instruments:
        for timeframe in timeframes:
            data = cached_repo.get_historical_data(instrument, start_date, end_date, timeframe)
            print(f"✓ Cached {instrument.name} {timeframe}: {len(data.data) if data.data else 0} records")
    
    print(f"\nTotal cache combinations: {cached_repo.get_cache_size()}")
    
    # Get cache statistics
    stats = cached_repo.get_cache_stats()
    print(f"Cache stats: {stats}")
    
    # Get detailed cache info
    cache_info = cached_repo.get_cache_info()
    print(f"\nDetailed cache info:")
    for entry in cache_info["cached_data"]:
        print(f"  {entry['instrument_key']} | {entry['timeframe']} | "
              f"{entry['start_date']} to {entry['end_date']} | "
              f"{entry['record_count']} records")


def example_cache_management():
    """Demonstrate cache management features."""
    
    cached_repo = CachedUpstoxHistoricalDataRepository()
    
    instrument = Instrument(instrument_key="NSE_EQ|INE002A01018", name="RELIANCE")
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    print("\n=== Cache Management Demo ===")
    
    # Populate cache with different timeframes
    timeframes = [Timeframe.MINUTE_5, Timeframe.MINUTE_15, Timeframe.HOUR_1]
    
    for timeframe in timeframes:
        cached_repo.get_historical_data(instrument, start_date, end_date, timeframe)
        print(f"✓ Cached {timeframe}")
    
    print(f"\nCache size: {cached_repo.get_cache_size()}")
    
    # Check what's cached
    for timeframe in timeframes:
        is_cached = cached_repo.is_cached(instrument, timeframe)
        cached_range = cached_repo.get_cached_date_range(instrument, timeframe)
        print(f"{timeframe} cached: {is_cached}, range: {cached_range}")
    
    # Remove specific timeframe from cache
    print(f"\nRemoving {Timeframe.MINUTE_5} from cache...")
    removed = cached_repo.remove_from_cache(instrument, Timeframe.MINUTE_5)
    print(f"Removed: {removed}")
    print(f"Cache size: {cached_repo.get_cache_size()}")
    
    # Clear entire cache
    print(f"\nClearing entire cache...")
    cached_repo.clear_cache()
    print(f"Cache size: {cached_repo.get_cache_size()}")


if __name__ == "__main__":
    print("🚀 CachedUpstoxHistoricalDataRepository - Intelligent Subset Caching Examples")
    
    # Run all examples
    example_intelligent_caching()
    example_cache_extension()
    example_multiple_instruments_and_timeframes()
    example_cache_management()
    
    print("\n✅ All examples completed!")
    print("\n💡 Key Benefits:")
    print("   • One API call can serve multiple subset requests")
    print("   • Automatic cache extension when needed")
    print("   • Separate caching per instrument-timeframe combination")
    print("   • Memory-efficient subset extraction")
    print("   • Intelligent range checking before API calls")
