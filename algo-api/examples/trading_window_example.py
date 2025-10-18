"""
Example demonstrating usage of TradingWindowService and TradingWindow classes.
"""
from datetime import date, time
import logging

from algo.domain.trading.trading_window_service import TradingWindowService
from algo.domain.trading.trading_window import TradingWindow, TradingWindowType

# Configure logging
logging.basicConfig(level=logging.INFO)


def main():
    """Main example function demonstrating trading window service usage."""
    
    # Initialize the trading window service with config directory
    config_directory = "config/trading_window"
    service = TradingWindowService(config_directory)
    
    print("✅ TradingWindowService initialized")
    print(f"📁 Config directory: {config_directory}")
    
    # Display available exchange-segment combinations
    exchanges_segments = service.get_available_exchanges_segments()
    print(f"\n📊 Available exchange-segment combinations: {len(exchanges_segments)}")
    for exchange, segment in exchanges_segments:
        years = service.get_available_years(exchange, segment)
        print(f"   - {exchange}-{segment}: Years {years}")
    
    # Example queries for NSE FNO
    exchange = "NSE"
    segment = "FNO"
    
    print(f"\n🔍 Examples for {exchange}-{segment}:")
    
    # Check regular trading day
    regular_date = date(2024, 11, 5)
    check_trading_day(service, regular_date, exchange, segment)
    
    # Check holiday
    christmas = date(2024, 12, 25)
    check_trading_day(service, christmas, exchange, segment)
    
    # Check special trading day (Muhurat trading)
    muhurat_date = date(2024, 11, 1)
    check_trading_day(service, muhurat_date, exchange, segment)
    
    # Get all holidays for 2024
    print(f"\n🎄 Holidays for {exchange}-{segment} in 2024:")
    holidays = service.get_holidays(2024, exchange, segment)
    for holiday in holidays:
        print(f"   - {holiday.date}: {holiday.description}")
    
    # Get all special trading days for 2024
    print(f"\n⭐ Special trading days for {exchange}-{segment} in 2024:")
    special_days = service.get_special_trading_days(2024, exchange, segment)
    for special_day in special_days:
        print(f"   - {special_day.date}: {special_day.description} "
              f"({special_day.open_time} - {special_day.close_time})")


def check_trading_day(service: TradingWindowService, target_date: date, exchange: str, segment: str):
    """
    Check and display information about a specific trading day.
    
    Args:
        service: TradingWindowService instance
        target_date: Date to check
        exchange: Exchange name
        segment: Market segment
    """
    print(f"\n📅 Checking {target_date} for {exchange}-{segment}:")
    
    # Get trading window
    window = service.get_trading_window(target_date, exchange, segment)
    
    if window is None:
        print("   ❌ No trading window configuration found")
        return
    
    # Display window information
    if window.is_holiday:
        print(f"   🚫 HOLIDAY: {window.description}")
        print("   ⏰ Market is closed")
    elif window.is_special_trading_day:
        print(f"   ⭐ SPECIAL TRADING DAY: {window.description}")
        print(f"   ⏰ Trading hours: {window.open_time} - {window.close_time}")
        duration = window.get_trading_duration_minutes()
        print(f"   ⏱️  Duration: {duration} minutes")
    else:
        print(f"   📈 REGULAR TRADING DAY")
        print(f"   ⏰ Trading hours: {window.open_time} - {window.close_time}")
        duration = window.get_trading_duration_minutes()
        print(f"   ⏱️  Duration: {duration} minutes")
    
    # Check specific times
    if not window.is_holiday:
        test_times = [time(9, 0), time(9, 15), time(12, 0), time(15, 30), time(16, 0)]
        for test_time in test_times:
            is_open = window.is_market_open_at(test_time)
            status = "OPEN" if is_open else "CLOSED"
            print(f"   🕐 {test_time}: {status}")


def demonstrate_trading_window_creation():
    """Demonstrate creating TradingWindow objects directly."""
    print("\n🏗️  Demonstrating TradingWindow creation:")
    
    # Create a regular trading window
    regular_window = TradingWindow(
        date=date(2024, 11, 5),
        exchange="NSE",
        segment="FNO",
        window_type=TradingWindowType.DEFAULT,
        open_time=time(9, 15),
        close_time=time(15, 30),
        description="Regular trading day",
        metadata={"weekly_settlement": False}
    )
    
    print(f"📈 Regular window: {regular_window}")
    print(f"   Duration: {regular_window.get_trading_duration_minutes()} minutes")
    print(f"   Dictionary: {regular_window.to_dict()}")
    
    # Create a holiday window
    holiday_window = TradingWindow(
        date=date(2024, 12, 25),
        exchange="NSE",
        segment="FNO",
        window_type=TradingWindowType.HOLIDAY,
        open_time=None,
        close_time=None,
        description="Christmas",
        metadata={"public_holiday": True}
    )
    
    print(f"\n🎄 Holiday window: {holiday_window}")
    print(f"   Is holiday: {holiday_window.is_holiday}")
    
    # Create a special trading window
    special_window = TradingWindow(
        date=date(2024, 11, 1),
        exchange="NSE",
        segment="FNO",
        window_type=TradingWindowType.SPECIAL,
        open_time=time(18, 0),
        close_time=time(19, 0),
        description="Muhurat Trading",
        metadata={"diwali_special": True}
    )
    
    print(f"\n⭐ Special window: {special_window}")
    print(f"   Duration: {special_window.get_trading_duration_minutes()} minutes")
    print(f"   Is special: {special_window.is_special_trading_day}")


if __name__ == "__main__":
    try:
        main()
        demonstrate_trading_window_creation()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
