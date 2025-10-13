"""
Tests for the TradingWindowService and TradingWindow classes.
"""
import pytest
from datetime import date, time

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


if __name__ == "__main__":
    pytest.main([__file__])
