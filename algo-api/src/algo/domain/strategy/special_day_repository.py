"""
Special Day Repository interface for managing holidays and special trading days.

This module provides an abstraction for managing special trading days such as holidays
and days with modified trading hours.
"""

from abc import ABC, abstractmethod
from datetime import date, time
from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .strategy import Exchange


class DayType(Enum):
    """Enumeration for different types of special days."""
    HOLIDAY = "HOLIDAY"
    SPECIAL_TRADING_DAY = "SPECIAL_TRADING_DAY"


@dataclass
class SpecialDay:
    """
    Represents a special trading day with optional modified trading hours.
    
    Attributes:
        date: The date of the special day
        day_type: Type of special day (holiday or special trading day)
        description: Human-readable description of the special day
        trading_start: Optional custom trading start time (None for holidays)
        trading_end: Optional custom trading end time (None for holidays)
        metadata: Optional additional metadata as key-value pairs
    """
    date: date
    day_type: DayType
    description: str
    trading_start: Optional[time] = None
    trading_end: Optional[time] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate the special day configuration after initialization."""
        if self.day_type == DayType.HOLIDAY:
            # Holidays should not have trading hours
            if self.trading_start is not None or self.trading_end is not None:
                raise ValueError("Holidays cannot have trading hours specified")
        elif self.day_type == DayType.SPECIAL_TRADING_DAY:
            # Special trading days should have both start and end times or neither
            if (self.trading_start is None) != (self.trading_end is None):
                raise ValueError("Special trading days must have both start and end times or neither")
        
        # Initialize metadata as empty dict if None
        if self.metadata is None:
            self.metadata = {}
    
    def is_holiday(self) -> bool:
        """Check if this special day is a holiday."""
        return self.day_type == DayType.HOLIDAY
    
    def is_special_trading_day(self) -> bool:
        """Check if this special day has special trading hours."""
        return self.day_type == DayType.SPECIAL_TRADING_DAY
    
    def has_custom_trading_hours(self) -> bool:
        """Check if this special day has custom trading hours."""
        return self.trading_start is not None and self.trading_end is not None


class SpecialDayRepository(ABC):
    """
    Abstract repository interface for managing special trading days.
    
    This interface provides methods to retrieve holidays, special trading days,
    and manage the underlying data source.
    """
    
    @abstractmethod
    def get_special_days_for_year(self, year: int, exchange: Optional[Exchange] = None) -> List[SpecialDay]:
        """
        Retrieve all special days for a given year and exchange.
        
        Args:
            year: The year for which to retrieve special days
            exchange: The exchange for which to retrieve special days (if None, uses default)
            
        Returns:
            List of SpecialDay objects for the specified year and exchange
            
        Raises:
            ValueError: If year is invalid
        """
        pass
    
    @abstractmethod
    def get_special_day(self, target_date: date, exchange: Optional[Exchange] = None) -> Optional[SpecialDay]:
        """
        Retrieve special day information for a specific date and exchange.
        
        Args:
            target_date: The date to check for special day information
            exchange: The exchange to check (if None, uses default)
            
        Returns:
            SpecialDay object if the date is a special day, None otherwise
        """
        pass
    
    @abstractmethod
    def get_holidays(self, year: int, exchange: Optional[Exchange] = None) -> List[SpecialDay]:
        """
        Retrieve all holidays for a given year and exchange.
        
        Args:
            year: The year for which to retrieve holidays
            exchange: The exchange for which to retrieve holidays (if None, uses default)
            
        Returns:
            List of SpecialDay objects with day_type HOLIDAY for the specified year and exchange
            
        Raises:
            ValueError: If year is invalid
        """
        pass
    
    @abstractmethod
    def get_special_trading_days(self, year: int, exchange: Optional[Exchange] = None) -> List[SpecialDay]:
        """
        Retrieve all special trading days for a given year and exchange.
        
        Args:
            year: The year for which to retrieve special trading days
            exchange: The exchange for which to retrieve special trading days (if None, uses default)
            
        Returns:
            List of SpecialDay objects with day_type SPECIAL_TRADING_DAY for the specified year and exchange
            
        Raises:
            ValueError: If year is invalid
        """
        pass
    
    @abstractmethod
    def refresh_cache(self) -> None:
        """
        Refresh the internal cache of special days.
        
        This method should be called when the underlying data source has been updated
        and the repository needs to reload the data.
        """
        pass
    
    def is_holiday(self, target_date: date, exchange: Optional[Exchange] = None) -> bool:
        """
        Check if a given date is a holiday for the specified exchange.
        
        Args:
            target_date: The date to check
            exchange: The exchange to check (if None, uses default)
            
        Returns:
            True if the date is a holiday, False otherwise
        """
        special_day = self.get_special_day(target_date, exchange)
        return special_day is not None and special_day.is_holiday()
    
    def is_special_trading_day(self, target_date: date, exchange: Optional[Exchange] = None) -> bool:
        """
        Check if a given date is a special trading day for the specified exchange.
        
        Args:
            target_date: The date to check
            exchange: The exchange to check (if None, uses default)
            
        Returns:
            True if the date is a special trading day, False otherwise
        """
        special_day = self.get_special_day(target_date, exchange)
        return special_day is not None and special_day.is_special_trading_day()
    
    def get_trading_hours(self, target_date: date, exchange: Optional[Exchange] = None) -> Optional[tuple[time, time]]:
        """
        Get custom trading hours for a specific date if it's a special trading day.
        
        Args:
            target_date: The date to check for custom trading hours
            exchange: The exchange to check (if None, uses default)
            
        Returns:
            Tuple of (start_time, end_time) if the date has custom trading hours,
            None otherwise
        """
        special_day = self.get_special_day(target_date, exchange)
        if special_day and special_day.has_custom_trading_hours():
            return (special_day.trading_start, special_day.trading_end)
        return None
