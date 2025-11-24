import pytest
from datetime import datetime, date, time, timedelta
from unittest.mock import Mock, patch, MagicMock
import calendar

from algo.domain.trading.nse import (
    _get_last_tuesday_of_month,
    get_current_monthly_expiry,
    get_next1_monthly_expiry,
    get_next2_monthly_expiry,
    get_monthly_expiry_for_date
)
from algo.domain.instrument.instrument import Exchange, Type
from algo.domain.trading.trading_window import TradingWindow, TradingWindowType


class TestGetLastTuesdayOfMonth:
    """Test cases for _get_last_tuesday_of_month function"""
    
    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_last_tuesday_normal_trading_day(self, mock_get_service):
        """Test getting last Tuesday when it's a normal trading day"""
        # Setup mock
        mock_service = Mock()
        mock_trading_window = TradingWindow(
            date=date(2023, 10, 31),  # Last Tuesday of October 2023
            exchange=Exchange.NSE,
            type=Type.FUT,
            window_type=TradingWindowType.DEFAULT,
            open_time=time(9, 15),
            close_time=time(15, 30),
            description="Regular trading day"
        )
        mock_service.get_trading_window.return_value = mock_trading_window
        mock_get_service.return_value = mock_service
        
        # Test
        result = _get_last_tuesday_of_month(2023, 10, Exchange.NSE, Type.FUT)
        
        # Verify
        expected_datetime = datetime(2023, 10, 31, 15, 29)  # close_time - 1 minute
        assert result == expected_datetime
        mock_service.get_trading_window.assert_called_once_with(
            date(2023, 10, 31), Exchange.NSE, Type.FUT
        )
    
    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_last_tuesday_is_holiday_moves_to_previous_day(self, mock_get_service):
        """Test when last Tuesday is holiday, moves to previous trading day"""
        # Setup mock
        mock_service = Mock()
        
        def mock_get_trading_window(target_date, exchange, instrument_type):
            if target_date == date(2023, 10, 31):  # Last Tuesday is holiday
                return TradingWindow(
                    date=target_date,
                    exchange=Exchange.NSE,
                    type=Type.FUT,
                    window_type=TradingWindowType.HOLIDAY,
                    open_time=None,
                    close_time=None,
                    description="Holiday"
                )
            elif target_date == date(2023, 10, 30):  # Monday is trading day
                return TradingWindow(
                    date=target_date,
                    exchange=Exchange.NSE,
                    type=Type.FUT,
                    window_type=TradingWindowType.DEFAULT,
                    open_time=time(9, 15),
                    close_time=time(15, 30),
                    description="Regular trading day"
                )
        
        mock_service.get_trading_window.side_effect = mock_get_trading_window
        mock_get_service.return_value = mock_service
        
        # Test
        result = _get_last_tuesday_of_month(2023, 10, Exchange.NSE, Type.FUT)
        
        # Verify - should use Monday (Oct 30) instead of Tuesday (Oct 31)
        expected_datetime = datetime(2023, 10, 30, 15, 29)
        assert result == expected_datetime
        assert mock_service.get_trading_window.call_count == 2
    
    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_no_trading_window_configuration_raises_error(self, mock_get_service):
        """Test error when no trading window configuration found"""
        # Setup mock
        mock_service = Mock()
        mock_service.get_trading_window.return_value = None
        mock_get_service.return_value = mock_service
        
        # Test & Verify
        with pytest.raises(ValueError, match="TradingWindowService not initialized properly: No trading window configuration found"):
            _get_last_tuesday_of_month(2023, 10, Exchange.NSE, Type.FUT)
    
    
    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_service_not_available_raises_error(self, mock_get_service):
        """Test error propagation when service is not available"""
        # Setup mock to raise ValueError
        mock_get_service.side_effect = ValueError("Service not registered")
        
        # Test & Verify
        with pytest.raises(ValueError, match="Service not registered"):
            _get_last_tuesday_of_month(2023, 10, Exchange.NSE, Type.FUT)
    
    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_different_exchanges_and_types(self, mock_get_service):
        """Test with different exchange and instrument type parameters"""
        # Setup mock
        mock_service = Mock()
        mock_trading_window = TradingWindow(
            date=date(2023, 10, 31),
            exchange=Exchange.BSE,
            type=Type.EQ,
            window_type=TradingWindowType.DEFAULT,
            open_time=time(9, 15),
            close_time=time(15, 30),
            description="BSE trading day"
        )
        mock_service.get_trading_window.return_value = mock_trading_window
        mock_get_service.return_value = mock_service
        
        # Test
        result = _get_last_tuesday_of_month(2023, 10, Exchange.BSE, Type.EQ)
        
        # Verify
        expected_datetime = datetime(2023, 10, 31, 15, 29)
        assert result == expected_datetime
        mock_service.get_trading_window.assert_called_once_with(
            date(2023, 10, 31), Exchange.BSE, Type.EQ
        )
    
    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_last_tuesday_calculation_accuracy(self, mock_get_service):
        """Test that last Tuesday calculation is accurate for different months"""
        # Test data: (year, month, expected_last_tuesday_date)
        test_cases = [
            (2023, 1, 31),   # January 2023: last Tuesday is 31st
            (2023, 2, 28),   # February 2023: last Tuesday is 28th
            (2023, 3, 28),   # March 2023: last Tuesday is 28th
            (2023, 4, 25),   # April 2023: last Tuesday is 25th
            (2023, 5, 30),   # May 2023: last Tuesday is 30th
            (2024, 2, 27),   # February 2024 (leap year): last Tuesday is 27th
        ]
        
        mock_service = Mock()
        
        def mock_get_trading_window(target_date, exchange, instrument_type):
            return TradingWindow(
                date=target_date,
                exchange=Exchange.NSE,
                type=Type.FUT,
                window_type=TradingWindowType.DEFAULT,
                open_time=time(9, 15),
                close_time=time(15, 30),
                description="Regular trading day"
            )
        
        mock_service.get_trading_window.side_effect = mock_get_trading_window
        mock_get_service.return_value = mock_service
        
        for year, month, expected_day in test_cases:
            result = _get_last_tuesday_of_month(year, month)
            expected_date = datetime(year, month, expected_day, 15, 29)
            assert result == expected_date, f"Failed for {year}-{month}: expected {expected_date}, got {result}"


