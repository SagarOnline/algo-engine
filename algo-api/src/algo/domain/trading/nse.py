from datetime import datetime, timedelta, date
import calendar
import pytz
import logging
from typing import Optional

from ..instrument.instrument import Exchange, Type
from .. import services

logger = logging.getLogger(__name__)


def _get_last_tuesday_of_month(
    year: int, 
    month: int, 
    exchange: Exchange = Exchange.NSE,
    instrument_type: Type = Type.FUT
) -> datetime:
    """
    Get the last Tuesday of a given month, adjusted for trading holidays.
    
    Args:
        year: Year
        month: Month (1-12)
        exchange: Exchange to check holidays for (default: NSE)
        instrument_type: Instrument type to check holidays for (default: FUT)
        
    Returns:
        datetime object representing the last Tuesday of the month at close_time - 1 minute,
        adjusted to previous trading day if the last Tuesday is a holiday
    """
    # Get the last day of the month
    last_day = calendar.monthrange(year, month)[1]
    
    # Create datetime for the last day of the month
    last_date = datetime(year, month, last_day)
    
    # Find the last Tuesday
    # Tuesday is weekday 1 (Monday is 0)
    days_back = (last_date.weekday() - 1) % 7
    last_tuesday = last_date - timedelta(days=days_back)
    
    # Get trading window service and check for holidays and adjust
    trading_window_service = services.get_trading_window_service()
    expiry_date = last_tuesday.date()
    
    # Keep moving back until we find a trading day
    while True:
        trading_window = trading_window_service.get_trading_window(expiry_date, exchange, instrument_type)
        
        if trading_window is None:
            # No trading window configuration found, log and throw error
            error_msg = f"TradingWindowService not initialized properly: No trading window configuration found for {exchange.value}-{instrument_type.value} on {expiry_date}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if not trading_window.is_holiday:
            # Found a trading day, calculate expiry time
            if trading_window.close_time is not None:
                # Subtract 1 minute from close time
                close_datetime = datetime.combine(expiry_date, trading_window.close_time)
                expiry_datetime = close_datetime - timedelta(minutes=1)
                
                # Use the trading window date with the calculated expiry time
                final_expiry_datetime = datetime.combine(
                    trading_window.date, 
                    expiry_datetime.time()
                )
                
                return final_expiry_datetime
            else:
                # Trading day but no close_time - this indicates improper initialization
                error_msg = f"TradingWindowService not initialized properly: Trading window for {exchange.value}-{instrument_type.value} on {expiry_date} is not a holiday but has no close_time"
                logger.error(error_msg)
                raise ValueError(error_msg)
        else:
            # It's a holiday, move to previous day
            expiry_date = expiry_date - timedelta(days=1)


def get_current_monthly_expiry(
    exchange: Exchange = Exchange.NSE,
    instrument_type: Type = Type.FUT
) -> datetime:
    """
    Get the current month's monthly expiry date.
    
    Args:
        exchange: Exchange to check holidays for (default: NSE)
        instrument_type: Instrument type to check holidays for (default: FUT)
    
    Returns:
        datetime object in UTC representing the last Tuesday of current month at close_time - 1 minute,
        adjusted to previous trading day if the last Tuesday is a holiday
    """
    now = datetime.now()
    return _get_last_tuesday_of_month(
        now.year, 
        now.month, 
        exchange, 
        instrument_type
    )


def get_next1_monthly_expiry(
    exchange: Exchange = Exchange.NSE,
    instrument_type: Type = Type.FUT
) -> datetime:
    """
    Get the next month's monthly expiry date.
    
    Args:
        exchange: Exchange to check holidays for (default: NSE)
        instrument_type: Instrument type to check holidays for (default: FUT)
    
    Returns:
        datetime object in UTC representing the last Tuesday of next month at close_time - 1 minute,
        adjusted to previous trading day if the last Tuesday is a holiday
    """
    now = datetime.now()
    
    # Calculate next month
    if now.month == 12:
        next_year = now.year + 1
        next_month = 1
    else:
        next_year = now.year
        next_month = now.month + 1
    
    return _get_last_tuesday_of_month(
        next_year, 
        next_month, 
        exchange, 
        instrument_type
    )


def get_next2_monthly_expiry(
    exchange: Exchange = Exchange.NSE,
    instrument_type: Type = Type.FUT
) -> datetime:
    """
    Get the month after next's monthly expiry date.
    
    Args:
        exchange: Exchange to check holidays for (default: NSE)
        instrument_type: Instrument type to check holidays for (default: FUT)
    
    Returns:
        datetime object in UTC representing the last Tuesday of month after next at close_time - 1 minute,
        adjusted to previous trading day if the last Tuesday is a holiday
    """
    now = datetime.now()
    
    # Calculate month after next
    if now.month >= 11:
        next2_year = now.year + 1
        next2_month = (now.month + 2) % 12
        if next2_month == 0:
            next2_month = 12
    else:
        next2_year = now.year
        next2_month = now.month + 2
    
    return _get_last_tuesday_of_month(
        next2_year, 
        next2_month, 
        exchange, 
        instrument_type
    )


def get_monthly_expiry_for_date(
    target_date: datetime,
    exchange: Exchange = Exchange.NSE,
    instrument_type: Type = Type.FUT
) -> datetime:
    """
    Get the monthly expiry for a specific date's month.
    
    Args:
        target_date: The date for which to find the monthly expiry
        exchange: Exchange to check holidays for (default: NSE)
        instrument_type: Instrument type to check holidays for (default: FUT)
        
    Returns:
        datetime object in UTC representing the last Tuesday of the target date's month at close_time - 1 minute,
        adjusted to previous trading day if the last Tuesday is a holiday
    """
    return _get_last_tuesday_of_month(
        target_date.year, 
        target_date.month, 
        exchange, 
        instrument_type
    )
