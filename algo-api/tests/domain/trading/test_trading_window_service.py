"""
Tests for the TradingWindowService and TradingWindow classes.
"""
import pytest
from datetime import date, time, datetime

from algo.domain.trading.trading_window import TradingWindow, TradingWindowType
from algo.domain.trading.trading_window_service import TradingWindowService


class TestTradingWindow:
    """Test cases for the TradingWindow class."""
    
    def test_regular_trading_window_creation(self):
        """Test creating a regular trading window."""
        window = TradingWindow(
            date=date(2024, 11, 5),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.DEFAULT,
            open_time=time(9, 15),
            close_time=time(15, 30),
            description="Regular trading day"
        )
        
        assert window.date == date(2024, 11, 5)
        assert window.exchange == "NSE"
        assert window.segment == "FNO"
        assert window.window_type == TradingWindowType.DEFAULT
        assert window.open_time == time(9, 15)
        assert window.close_time == time(15, 30)
        assert window.is_regular_trading_day
        assert not window.is_holiday
        assert not window.is_special_trading_day
    
    def test_holiday_trading_window_creation(self):
        """Test creating a holiday trading window."""
        window = TradingWindow(
            date=date(2024, 12, 25),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.HOLIDAY,
            open_time=None,
            close_time=None,
            description="Christmas"
        )
        
        assert window.is_holiday
        assert not window.is_regular_trading_day
        assert not window.is_special_trading_day
        assert window.open_time is None
        assert window.close_time is None
    
    def test_special_trading_window_creation(self):
        """Test creating a special trading window."""
        window = TradingWindow(
            date=date(2024, 11, 1),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.SPECIAL,
            open_time=time(18, 0),
            close_time=time(19, 0),
            description="Muhurat Trading"
        )
        
        assert window.is_special_trading_day
        assert not window.is_holiday
        assert not window.is_regular_trading_day
        assert window.open_time == time(18, 0)
        assert window.close_time == time(19, 0)
    
    def test_holiday_with_trading_hours_raises_error(self):
        """Test that creating a holiday with trading hours raises an error."""
        with pytest.raises(ValueError, match="Holiday trading windows cannot have open/close times"):
            TradingWindow(
                date=date(2024, 12, 25),
                exchange="NSE",
                segment="FNO",
                window_type=TradingWindowType.HOLIDAY,
                open_time=time(9, 15),
                close_time=time(15, 30),
                description="Christmas"
            )
    
    def test_trading_window_without_times_raises_error(self):
        """Test that creating a non-holiday window without times raises an error."""
        with pytest.raises(ValueError, match="Non-holiday trading windows must have both open and close times"):
            TradingWindow(
                date=date(2024, 11, 5),
                exchange="NSE",
                segment="FNO",
                window_type=TradingWindowType.DEFAULT,
                open_time=None,
                close_time=None,
                description="Regular trading day"
            )
    
    def test_invalid_time_order_raises_error(self):
        """Test that open time after close time raises an error."""
        with pytest.raises(ValueError, match="Open time must be before close time"):
            TradingWindow(
                date=date(2024, 11, 5),
                exchange="NSE",
                segment="FNO",
                window_type=TradingWindowType.DEFAULT,
                open_time=time(15, 30),
                close_time=time(9, 15),
                description="Invalid times"
            )
    
    def test_trading_duration_calculation(self):
        """Test trading duration calculation."""
        window = TradingWindow(
            date=date(2024, 11, 5),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.DEFAULT,
            open_time=time(9, 15),
            close_time=time(15, 30),
            description="Regular trading day"
        )
        
        # 9:15 to 15:30 = 6 hours 15 minutes = 375 minutes
        assert window.get_trading_duration_minutes() == 375
    
    def test_holiday_duration_is_none(self):
        """Test that holiday duration is None."""
        window = TradingWindow(
            date=date(2024, 12, 25),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.HOLIDAY,
            open_time=None,
            close_time=None,
            description="Christmas"
        )
        
        assert window.get_trading_duration_minutes() is None
    
    def test_market_open_check(self):
        """Test market open time checking."""
        window = TradingWindow(
            date=date(2024, 11, 5),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.DEFAULT,
            open_time=time(9, 15),
            close_time=time(15, 30),
            description="Regular trading day"
        )
        
        assert window.is_market_open_at(time(9, 15))  # Open time
        assert window.is_market_open_at(time(12, 0))  # During market hours
        assert window.is_market_open_at(time(15, 30))  # Close time
        assert not window.is_market_open_at(time(9, 0))  # Before open
        assert not window.is_market_open_at(time(16, 0))  # After close
    
    def test_to_dict_conversion(self):
        """Test conversion to dictionary."""
        window = TradingWindow(
            date=date(2024, 11, 5),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.DEFAULT,
            open_time=time(9, 15),
            close_time=time(15, 30),
            description="Regular trading day",
            metadata={"test": "value"}
        )
        
        dict_repr = window.to_dict()
        
        assert dict_repr["date"] == "2024-11-05"
        assert dict_repr["exchange"] == "NSE"
        assert dict_repr["segment"] == "FNO"
        assert dict_repr["window_type"] == "DEFAULT"
        assert dict_repr["open_time"] == "09:15"
        assert dict_repr["close_time"] == "15:30"
        assert dict_repr["description"] == "Regular trading day"
        assert dict_repr["metadata"] == {"test": "value"}
    
    def test_from_dict_creation(self):
        """Test creation from dictionary."""
        data = {
            "date": "2024-11-05",
            "exchange": "NSE",
            "segment": "FNO",
            "window_type": "DEFAULT",
            "open_time": "09:15",
            "close_time": "15:30",
            "description": "Regular trading day",
            "metadata": {"test": "value"}
        }
        
        window = TradingWindow.from_dict(data)
        
        assert window.date == date(2024, 11, 5)
        assert window.exchange == "NSE"
        assert window.segment == "FNO"
        assert window.window_type == TradingWindowType.DEFAULT
        assert window.open_time == time(9, 15)
        assert window.close_time == time(15, 30)
        assert window.description == "Regular trading day"
        assert window.metadata == {"test": "value"}
    
    def test_is_within_trading_window_normal_trading_day(self):
        """Test is_within_trading_window for a normal trading day."""
        window = TradingWindow(
            date=date(2024, 11, 5),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.DEFAULT,
            open_time=time(9, 15),
            close_time=time(15, 30),
            description="Regular trading day"
        )
        
        # Test within trading hours
        assert window.is_within_trading_window(datetime(2024, 11, 5, 10, 30))  # Mid-day
        assert window.is_within_trading_window(datetime(2024, 11, 5, 9, 15))   # Exact open
        assert window.is_within_trading_window(datetime(2024, 11, 5, 15, 30))  # Exact close
        assert window.is_within_trading_window(datetime(2024, 11, 5, 12, 0))   # Noon
        
        # Test outside trading hours
        assert not window.is_within_trading_window(datetime(2024, 11, 5, 9, 14))   # Before open
        assert not window.is_within_trading_window(datetime(2024, 11, 5, 15, 31))  # After close
        assert not window.is_within_trading_window(datetime(2024, 11, 5, 8, 0))    # Early morning
        assert not window.is_within_trading_window(datetime(2024, 11, 5, 16, 0))   # Evening
        
        # Test different date
        assert not window.is_within_trading_window(datetime(2024, 11, 6, 10, 30))  # Next day
        assert not window.is_within_trading_window(datetime(2024, 11, 4, 10, 30))  # Previous day
    
    def test_is_within_trading_window_holiday(self):
        """Test is_within_trading_window for a holiday."""
        holiday_window = TradingWindow(
            date=date(2024, 12, 25),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.HOLIDAY,
            open_time=None,
            close_time=None,
            description="Christmas"
        )
        
        # All times should return False for holidays
        assert not holiday_window.is_within_trading_window(datetime(2024, 12, 25, 9, 15))
        assert not holiday_window.is_within_trading_window(datetime(2024, 12, 25, 10, 30))
        assert not holiday_window.is_within_trading_window(datetime(2024, 12, 25, 15, 30))
        assert not holiday_window.is_within_trading_window(datetime(2024, 12, 25, 0, 0))
        assert not holiday_window.is_within_trading_window(datetime(2024, 12, 25, 23, 59))
        
        # Different date should also be False
        assert not holiday_window.is_within_trading_window(datetime(2024, 12, 24, 10, 30))
    
    def test_is_within_trading_window_special_trading_day(self):
        """Test is_within_trading_window for a special trading day."""
        special_window = TradingWindow(
            date=date(2024, 11, 1),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.SPECIAL,
            open_time=time(18, 0),
            close_time=time(19, 0),
            description="Muhurat Trading"
        )
        
        # Test within special trading hours
        assert special_window.is_within_trading_window(datetime(2024, 11, 1, 18, 0))   # Exact open
        assert special_window.is_within_trading_window(datetime(2024, 11, 1, 18, 30))  # Mid-session
        assert special_window.is_within_trading_window(datetime(2024, 11, 1, 19, 0))   # Exact close
        
        # Test outside special trading hours
        assert not special_window.is_within_trading_window(datetime(2024, 11, 1, 17, 59))  # Before open
        assert not special_window.is_within_trading_window(datetime(2024, 11, 1, 19, 1))   # After close
        assert not special_window.is_within_trading_window(datetime(2024, 11, 1, 9, 15))   # Normal trading hours
        assert not special_window.is_within_trading_window(datetime(2024, 11, 1, 15, 30))  # Normal trading hours
        
        # Test different date
        assert not special_window.is_within_trading_window(datetime(2024, 11, 2, 18, 30))
    
    def test_is_within_trading_window_weekly_holiday(self):
        """Test is_within_trading_window for a weekly holiday (weekend)."""
        # Create a trading window that represents a weekly holiday (Saturday)
        weekly_holiday_window = TradingWindow(
            date=date(2024, 11, 2),  # Saturday
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.HOLIDAY,
            open_time=None,
            close_time=None,
            description="Weekly Holiday",
            metadata={"weekly_holiday": True}
        )
        
        # All times should return False for weekly holidays
        assert not weekly_holiday_window.is_within_trading_window(datetime(2024, 11, 2, 9, 15))
        assert not weekly_holiday_window.is_within_trading_window(datetime(2024, 11, 2, 10, 30))
        assert not weekly_holiday_window.is_within_trading_window(datetime(2024, 11, 2, 15, 30))
        assert not weekly_holiday_window.is_within_trading_window(datetime(2024, 11, 2, 12, 0))
        
        # Different date should also be False
        assert not weekly_holiday_window.is_within_trading_window(datetime(2024, 11, 1, 10, 30))
    
    def test_is_within_trading_window_edge_cases(self):
        """Test edge cases for is_within_trading_window."""
        window = TradingWindow(
            date=date(2024, 11, 5),
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.DEFAULT,
            open_time=time(9, 15),
            close_time=time(15, 30),
            description="Regular trading day"
        )
        
        # Test exact boundary times
        assert window.is_within_trading_window(datetime(2024, 11, 5, 9, 15, 0))    # Exact open with seconds
        assert window.is_within_trading_window(datetime(2024, 11, 5, 15, 30, 0))   # Exact close with seconds
        
        # Test microseconds before/after boundaries
        assert not window.is_within_trading_window(datetime(2024, 11, 5, 9, 14, 59))   # 1 second before
        assert not window.is_within_trading_window(datetime(2024, 11, 5, 15, 30, 1))   # 1 second after
        
        # Test with different timezone-aware datetimes (should work the same as they use .time())
        from datetime import timezone
        utc_tz = timezone.utc
        assert window.is_within_trading_window(datetime(2024, 11, 5, 10, 30, tzinfo=utc_tz))
    
    def test_is_within_trading_window_budget_day_special(self):
        """Test is_within_trading_window for Budget Day special trading (from 2025 config)."""
        budget_day_window = TradingWindow(
            date=date(2025, 2, 1),  # Saturday Budget Day
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.SPECIAL,
            open_time=time(9, 0),
            close_time=time(13, 0),
            description="Union Budget Day (Saturday)"
        )
        
        # Test within special budget trading hours
        assert budget_day_window.is_within_trading_window(datetime(2025, 2, 1, 9, 0))    # Exact open
        assert budget_day_window.is_within_trading_window(datetime(2025, 2, 1, 11, 0))   # Mid-session
        assert budget_day_window.is_within_trading_window(datetime(2025, 2, 1, 13, 0))   # Exact close
        
        # Test outside budget trading hours
        assert not budget_day_window.is_within_trading_window(datetime(2025, 2, 1, 8, 59))   # Before open
        assert not budget_day_window.is_within_trading_window(datetime(2025, 2, 1, 13, 1))   # After close
        assert not budget_day_window.is_within_trading_window(datetime(2025, 2, 1, 15, 30))  # Normal close time
        
        # Test different date
        assert not budget_day_window.is_within_trading_window(datetime(2025, 2, 2, 11, 0))
    
    def test_is_within_trading_window_muhurat_trading_special(self):
        """Test is_within_trading_window for Muhurat Trading special session (from 2025 config)."""
        muhurat_window = TradingWindow(
            date=date(2025, 10, 21),  # Saturday Muhurat Trading
            exchange="NSE",
            segment="FNO",
            window_type=TradingWindowType.SPECIAL,
            open_time=time(13, 45),
            close_time=time(14, 45),
            description="Muhurat Trading (Saturday)"
        )
        
        # Test within Muhurat trading hours
        assert muhurat_window.is_within_trading_window(datetime(2025, 10, 21, 13, 45))  # Exact open
        assert muhurat_window.is_within_trading_window(datetime(2025, 10, 21, 14, 15))  # Mid-session
        assert muhurat_window.is_within_trading_window(datetime(2025, 10, 21, 14, 45))  # Exact close
        
        # Test outside Muhurat trading hours
        assert not muhurat_window.is_within_trading_window(datetime(2025, 10, 21, 13, 44))  # Before open
        assert not muhurat_window.is_within_trading_window(datetime(2025, 10, 21, 14, 46))  # After close
        assert not muhurat_window.is_within_trading_window(datetime(2025, 10, 21, 9, 15))   # Normal open time
        assert not muhurat_window.is_within_trading_window(datetime(2025, 10, 21, 15, 30))  # Normal close time
        
        # Test different date
        assert not muhurat_window.is_within_trading_window(datetime(2025, 10, 22, 14, 15))


