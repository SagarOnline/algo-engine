"""
Trading window service for managing trading schedules across exchanges and segments.
"""
import json
import logging
from datetime import date, time, datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .trading_window import TradingWindow, TradingWindowType
from ..strategy.strategy import Exchange, Segment

logger = logging.getLogger(__name__)

# Type aliases for better readability
ExchangeSegmentKey = str  # Format: "NSE-FNO"
TradingConfigData = Dict[str, Any]
TradingWindowCache = Dict[ExchangeSegmentKey, Dict[int, Dict[date, TradingWindow]]]


class TradingWindowService:
    """
    Service class for managing trading windows across different exchanges and segments.
    
    This service loads trading window configurations from provided configuration data
    and provides methods to query trading schedules for specific dates, exchanges, and segments.
    """
    
    def __init__(self, config_data_list: List[TradingConfigData]) -> None:
        """
        Initialize the trading window service with configuration data.
        
        Args:
            config_data_list: List of trading window configuration dictionaries
            
        Raises:
            ValueError: If configuration data is invalid or malformed
        """
        self.config_data_list = config_data_list
        
        # Cache structure: {exchange-segment: {year: {date: TradingWindow}}}
        self._trading_windows: TradingWindowCache = {}
        
        # Load all configuration data
        self._load_configurations()
        
        logger.info(f"TradingWindowService initialized with {len(self._trading_windows)} exchange-segment configurations")
    
    def _load_configurations(self) -> None:
        """Load all configuration data from the provided list."""
        if not self.config_data_list:
            logger.warning("No configuration data provided")
            return
        
        for index, config_data in enumerate(self.config_data_list):
            try:
                self._load_configuration_data(config_data, index)
            except Exception as e:
                logger.error(f"Failed to load configuration data at index {index}: {e}")
                raise ValueError(f"Invalid configuration data at index {index}: {e}")
    
    def _load_configuration_data(self, config_data: TradingConfigData, config_index: int) -> None:
        """
        Load a single configuration data dictionary.
        
        Args:
            config_data: Configuration data dictionary
            config_index: Index of the configuration in the list (for error reporting)
        """
        logger.debug(f"Loading trading window configuration from data index {config_index}")
        
        self._validate_configuration(config_data, config_index)
        
        exchange = config_data["exchange"]
        segment = config_data["segment"]
        year = config_data["year"]
        
        exchange_segment_key = f"{exchange}-{segment}"
        
        # Initialize cache structure
        if exchange_segment_key not in self._trading_windows:
            self._trading_windows[exchange_segment_key] = {}
        
        if year not in self._trading_windows[exchange_segment_key]:
            self._trading_windows[exchange_segment_key][year] = {}
        
        year_cache = self._trading_windows[exchange_segment_key][year]
        
        # Load default trading windows
        default_windows = config_data.get("default_trading_windows", [])
        
        # Load holidays
        holidays = config_data.get("holidays", [])
        for holiday_data in holidays:
            holiday_date = datetime.strptime(holiday_data["date"], "%Y-%m-%d").date()
            
            trading_window = TradingWindow(
                date=holiday_date,
                exchange=exchange,
                segment=segment,
                window_type=TradingWindowType.HOLIDAY,
                open_time=None,
                close_time=None,
                description=holiday_data.get("description"),
                metadata={"holiday": True}
            )
            
            year_cache[holiday_date] = trading_window
        
        # Load special trading days
        special_days = config_data.get("special_days", [])
        for special_day_data in special_days:
            special_date = datetime.strptime(special_day_data["date"], "%Y-%m-%d").date()
            
            # Parse times
            open_time = datetime.strptime(special_day_data["open_time"], "%H:%M").time()
            close_time = datetime.strptime(special_day_data["close_time"], "%H:%M").time()
            
            trading_window = TradingWindow(
                date=special_date,
                exchange=exchange,
                segment=segment,
                window_type=TradingWindowType.SPECIAL,
                open_time=open_time,
                close_time=close_time,
                description=special_day_data.get("description"),
                metadata={"special_trading": True}
            )
            
            year_cache[special_date] = trading_window
        
        # Store default and weekly holiday configuration for generating regular trading days
        self._store_default_configuration(exchange_segment_key, year, default_windows)
        self._store_weekly_holidays_configuration(exchange_segment_key, year, config_data)
        
        logger.info(f"Loaded {len(holidays)} holidays and {len(special_days)} special days for {exchange_segment_key} {year}")
    
    def _validate_configuration(self, config_data: TradingConfigData, config_index: int) -> None:
        """
        Validate the configuration data structure.
        
        Args:
            config_data: Configuration data to validate
            config_index: Index of the configuration in the list (for error messages)
            
        Raises:
            ValueError: If configuration is invalid
        """
        required_fields = ["exchange", "segment", "year"]
        for field in required_fields:
            if field not in config_data:
                raise ValueError(f"Missing required field '{field}' in configuration at index {config_index}")
        
        if not isinstance(config_data["year"], int):
            raise ValueError(f"Year must be an integer in configuration at index {config_index}")
        
        # Validate default trading windows
        default_windows = config_data.get("default_trading_windows", [])
        if not isinstance(default_windows, list):
            raise ValueError(f"default_trading_windows must be a list in configuration at index {config_index}")
        
        # Validate holidays
        holidays = config_data.get("holidays", [])
        if not isinstance(holidays, list):
            raise ValueError(f"holidays must be a list in configuration at index {config_index}")
        
        for holiday in holidays:
            if "date" not in holiday:
                raise ValueError(f"Holiday missing 'date' field in configuration at index {config_index}")
        
        # Validate special days
        special_days = config_data.get("special_days", [])
        if not isinstance(special_days, list):
            raise ValueError(f"special_days must be a list in configuration at index {config_index}")
        
        for special_day in special_days:
            required_special_fields = ["date", "open_time", "close_time"]
            for field in required_special_fields:
                if field not in special_day:
                    raise ValueError(f"Special day missing '{field}' field in configuration at index {config_index}")
        
        # Validate weekly holidays
        weekly_holidays = config_data.get("weekly_holidays", [])
        if not isinstance(weekly_holidays, list):
            raise ValueError(f"weekly_holidays must be a list in configuration at index {config_index}")
        
        valid_days = {"MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"}
        for weekly_holiday in weekly_holidays:
            if not isinstance(weekly_holiday, dict):
                raise ValueError(f"Weekly holiday must be an object with 'day_of_week' field in configuration at index {config_index}")
            
            if "day_of_week" not in weekly_holiday:
                raise ValueError(f"Weekly holiday missing 'day_of_week' field in configuration at index {config_index}")
            
            day_of_week = weekly_holiday["day_of_week"]
            if not isinstance(day_of_week, str) or day_of_week.upper() not in valid_days:
                raise ValueError(f"Weekly holiday 'day_of_week' must be one of {valid_days} in configuration at index {config_index}")
    
    def _store_default_configuration(
        self, 
        exchange_segment_key: str, 
        year: int, 
        default_windows: List[Dict[str, Any]]
    ) -> None:
        """
        Store default trading window configuration.
        
        Args:
            exchange_segment_key: Exchange-segment key
            year: Year of the configuration
            default_windows: List of default window configurations
        """
        # For now, we'll store the first default window as the standard
        # In a more complex system, we might handle multiple default windows with date ranges
        if default_windows:
            default_config = default_windows[0]
            
            # Store default configuration in metadata for later use
            if not hasattr(self, '_default_configs'):
                self._default_configs: Dict[str, Dict[int, Dict[str, Any]]] = {}
            
            if exchange_segment_key not in self._default_configs:
                self._default_configs[exchange_segment_key] = {}
            
            self._default_configs[exchange_segment_key][year] = {
                "open_time": datetime.strptime(default_config["open_time"], "%H:%M").time(),
                "close_time": datetime.strptime(default_config["close_time"], "%H:%M").time(),
                "effective_from": default_config.get("effective_from"),
                "effective_to": default_config.get("effective_to")
            }
    
    def _store_weekly_holidays_configuration(
        self, 
        exchange_segment_key: str, 
        year: int, 
        config_data: TradingConfigData
    ) -> None:
        """
        Store weekly holidays configuration.
        
        Args:
            exchange_segment_key: Exchange-segment key
            year: Year of the configuration
            config_data: Configuration data containing weekly holidays
        """
        weekly_holidays_config = config_data.get("weekly_holidays", [])
        
        if weekly_holidays_config:
            # Convert day names to weekday numbers (0=Monday, 6=Sunday)
            day_name_to_number = {
                "MONDAY": 0,
                "TUESDAY": 1,
                "WEDNESDAY": 2,
                "THURSDAY": 3,
                "FRIDAY": 4,
                "SATURDAY": 5,
                "SUNDAY": 6
            }
            
            weekly_holidays = []
            for holiday_config in weekly_holidays_config:
                day_name = holiday_config["day_of_week"].upper()
                weekly_holidays.append(day_name_to_number[day_name])
            
            # Store weekly holidays configuration
            if not hasattr(self, '_weekly_holidays'):
                self._weekly_holidays: Dict[str, Dict[int, List[int]]] = {}
            
            if exchange_segment_key not in self._weekly_holidays:
                self._weekly_holidays[exchange_segment_key] = {}
            
            self._weekly_holidays[exchange_segment_key][year] = weekly_holidays
            
            # Log with both formats for clarity
            day_names = [holiday_config["day_of_week"] for holiday_config in weekly_holidays_config]
            logger.info(f"Configured weekly holidays {day_names} (weekdays {weekly_holidays}) for {exchange_segment_key} {year}")
    
    def get_trading_window(
        self, 
        target_date: date, 
        exchange: Exchange, 
        segment: Segment
    ) -> Optional[TradingWindow]:
        """
        Get the trading window for a specific date, exchange, and segment.
        
        Args:
            target_date: The date to get trading window for
            exchange: Exchange enum (e.g., Exchange.NSE, Exchange.BSE)
            segment: Market segment enum (e.g., Segment.FNO, Segment.EQ)
            
        Returns:
            TradingWindow object if found, None if no configuration exists
        """
        exchange_segment_key = f"{exchange.value}-{segment.value}"
        year = target_date.year
        
        # Check if we have configuration for this exchange-segment-year
        if (exchange_segment_key not in self._trading_windows or 
            year not in self._trading_windows[exchange_segment_key]):
            logger.warning(f"No trading window configuration found for {exchange_segment_key} {year}")
            return None
        
        year_cache = self._trading_windows[exchange_segment_key][year]
        
        # Check if we have a specific entry for this date (holiday or special day)
        if target_date in year_cache:
            return year_cache[target_date]
        
        # If no specific entry, generate default trading window
        return self._generate_default_trading_window(target_date, exchange, segment)
    
    def _generate_default_trading_window(
        self, 
        target_date: date, 
        exchange: Exchange, 
        segment: Segment
    ) -> Optional[TradingWindow]:
        """
        Generate a default trading window for a date.
        
        Args:
            target_date: The date to generate window for
            exchange: Exchange enum
            segment: Market segment enum
            
        Returns:
            Default TradingWindow or None if no default configuration exists
        """
        exchange_segment_key = f"{exchange.value}-{segment.value}"
        year = target_date.year
        
        # Get default configuration
        if (not hasattr(self, '_default_configs') or 
            exchange_segment_key not in self._default_configs or 
            year not in self._default_configs[exchange_segment_key]):
            return None
        
        # Check if this day falls on a weekly holiday
        if self._is_weekly_holiday(target_date, exchange_segment_key, year):
            return TradingWindow(
                date=target_date,
                exchange=exchange.value,
                segment=segment.value,
                window_type=TradingWindowType.HOLIDAY,
                open_time=None,
                close_time=None,
                description="Weekly Holiday",
                metadata={"weekly_holiday": True}
            )
        
        default_config = self._default_configs[exchange_segment_key][year]
        
        return TradingWindow(
            date=target_date,
            exchange=exchange.value,
            segment=segment.value,
            window_type=TradingWindowType.DEFAULT,
            open_time=default_config["open_time"],
            close_time=default_config["close_time"],
            description="Regular trading day",
            metadata={"default": True}
        )
    
    def _is_weekly_holiday(
        self, 
        target_date: date, 
        exchange_segment_key: str, 
        year: int
    ) -> bool:
        """
        Check if a date falls on a configured weekly holiday.
        
        Args:
            target_date: The date to check
            exchange_segment_key: Exchange-segment key
            year: Year to check configuration for
            
        Returns:
            True if the date is a weekly holiday, False otherwise
        """
        if (not hasattr(self, '_weekly_holidays') or 
            exchange_segment_key not in self._weekly_holidays or 
            year not in self._weekly_holidays[exchange_segment_key]):
            return False
        
        weekly_holidays = self._weekly_holidays[exchange_segment_key][year]
        
        # Check if the weekday (0=Monday, 6=Sunday) is in the weekly holidays list
        return target_date.weekday() in weekly_holidays
    
    def is_holiday(self, target_date: date, exchange: Exchange, segment: Segment) -> bool:
        """
        Check if a specific date is a holiday for the given exchange and segment.
        
        Args:
            target_date: The date to check
            exchange: Exchange enum
            segment: Market segment enum
            
        Returns:
            True if the date is a holiday, False otherwise
        """
        trading_window = self.get_trading_window(target_date, exchange, segment)
        return trading_window is not None and trading_window.is_holiday
    
    def is_special_trading_day(self, target_date: date, exchange: Exchange, segment: Segment) -> bool:
        """
        Check if a specific date is a special trading day for the given exchange and segment.
        
        Args:
            target_date: The date to check
            exchange: Exchange enum
            segment: Market segment enum
            
        Returns:
            True if the date is a special trading day, False otherwise
        """
        trading_window = self.get_trading_window(target_date, exchange, segment)
        return trading_window is not None and trading_window.is_special_trading_day
    
    def get_trading_hours(
        self, 
        target_date: date, 
        exchange: Exchange, 
        segment: Segment
    ) -> Optional[Tuple[time, time]]:
        """
        Get trading hours for a specific date, exchange, and segment.
        
        Args:
            target_date: The date to get trading hours for
            exchange: Exchange enum
            segment: Market segment enum
            
        Returns:
            Tuple of (open_time, close_time) if market is open, None if holiday
        """
        trading_window = self.get_trading_window(target_date, exchange, segment)
        
        if trading_window is None or trading_window.is_holiday:
            return None
        
        return (trading_window.open_time, trading_window.close_time)
    
    def get_holidays(self, year: int, exchange: Exchange, segment: Segment) -> List[TradingWindow]:
        """
        Get all holidays for a specific year, exchange, and segment.
        
        Args:
            year: The year to get holidays for
            exchange: Exchange enum
            segment: Market segment enum
            
        Returns:
            List of holiday TradingWindow objects
        """
        exchange_segment_key = f"{exchange.value}-{segment.value}"
        
        if (exchange_segment_key not in self._trading_windows or 
            year not in self._trading_windows[exchange_segment_key]):
            return []
        
        year_cache = self._trading_windows[exchange_segment_key][year]
        
        holidays = [
            window for window in year_cache.values() 
            if window.is_holiday
        ]
        
        return sorted(holidays, key=lambda x: x.date)
    
    def get_special_trading_days(self, year: int, exchange: Exchange, segment: Segment) -> List[TradingWindow]:
        """
        Get all special trading days for a specific year, exchange, and segment.
        
        Args:
            year: The year to get special trading days for
            exchange: Exchange enum
            segment: Market segment enum
            
        Returns:
            List of special trading day TradingWindow objects
        """
        exchange_segment_key = f"{exchange.value}-{segment.value}"
        
        if (exchange_segment_key not in self._trading_windows or 
            year not in self._trading_windows[exchange_segment_key]):
            return []
        
        year_cache = self._trading_windows[exchange_segment_key][year]
        
        special_days = [
            window for window in year_cache.values() 
            if window.is_special_trading_day
        ]
        
        return sorted(special_days, key=lambda x: x.date)
    
    
    def get_available_years(self, exchange: Exchange, segment: Segment) -> List[int]:
        """
        Get list of available years for a specific exchange and segment.
        
        Args:
            exchange: Exchange enum
            segment: Market segment enum
            
        Returns:
            List of available years
        """
        exchange_segment_key = f"{exchange.value}-{segment.value}"
        
        if exchange_segment_key not in self._trading_windows:
            return []
        
        return sorted(self._trading_windows[exchange_segment_key].keys())
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the loaded trading window data.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            "total_exchange_segments": len(self._trading_windows),
            "exchange_segments": {}
        }
        
        for exchange_segment_key, years_data in self._trading_windows.items():
            exchange, segment = exchange_segment_key.split("-", 1)
            
            total_windows = 0
            total_holidays = 0
            total_special_days = 0
            years_loaded = list(years_data.keys())
            
            for year_data in years_data.values():
                for window in year_data.values():
                    total_windows += 1
                    if window.is_holiday:
                        total_holidays += 1
                    elif window.is_special_trading_day:
                        total_special_days += 1
            
            stats["exchange_segments"][exchange_segment_key] = {
                "exchange": exchange,
                "segment": segment,
                "years_loaded": sorted(years_loaded),
                "total_windows": total_windows,
                "total_holidays": total_holidays,
                "total_special_days": total_special_days
            }
        
        return stats
