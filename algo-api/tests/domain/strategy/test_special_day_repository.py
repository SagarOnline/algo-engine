"""
Test cases for the SpecialDayRepository interface and JsonSpecialDayRepository implementation.

This module contains comprehensive tests for the special day management system.
"""

import pytest
import tempfile
import json
from datetime import date, time
from pathlib import Path

from algo.domain.strategy.special_day_repository import (
    DayType, 
    SpecialDay, 
    SpecialDayRepository
)
from algo.domain.strategy.strategy import Exchange
from algo.infrastructure.json_special_day_repository import JsonSpecialDayRepository


class TestSpecialDay:
    """Test cases for the SpecialDay class."""
    
    def test_holiday_creation(self):
        """Test creating a holiday special day."""
        holiday = SpecialDay(
            date=date(2023, 1, 1),
            day_type=DayType.HOLIDAY,
            description="New Year's Day"
        )
        
        assert holiday.date == date(2023, 1, 1)
        assert holiday.day_type == DayType.HOLIDAY
        assert holiday.description == "New Year's Day"
        assert holiday.trading_start is None
        assert holiday.trading_end is None
        assert holiday.metadata == {}
        assert holiday.is_holiday()
        assert not holiday.is_special_trading_day()
        assert not holiday.has_custom_trading_hours()
    
    def test_special_trading_day_creation(self):
        """Test creating a special trading day."""
        trading_day = SpecialDay(
            date=date(2023, 12, 24),
            day_type=DayType.SPECIAL_TRADING_DAY,
            description="Christmas Eve - Early Close",
            trading_start=time(9, 15),
            trading_end=time(13, 0),
            metadata={"early_close": True}
        )
        
        assert trading_day.date == date(2023, 12, 24)
        assert trading_day.day_type == DayType.SPECIAL_TRADING_DAY
        assert trading_day.description == "Christmas Eve - Early Close"
        assert trading_day.trading_start == time(9, 15)
        assert trading_day.trading_end == time(13, 0)
        assert trading_day.metadata == {"early_close": True}
        assert not trading_day.is_holiday()
        assert trading_day.is_special_trading_day()
        assert trading_day.has_custom_trading_hours()
    
    def test_holiday_with_trading_hours_raises_error(self):
        """Test that creating a holiday with trading hours raises an error."""
        with pytest.raises(ValueError, match="Holidays cannot have trading hours"):
            SpecialDay(
                date=date(2023, 1, 1),
                day_type=DayType.HOLIDAY,
                description="New Year's Day",
                trading_start=time(9, 15)
            )
    
    def test_special_trading_day_with_partial_hours_raises_error(self):
        """Test that creating a special trading day with only start or end time raises an error."""
        with pytest.raises(ValueError, match="must have both start and end times"):
            SpecialDay(
                date=date(2023, 12, 24),
                day_type=DayType.SPECIAL_TRADING_DAY,
                description="Christmas Eve",
                trading_start=time(9, 15)  # Missing trading_end
            )