class TestTradingWindowService:
    """Test cases for the TradingWindowService class."""
    
    @pytest.fixture
    def sample_config_data(self):
        """Sample trading window configuration data."""
        return {
            "exchange": "NSE",
            "segment": "FNO",
            "year": 2024,
            "default_trading_windows": [
                {
                    "effective_from": None,
                    "effective_to": None,
                    "open_time": "09:15",
                    "close_time": "15:30"
                }
            ],
            "weekly_holidays": [
                {
                    "day_of_week": "SATURDAY"
                },
                {
                    "day_of_week": "SUNDAY"
                }
            ],
            "special_days": [
                {
                    "date": "2024-11-01",
                    "description": "Muhurat Trading",
                    "open_time": "18:00",
                    "close_time": "19:00"
                }
            ],
            "holidays": [
                {
                    "date": "2024-12-25",
                    "description": "Christmas"
                },
                {
                    "date": "2024-01-26",
                    "description": "Republic Day"
                }
            ]
        }
    
    @pytest.fixture
    def config_data_without_weekly_holidays(self):
        """Sample config data without weekly holidays for comparison tests."""
        return {
            "exchange": "BSE",
            "segment": "EQ",
            "year": 2024,
            "default_trading_windows": [
                {
                    "effective_from": None,
                    "effective_to": None,
                    "open_time": "09:15",
                    "close_time": "15:30"
                }
            ],
            "holidays": []
        }
    
    @pytest.fixture
    def config_data_list(self, sample_config_data):
        """Sample configuration data list for TradingWindowService."""
        return [sample_config_data]
    
    def test_service_initialization(self, config_data_list):
        """Test service initialization with valid config data."""
        service = TradingWindowService(config_data_list)
        
        assert service.config_data_list == config_data_list
        
        # Check that configuration was loaded
        exchanges_segments = service.get_available_exchanges_segments()
        assert ("NSE", "FNO") in exchanges_segments
        
        years = service.get_available_years("NSE", "FNO")
        assert 2024 in years
    
    def test_service_initialization_empty_config(self):
        """Test service initialization with empty configuration data."""
        service = TradingWindowService([])
        
        # Should initialize successfully but have no data
        exchanges_segments = service.get_available_exchanges_segments()
        assert len(exchanges_segments) == 0
    
    def test_service_initialization_invalid_config(self):
        """Test service initialization with invalid configuration data."""
        invalid_config = [
            {
                "exchange": "NSE",
                # Missing required fields like 'segment', 'year', etc.
                "invalid_field": "value"
            }
        ]
        
        with pytest.raises(ValueError, match="Invalid configuration data"):
            TradingWindowService(invalid_config)
    
    def test_get_holiday_trading_window(self, config_data_list):
        """Test retrieving a holiday trading window."""
        service = TradingWindowService(config_data_list)
        
        christmas = date(2024, 12, 25)
        window = service.get_trading_window(christmas, "NSE", "FNO")
        
        assert window is not None
        assert window.is_holiday
        assert window.description == "Christmas"
        assert window.open_time is None
        assert window.close_time is None
    
    def test_get_special_trading_window(self, config_data_list):
        """Test retrieving a special trading day window."""
        service = TradingWindowService(config_data_list)
        
        muhurat_date = date(2024, 11, 1)
        window = service.get_trading_window(muhurat_date, "NSE", "FNO")
        
        assert window is not None
        assert window.is_special_trading_day
        assert window.description == "Muhurat Trading"
        assert window.open_time == time(18, 0)
        assert window.close_time == time(19, 0)
    
    def test_get_default_trading_window(self, config_data_list):
        """Test retrieving a default trading window."""
        service = TradingWindowService(config_data_list)
        
        regular_date = date(2024, 11, 5)  # A regular trading day
        window = service.get_trading_window(regular_date, "NSE", "FNO")
        
        assert window is not None
        assert window.is_regular_trading_day
        assert window.open_time == time(9, 15)
        assert window.close_time == time(15, 30)
        assert window.description == "Regular trading day"
    
    def test_is_holiday_check(self, config_data_list):
        """Test holiday checking."""
        service = TradingWindowService(config_data_list)
        
        assert service.is_holiday(date(2024, 12, 25), "NSE", "FNO")  # Christmas
        assert service.is_holiday(date(2024, 1, 26), "NSE", "FNO")   # Republic Day
        assert not service.is_holiday(date(2024, 11, 5), "NSE", "FNO")  # Regular day
    
    def test_is_special_trading_day_check(self, config_data_list):
        """Test special trading day checking."""
        service = TradingWindowService(config_data_list)
        
        assert service.is_special_trading_day(date(2024, 11, 1), "NSE", "FNO")  # Muhurat
        assert not service.is_special_trading_day(date(2024, 12, 25), "NSE", "FNO")  # Holiday
        assert not service.is_special_trading_day(date(2024, 11, 5), "NSE", "FNO")   # Regular
    
    def test_get_trading_hours(self, config_data_list):
        """Test trading hours retrieval."""
        service = TradingWindowService(config_data_list)
        
        # Regular trading day
        regular_hours = service.get_trading_hours(date(2024, 11, 5), "NSE", "FNO")
        assert regular_hours == (time(9, 15), time(15, 30))
        
        # Special trading day
        special_hours = service.get_trading_hours(date(2024, 11, 1), "NSE", "FNO")
        assert special_hours == (time(18, 0), time(19, 0))
        
        # Holiday (no trading)
        holiday_hours = service.get_trading_hours(date(2024, 12, 25), "NSE", "FNO")
        assert holiday_hours is None
    
    def test_get_holidays(self, config_data_list):
        """Test retrieving all holidays for a year."""
        service = TradingWindowService(config_data_list)
        
        holidays = service.get_holidays(2024, "NSE", "FNO")
        
        assert len(holidays) == 2
        assert holidays[0].date == date(2024, 1, 26)  # Republic Day (sorted by date)
        assert holidays[1].date == date(2024, 12, 25)  # Christmas
        
        for holiday in holidays:
            assert holiday.is_holiday
    
    def test_get_special_trading_days(self, config_data_list):
        """Test retrieving all special trading days for a year."""
        service = TradingWindowService(config_data_list)
        
        special_days = service.get_special_trading_days(2024, "NSE", "FNO")
        
        assert len(special_days) == 1
        assert special_days[0].date == date(2024, 11, 1)  # Muhurat Trading
        assert special_days[0].is_special_trading_day
    
    def test_get_cache_stats(self, config_data_list):
        """Test cache statistics retrieval."""
        service = TradingWindowService(config_data_list)
        
        stats = service.get_cache_stats()
        
        assert stats["total_exchange_segments"] == 1
        assert "NSE-FNO" in stats["exchange_segments"]
        
        nse_fno_stats = stats["exchange_segments"]["NSE-FNO"]
        assert nse_fno_stats["exchange"] == "NSE"
        assert nse_fno_stats["segment"] == "FNO"
        assert nse_fno_stats["years_loaded"] == [2024]
        assert nse_fno_stats["total_holidays"] == 2
        assert nse_fno_stats["total_special_days"] == 1
    
    def test_non_existent_exchange_segment(self, config_data_list):
        """Test querying non-existent exchange-segment combination."""
        service = TradingWindowService(config_data_list)
        
        window = service.get_trading_window(date(2024, 11, 5), "BSE", "EQ")
        assert window is None
        
        assert not service.is_holiday(date(2024, 12, 25), "BSE", "EQ")
        assert service.get_trading_hours(date(2024, 11, 5), "BSE", "EQ") is None
        assert service.get_holidays(2024, "BSE", "EQ") == []
    
    def test_weekly_holidays_validation_valid_config(self):
        """Test validation of valid weekly holidays configuration."""
        valid_config = [{
            "exchange": "NSE",
            "segment": "FNO",
            "year": 2024,
            "default_trading_windows": [{"open_time": "09:15", "close_time": "15:30"}],
            "weekly_holidays": [
                {"day_of_week": "SATURDAY"},
                {"day_of_week": "SUNDAY"}
            ]
        }]
        
        # Should not raise any exception
        service = TradingWindowService(valid_config)
        assert service is not None
    
    def test_weekly_holidays_validation_invalid_day_name(self):
        """Test validation failure for invalid day names in weekly holidays."""
        invalid_config = [{
            "exchange": "NSE",
            "segment": "FNO",
            "year": 2024,
            "default_trading_windows": [{"open_time": "09:15", "close_time": "15:30"}],
            "weekly_holidays": [
                {"day_of_week": "INVALID_DAY"}
            ]
        }]
        
        with pytest.raises(ValueError, match="Weekly holiday 'day_of_week' must be one of"):
            TradingWindowService(invalid_config)
    
    def test_weekly_holidays_validation_missing_day_of_week(self):
        """Test validation failure for missing day_of_week field."""
        invalid_config = [{
            "exchange": "NSE",
            "segment": "FNO",
            "year": 2024,
            "default_trading_windows": [{"open_time": "09:15", "close_time": "15:30"}],
            "weekly_holidays": [
                {"invalid_field": "SATURDAY"}
            ]
        }]
        
        with pytest.raises(ValueError, match="Weekly holiday missing 'day_of_week' field"):
            TradingWindowService(invalid_config)
    
    def test_weekly_holidays_validation_not_object(self):
        """Test validation failure for non-object weekly holiday entries."""
        invalid_config = [{
            "exchange": "NSE",
            "segment": "FNO",
            "year": 2024,
            "default_trading_windows": [{"open_time": "09:15", "close_time": "15:30"}],
            "weekly_holidays": ["SATURDAY", "SUNDAY"]  # Should be objects
        }]
        
        with pytest.raises(ValueError, match="Weekly holiday must be an object with 'day_of_week' field"):
            TradingWindowService(invalid_config)
    
    def test_weekly_holidays_saturday_detection(self, config_data_list):
        """Test that Saturdays are correctly identified as weekly holidays."""
        service = TradingWindowService(config_data_list)
        
        # November 2, 2024 is a Saturday
        saturday_date = date(2024, 11, 2)
        window = service.get_trading_window(saturday_date, "NSE", "FNO")
        
        assert window is not None
        assert window.is_holiday
        assert window.description == "Weekly Holiday"
        assert window.open_time is None
        assert window.close_time is None
        assert "weekly_holiday" in window.metadata
    
    def test_weekly_holidays_sunday_detection(self, config_data_list):
        """Test that Sundays are correctly identified as weekly holidays."""
        service = TradingWindowService(config_data_list)
        
        # November 3, 2024 is a Sunday
        sunday_date = date(2024, 11, 3)
        window = service.get_trading_window(sunday_date, "NSE", "FNO")
        
        assert window is not None
        assert window.is_holiday
        assert window.description == "Weekly Holiday"
        assert window.open_time is None
        assert window.close_time is None
        assert "weekly_holiday" in window.metadata
    
    def test_weekly_holidays_weekday_not_holiday(self, config_data_list):
        """Test that weekdays are not identified as weekly holidays when only weekends are configured."""
        service = TradingWindowService(config_data_list)
        
        # November 1, 2024 is a Friday (not a weekend)
        friday_date = date(2024, 11, 1)
        window = service.get_trading_window(friday_date, "NSE", "FNO")
        
        # Should be special trading day (Muhurat), not weekly holiday
        assert window is not None
        assert window.is_special_trading_day
        assert not window.is_holiday or "special_trading" in window.metadata
    
    def test_weekly_holidays_all_days_configuration(self):
        """Test configuration with all days as weekly holidays."""
        all_days_config = [{
            "exchange": "TEST",
            "segment": "ALL",
            "year": 2024,
            "default_trading_windows": [{"open_time": "09:15", "close_time": "15:30"}],
            "weekly_holidays": [
                {"day_of_week": "MONDAY"},
                {"day_of_week": "TUESDAY"},
                {"day_of_week": "WEDNESDAY"},
                {"day_of_week": "THURSDAY"},
                {"day_of_week": "FRIDAY"},
                {"day_of_week": "SATURDAY"},
                {"day_of_week": "SUNDAY"}
            ]
        }]
        
        service = TradingWindowService(all_days_config)
        
        # Test each day of the week
        for day_offset in range(7):
            test_date = date(2024, 11, 4 + day_offset)  # Starting from Monday Nov 4, 2024
            window = service.get_trading_window(test_date, "TEST", "ALL")
            
            assert window is not None
            assert window.is_holiday
            assert window.description == "Weekly Holiday"
    
    def test_weekly_holidays_case_insensitive(self):
        """Test that day names are case insensitive."""
        mixed_case_config = [{
            "exchange": "NSE",
            "segment": "FNO",
            "year": 2024,
            "default_trading_windows": [{"open_time": "09:15", "close_time": "15:30"}],
            "weekly_holidays": [
                {"day_of_week": "saturday"},  # lowercase
                {"day_of_week": "Sunday"},    # mixed case
                {"day_of_week": "FRIDAY"}     # uppercase
            ]
        }]
        
        service = TradingWindowService(mixed_case_config)
        
        # Test Saturday (Nov 2, 2024)
        saturday_window = service.get_trading_window(date(2024, 11, 2), "NSE", "FNO")
        assert saturday_window.is_holiday
        
        # Test Sunday (Nov 3, 2024)
        sunday_window = service.get_trading_window(date(2024, 11, 3), "NSE", "FNO")
        assert sunday_window.is_holiday
        
        # Test Friday (Nov 1, 2024) - should override special day
        friday_window = service.get_trading_window(date(2024, 11, 1), "NSE", "FNO")
        assert friday_window.is_holiday  # Weekly holiday takes precedence
    
    def test_weekly_holidays_without_configuration(self, config_data_without_weekly_holidays):
        """Test behavior when no weekly holidays are configured."""
        service = TradingWindowService([config_data_without_weekly_holidays])
        
        # November 2, 2024 is a Saturday, but no weekly holidays configured
        saturday_date = date(2024, 11, 2)
        window = service.get_trading_window(saturday_date, "BSE", "EQ")
        
        # Should generate default trading window since no weekly holidays configured
        assert window is not None
        assert window.is_regular_trading_day
        assert window.open_time == time(9, 15)
        assert window.close_time == time(15, 30)
    
    def test_weekly_holidays_storage_and_conversion(self, config_data_list):
        """Test that day names are properly converted and stored as numeric values."""
        service = TradingWindowService(config_data_list)
        
        # Access the internal storage to verify conversion
        assert hasattr(service, '_weekly_holidays')
        
        weekly_holidays = service._weekly_holidays.get("NSE-FNO", {}).get(2024, [])
        
        # Should contain numeric values for Saturday (5) and Sunday (6)
        assert 5 in weekly_holidays  # Saturday
        assert 6 in weekly_holidays  # Sunday
        assert len(weekly_holidays) == 2
    
    def test_weekly_holidays_multiple_years(self):
        """Test weekly holidays configuration for multiple years."""
        multi_year_config = [
            {
                "exchange": "NSE",
                "segment": "FNO",
                "year": 2024,
                "default_trading_windows": [{"open_time": "09:15", "close_time": "15:30"}],
                "weekly_holidays": [{"day_of_week": "SATURDAY"}, {"day_of_week": "SUNDAY"}]
            },
            {
                "exchange": "NSE",
                "segment": "FNO",
                "year": 2025,
                "default_trading_windows": [{"open_time": "09:15", "close_time": "15:30"}],
                "weekly_holidays": [{"day_of_week": "FRIDAY"}, {"day_of_week": "SATURDAY"}, {"day_of_week": "SUNDAY"}]
            }
        ]
        
        service = TradingWindowService(multi_year_config)
        
        # Test 2024 configuration (Saturday/Sunday)
        saturday_2024 = date(2024, 11, 2)  # Saturday
        friday_2024 = date(2024, 11, 1)    # Friday
        
        saturday_window_2024 = service.get_trading_window(saturday_2024, "NSE", "FNO")
        friday_window_2024 = service.get_trading_window(friday_2024, "NSE", "FNO")
        
        assert saturday_window_2024.is_holiday  # Saturday is weekly holiday in 2024
        assert not friday_window_2024.is_holiday or "special_trading" in friday_window_2024.metadata  # Friday is not weekly holiday in 2024
        
        # Test 2025 configuration (Friday/Saturday/Sunday)
        saturday_2025 = date(2025, 11, 1)  # Saturday
        friday_2025 = date(2025, 10, 31)   # Friday
        
        saturday_window_2025 = service.get_trading_window(saturday_2025, "NSE", "FNO")
        friday_window_2025 = service.get_trading_window(friday_2025, "NSE", "FNO")
        
        assert saturday_window_2025.is_holiday  # Saturday is weekly holiday in 2025
        assert friday_window_2025.is_holiday    # Friday is weekly holiday in 2025


if __name__ == "__main__":
    pytest.main([__file__])