class TestGetCurrentMonthlyExpiry:
    """Test cases for get_current_monthly_expiry function"""
    
    @patch('algo.domain.trading.nse.datetime')
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_current_monthly_expiry_calls_helper_with_current_date(self, mock_helper, mock_datetime):
        """Test that current expiry uses current date"""
        # Setup mock
        mock_now = datetime(2023, 10, 15, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        expected_result = datetime(2023, 10, 31, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test
        result = get_current_monthly_expiry(Exchange.NSE, Type.FUT)
        
        # Verify
        assert result == expected_result
        mock_helper.assert_called_once_with(2023, 10, Exchange.NSE, Type.FUT)
    
    @patch('algo.domain.trading.nse.datetime')
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_current_monthly_expiry_default_parameters(self, mock_helper, mock_datetime):
        """Test current expiry with default parameters"""
        # Setup mock
        mock_now = datetime(2023, 5, 20, 10, 30, 0)
        mock_datetime.now.return_value = mock_now
        expected_result = datetime(2023, 5, 30, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test with default parameters
        result = get_current_monthly_expiry()
        
        # Verify default parameters are used
        mock_helper.assert_called_once_with(2023, 5, Exchange.NSE, Type.FUT)


class TestGetNext1MonthlyExpiry:
    """Test cases for get_next1_monthly_expiry function"""
    
    @patch('algo.domain.trading.nse.datetime')
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_next1_monthly_expiry_normal_month(self, mock_helper, mock_datetime):
        """Test next month expiry for normal month progression"""
        # Setup mock - current month is October
        mock_now = datetime(2023, 10, 15, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        expected_result = datetime(2023, 11, 28, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test
        result = get_next1_monthly_expiry(Exchange.BSE, Type.EQ)
        
        # Verify next month (November) is used
        assert result == expected_result
        mock_helper.assert_called_once_with(2023, 11, Exchange.BSE, Type.EQ)
    
    @patch('algo.domain.trading.nse.datetime')
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_next1_monthly_expiry_december_to_january(self, mock_helper, mock_datetime):
        """Test next month expiry when crossing year boundary"""
        # Setup mock - current month is December
        mock_now = datetime(2023, 12, 15, 14, 30, 0)
        mock_datetime.now.return_value = mock_now
        expected_result = datetime(2024, 1, 30, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test
        result = get_next1_monthly_expiry()
        
        # Verify next year January is used
        assert result == expected_result
        mock_helper.assert_called_once_with(2024, 1, Exchange.NSE, Type.FUT)


class TestGetNext2MonthlyExpiry:
    """Test cases for get_next2_monthly_expiry function"""
    
    @patch('algo.domain.trading.nse.datetime')
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_next2_monthly_expiry_normal_months(self, mock_helper, mock_datetime):
        """Test month after next expiry for normal progression"""
        # Setup mock - current month is August
        mock_now = datetime(2023, 8, 10, 11, 0, 0)
        mock_datetime.now.return_value = mock_now
        expected_result = datetime(2023, 10, 31, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test
        result = get_next2_monthly_expiry(Exchange.NSE, Type.PE)
        
        # Verify month after next (October) is used
        assert result == expected_result
        mock_helper.assert_called_once_with(2023, 10, Exchange.NSE, Type.PE)
    
    @patch('algo.domain.trading.nse.datetime')
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_next2_monthly_expiry_november_to_january(self, mock_helper, mock_datetime):
        """Test month after next when November -> January next year"""
        # Setup mock - current month is November
        mock_now = datetime(2023, 11, 20, 16, 45, 0)
        mock_datetime.now.return_value = mock_now
        expected_result = datetime(2024, 1, 30, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test
        result = get_next2_monthly_expiry()
        
        # Verify next year January is used
        assert result == expected_result
        mock_helper.assert_called_once_with(2024, 1, Exchange.NSE, Type.FUT)
    
    @patch('algo.domain.trading.nse.datetime')
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_next2_monthly_expiry_december_to_february(self, mock_helper, mock_datetime):
        """Test month after next when December -> February next year"""
        # Setup mock - current month is December
        mock_now = datetime(2023, 12, 5, 9, 30, 0)
        mock_datetime.now.return_value = mock_now
        expected_result = datetime(2024, 2, 27, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test
        result = get_next2_monthly_expiry()
        
        # Verify next year February is used
        assert result == expected_result
        mock_helper.assert_called_once_with(2024, 2, Exchange.NSE, Type.FUT)


class TestGetMonthlyExpiryForDate:
    """Test cases for get_monthly_expiry_for_date function"""
    
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_monthly_expiry_for_specific_date(self, mock_helper):
        """Test getting expiry for a specific date"""
        # Setup mock
        target_date = datetime(2023, 7, 15, 14, 20, 30)
        expected_result = datetime(2023, 7, 25, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test
        result = get_monthly_expiry_for_date(target_date, Exchange.BSE, Type.CE)
        
        # Verify
        assert result == expected_result
        mock_helper.assert_called_once_with(2023, 7, Exchange.BSE, Type.CE)
    
    @patch('algo.domain.trading.nse._get_last_tuesday_of_month')
    def test_get_monthly_expiry_for_date_default_parameters(self, mock_helper):
        """Test getting expiry for date with default exchange and type"""
        # Setup mock
        target_date = datetime(2024, 3, 8, 10, 15, 45)
        expected_result = datetime(2024, 3, 26, 15, 29)
        mock_helper.return_value = expected_result
        
        # Test with default parameters
        result = get_monthly_expiry_for_date(target_date)
        
        # Verify default parameters are used
        mock_helper.assert_called_once_with(2024, 3, Exchange.NSE, Type.FUT)


class TestIntegrationScenarios:
    """Integration test scenarios with real-world cases"""
    
    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_real_world_diwali_holiday_scenario(self, mock_get_service):
        """Test real-world scenario where Diwali falls on last Tuesday"""
        # Setup mock - Simulate a scenario where last Tuesday of a month is Diwali
        mock_service = Mock()
        
        def mock_get_trading_window(target_date, exchange, instrument_type):
            if target_date == date(2023, 10, 31):  # Last Tuesday is Diwali
                return TradingWindow(
                    date=target_date,
                    exchange=Exchange.NSE,
                    type=Type.FUT,
                    window_type=TradingWindowType.HOLIDAY,
                    open_time=None,
                    close_time=None,
                    description="Diwali Holiday",
                    metadata={"holiday_name": "Diwali"}
                )
            elif target_date == date(2023, 10, 30):  # Monday is trading day  
                return TradingWindow(
                    date=target_date,
                    exchange=Exchange.NSE,
                    type=Type.FUT,
                    window_type=TradingWindowType.DEFAULT,
                    open_time=time(9, 15),
                    close_time=time(15, 30),
                    description="Regular trading day"
                )
        
        mock_service.get_trading_window.side_effect = mock_get_trading_window
        mock_get_service.return_value = mock_service
        
        # Test
        result = _get_last_tuesday_of_month(2023, 10)
        
        # Verify expiry moved to previous day
        expected_datetime = datetime(2023, 10, 30, 15, 29)
        assert result == expected_datetime
    
    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_multiple_consecutive_holidays(self, mock_get_service):
        """Test scenario with multiple consecutive holidays"""
        mock_service = Mock()
        
        def mock_get_trading_window(target_date, exchange, instrument_type):
            # Multiple holidays from Oct 29-31
            if target_date in [date(2023, 10, 31), date(2023, 10, 30), date(2023, 10, 29)]:
                return TradingWindow(
                    date=target_date,
                    exchange=Exchange.NSE, 
                    type=Type.FUT,
                    window_type=TradingWindowType.HOLIDAY,
                    open_time=None,
                    close_time=None,
                    description="Extended Holiday"
                )
            elif target_date == date(2023, 10, 28):  # Saturday - Weekly holiday
                return TradingWindow(
                    date=target_date,
                    exchange=Exchange.NSE,
                    type=Type.FUT, 
                    window_type=TradingWindowType.HOLIDAY,
                    open_time=None,
                    close_time=None,
                    description="Weekly Holiday",
                    metadata={"weekly_holiday": True}
                )
            elif target_date == date(2023, 10, 27):  # Friday is trading day
                return TradingWindow(
                    date=target_date,
                    exchange=Exchange.NSE,
                    type=Type.FUT,
                    window_type=TradingWindowType.DEFAULT,
                    open_time=time(9, 15),
                    close_time=time(15, 30), 
                    description="Regular trading day"
                )
        
        mock_service.get_trading_window.side_effect = mock_get_trading_window
        mock_get_service.return_value = mock_service
        
        # Test
        result = _get_last_tuesday_of_month(2023, 10)
        
        # Verify expiry moved to Friday (Oct 27)
        expected_datetime = datetime(2023, 10, 27, 15, 29)
        assert result == expected_datetime
        
        # Verify multiple calls were made
        assert mock_service.get_trading_window.call_count == 5

    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_different_close_times_for_different_segments(self, mock_get_service):
        """Test that different market segments can have different close times"""
        mock_service = Mock()
        
        # Setup different close times for different segments
        def mock_get_trading_window(target_date, exchange, instrument_type):
            if instrument_type == Type.EQ:
                close_time_val = time(15, 30)  # Equity closes at 3:30 PM
            else:
                close_time_val = time(15, 29)  # F&O closes at 3:29 PM
                
            return TradingWindow(
                date=target_date,
                exchange=exchange,
                type=instrument_type,
                window_type=TradingWindowType.DEFAULT,
                open_time=time(9, 15),
                close_time=close_time_val,
                description="Regular trading day"
            )
        
        mock_service.get_trading_window.side_effect = mock_get_trading_window
        mock_get_service.return_value = mock_service
        
        # Test EQ segment
        result_eq = _get_last_tuesday_of_month(2023, 10, Exchange.NSE, Type.EQ)
        expected_eq = datetime(2023, 10, 31, 15, 29)  # 15:30 - 1 minute
        assert result_eq == expected_eq
        
        # Test FUT segment  
        result_fut = _get_last_tuesday_of_month(2023, 10, Exchange.NSE, Type.FUT)
        expected_fut = datetime(2023, 10, 31, 15, 28)  # 15:29 - 1 minute
        assert result_fut == expected_fut

    @patch('algo.domain.trading.nse.services.get_trading_window_service')
    def test_edge_case_february_leap_year(self, mock_get_service):
        """Test February in leap year vs non-leap year"""
        mock_service = Mock()
        
        def mock_get_trading_window(target_date, exchange, instrument_type):
            return TradingWindow(
                date=target_date,
                exchange=exchange,
                type=instrument_type,
                window_type=TradingWindowType.DEFAULT,
                open_time=time(9, 15),
                close_time=time(15, 30),
                description="Regular trading day"
            )
        
        mock_service.get_trading_window.side_effect = mock_get_trading_window
        mock_get_service.return_value = mock_service
        
        # Test leap year 2024 - February has 29 days, last Tuesday should be Feb 27
        result_2024 = _get_last_tuesday_of_month(2024, 2)
        expected_2024 = datetime(2024, 2, 27, 15, 29)
        assert result_2024 == expected_2024
        
        # Test non-leap year 2023 - February has 28 days, last Tuesday should be Feb 28
        result_2023 = _get_last_tuesday_of_month(2023, 2)
        expected_2023 = datetime(2023, 2, 28, 15, 29)
        assert result_2023 == expected_2023


if __name__ == "__main__":
    pytest.main([__file__])
