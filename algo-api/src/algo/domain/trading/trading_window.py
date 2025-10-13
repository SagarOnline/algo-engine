"""
Trading window domain model for representing trading sessions and schedules.
"""
from datetime import date, time, datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class TradingWindowType(Enum):
    """Types of trading windows."""
    DEFAULT = "DEFAULT"
    SPECIAL = "SPECIAL"
    HOLIDAY = "HOLIDAY"


@dataclass(frozen=True)
class TradingWindow:
    """
    Represents a trading window for a specific date, exchange and segment.
    
    Attributes:
        date: The trading date
        exchange: Exchange name (e.g., NSE, BSE)
        segment: Market segment (e.g., FNO, EQ, CDS)
        window_type: Type of trading window (DEFAULT, SPECIAL, HOLIDAY)
        open_time: Market opening time (None for holidays)
        close_time: Market closing time (None for holidays)
        description: Optional description of the trading window
        metadata: Additional metadata about the trading window
    """
    date: date
    exchange: str
    segment: str
    window_type: TradingWindowType
    open_time: Optional[time]
    close_time: Optional[time]
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Validate trading window data after initialization."""
        if self.window_type == TradingWindowType.HOLIDAY:
            if self.open_time is not None or self.close_time is not None:
                raise ValueError("Holiday trading windows cannot have open/close times")
        else:
            if self.open_time is None or self.close_time is None:
                raise ValueError("Non-holiday trading windows must have both open and close times")
            if self.open_time >= self.close_time:
                raise ValueError("Open time must be before close time")
    
    @property
    def is_holiday(self) -> bool:
        """Check if this is a holiday (no trading)."""
        return self.window_type == TradingWindowType.HOLIDAY
    
    @property
    def is_special_trading_day(self) -> bool:
        """Check if this is a special trading day with non-standard hours."""
        return self.window_type == TradingWindowType.SPECIAL
    
    @property
    def is_regular_trading_day(self) -> bool:
        """Check if this is a regular trading day with standard hours."""
        return self.window_type == TradingWindowType.DEFAULT
    
    def get_trading_duration_minutes(self) -> Optional[int]:
        """
        Get the trading duration in minutes.
        
        Returns:
            Trading duration in minutes, or None for holidays
        """
        if self.is_holiday or self.open_time is None or self.close_time is None:
            return None
        
        # Convert times to minutes since midnight
        open_minutes = self.open_time.hour * 60 + self.open_time.minute
        close_minutes = self.close_time.hour * 60 + self.close_time.minute
        
        return close_minutes - open_minutes
    
    def is_market_open_at(self, check_time: time) -> bool:
        """
        Check if the market is open at a specific time.
        
        Args:
            check_time: The time to check
            
        Returns:
            True if market is open at the given time, False otherwise
        """
        if self.is_holiday or self.open_time is None or self.close_time is None:
            return False
        
        return self.open_time <= check_time <= self.close_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trading window to dictionary representation."""
        return {
            "date": self.date.isoformat(),
            "exchange": self.exchange,
            "segment": self.segment,
            "window_type": self.window_type.value,
            "open_time": self.open_time.strftime("%H:%M") if self.open_time else None,
            "close_time": self.close_time.strftime("%H:%M") if self.close_time else None,
            "description": self.description,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TradingWindow':
        """Create TradingWindow from dictionary representation."""
        return cls(
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            exchange=data["exchange"],
            segment=data["segment"],
            window_type=TradingWindowType(data["window_type"]),
            open_time=datetime.strptime(data["open_time"], "%H:%M").time() if data.get("open_time") else None,
            close_time=datetime.strptime(data["close_time"], "%H:%M").time() if data.get("close_time") else None,
            description=data.get("description"),
            metadata=data.get("metadata")
        )
    
    def __str__(self) -> str:
        """String representation of trading window."""
        if self.is_holiday:
            return f"{self.date} {self.exchange}-{self.segment}: HOLIDAY - {self.description}"
        else:
            return f"{self.date} {self.exchange}-{self.segment}: {self.open_time}-{self.close_time}"