class TestJsonSpecialDayRepository:
    """Test cases for the JsonSpecialDayRepository class."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample special day data for testing."""
        return [
            {
                "date": "2023-01-01",
                "day_type": "HOLIDAY",
                "description": "New Year's Day",
                "metadata": {"category": "national"}
            },
            {
                "date": "2023-12-24",
                "day_type": "SPECIAL_TRADING_DAY",
                "description": "Christmas Eve - Early Close",
                "trading_start": "09:15:00",
                "trading_end": "13:00:00",
                "metadata": {"early_close": True}
            },
            {
                "date": "2024-01-01",
                "day_type": "HOLIDAY",
                "description": "New Year's Day 2024",
                "metadata": {"category": "national"}
            }
        ]
    
    @pytest.fixture
    def temp_json_file(self, sample_data):
        """Create a temporary JSON file with sample data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_data, f)
            temp_file_path = f.name
        
        yield temp_file_path
        
        # Cleanup
        Path(temp_file_path).unlink(missing_ok=True)
    
    def test_repository_initialization(self, temp_json_file):
        """Test repository initialization with valid JSON file."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        assert repo.json_path == Path(temp_json_file)
        assert len(repo._cache) > 0
    
    def test_repository_initialization_directory_mode(self, tmp_path):
        """Test repository initialization with directory containing exchange-year files."""
        # Create a temporary directory with exchange-year files
        special_day_dir = tmp_path / "special_days"
        special_day_dir.mkdir()
        
        # Create nse_2023.json
        nse_2023_data = [
            {
                "date": "2023-01-01",
                "day_type": "HOLIDAY", 
                "description": "New Year's Day",
                "metadata": {"category": "national"}
            }
        ]
        nse_file = special_day_dir / "nse_2023.json"
        with open(nse_file, 'w') as f:
            json.dump(nse_2023_data, f)
        
        repo = JsonSpecialDayRepository(str(special_day_dir))
        assert repo._is_directory_mode
        assert Exchange.NSE.value in repo._cache
        assert 2023 in repo._cache[Exchange.NSE.value]
    
    def test_repository_initialization_file_not_found(self):
        """Test repository initialization with non-existent file."""
        with pytest.raises(FileNotFoundError):
            JsonSpecialDayRepository("non_existent_file.json")
    
    def test_get_special_days_for_year(self, temp_json_file):
        """Test retrieving special days for a specific year."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        
        # Test 2023 data
        days_2023 = repo.get_special_days_for_year(2023)
        assert len(days_2023) == 2
        assert days_2023[0].date == date(2023, 1, 1)
        assert days_2023[1].date == date(2023, 12, 24)
        
        # Test 2024 data
        days_2024 = repo.get_special_days_for_year(2024)
        assert len(days_2024) == 1
        assert days_2024[0].date == date(2024, 1, 1)
        
        # Test year with no data
        days_2025 = repo.get_special_days_for_year(2025)
        assert len(days_2025) == 0
    
    def test_get_special_days_invalid_year(self, temp_json_file):
        """Test retrieving special days for invalid year."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        
        with pytest.raises(ValueError, match="Invalid year"):
            repo.get_special_days_for_year(1800)
        
        with pytest.raises(ValueError, match="Invalid year"):
            repo.get_special_days_for_year(2200)
    
    def test_get_special_day(self, temp_json_file):
        """Test retrieving a specific special day."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        
        # Test existing special day
        special_day = repo.get_special_day(date(2023, 1, 1))
        assert special_day is not None
        assert special_day.description == "New Year's Day"
        assert special_day.day_type == DayType.HOLIDAY
        
        # Test non-existent special day
        regular_day = repo.get_special_day(date(2023, 6, 15))
        assert regular_day is None
    
    def test_get_holidays(self, temp_json_file):
        """Test retrieving holidays for a specific year."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        
        holidays_2023 = repo.get_holidays(2023)
        assert len(holidays_2023) == 1
        assert holidays_2023[0].day_type == DayType.HOLIDAY
        assert holidays_2023[0].description == "New Year's Day"
    
    def test_get_special_trading_days(self, temp_json_file):
        """Test retrieving special trading days for a specific year."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        
        trading_days_2023 = repo.get_special_trading_days(2023)
        assert len(trading_days_2023) == 1
        assert trading_days_2023[0].day_type == DayType.SPECIAL_TRADING_DAY
        assert trading_days_2023[0].description == "Christmas Eve - Early Close"
        assert trading_days_2023[0].trading_start == time(9, 15)
        assert trading_days_2023[0].trading_end == time(13, 0)
    
    def test_convenience_methods(self, temp_json_file):
        """Test convenience methods for checking special days."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        
        # Test holiday check
        assert repo.is_holiday(date(2023, 1, 1))
        assert not repo.is_holiday(date(2023, 6, 15))
        
        # Test special trading day check
        assert repo.is_special_trading_day(date(2023, 12, 24))
        assert not repo.is_special_trading_day(date(2023, 1, 1))
        
        # Test trading hours retrieval
        trading_hours = repo.get_trading_hours(date(2023, 12, 24))
        assert trading_hours == (time(9, 15), time(13, 0))
        
        no_hours = repo.get_trading_hours(date(2023, 1, 1))
        assert no_hours is None
    
    def test_cache_stats(self, temp_json_file):
        """Test cache statistics."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        
        stats = repo.get_cache_stats()
        assert stats['exchanges'][Exchange.NSE.value]['years_loaded'] == [2023, 2024]
        assert stats['total_special_days'] == 3
        assert stats['total_holidays'] == 2
        assert stats['total_special_trading_days'] == 1
    
    def test_refresh_cache(self, temp_json_file):
        """Test cache refresh functionality."""
        repo = JsonSpecialDayRepository(temp_json_file, exchange=Exchange.NSE)
        
        initial_stats = repo.get_cache_stats()
        
        # Refresh cache (should be no-op if file hasn't changed)
        repo.refresh_cache()
        
        refreshed_stats = repo.get_cache_stats()
        assert initial_stats == refreshed_stats
    
    def test_invalid_json_format(self):
        """Test handling of invalid JSON format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Invalid JSON format"):
                JsonSpecialDayRepository(temp_file_path, exchange=Exchange.NSE)
        finally:
            Path(temp_file_path).unlink(missing_ok=True)
    
    def test_invalid_data_structure(self):
        """Test handling of invalid data structure."""
        invalid_data = {"not": "a list"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file_path = f.name
        
        try:
            with pytest.raises(ValueError, match="must contain an array"):
                JsonSpecialDayRepository(temp_file_path, exchange=Exchange.NSE)
        finally:
            Path(temp_file_path).unlink(missing_ok=True)
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        invalid_data = [
            {
                "day_type": "HOLIDAY",
                "description": "Missing date field"
                # Missing 'date' field
            }
        ]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Missing required field"):
                JsonSpecialDayRepository(temp_file_path, exchange=Exchange.NSE)
        finally:
            Path(temp_file_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__])
