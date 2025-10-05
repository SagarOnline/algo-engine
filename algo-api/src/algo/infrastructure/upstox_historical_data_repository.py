import datetime
import os
from datetime import datetime, date, timedelta
from typing import Tuple, List
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy.strategy import Instrument
from algo.domain.timeframe import Timeframe


import upstox_client
from upstox_client.rest import ApiException

from algo.infrastructure.access_token import AccessToken

def parse_timeframe(timeframe: Timeframe) -> Tuple[str, str]:
        tf = timeframe.value if hasattr(timeframe, 'value') else str(timeframe)
        if tf.endswith('min'):
            return (tf.replace('min', ''), 'minutes')
        if tf.endswith('m'):
            return (tf.replace('m', ''), 'minutes')
        if tf.endswith('h'):
            return (str(int(tf.replace('h', '')) * 60), 'minutes')
        if tf.endswith('d'):
            return (tf.replace('d', ''), 'days')
        if tf.endswith('w'):
            return (tf.replace('w', ''), 'weeks')
        if tf.isdigit():
            return (tf, 'minutes')
        raise ValueError(f"Invalid timeframe format: {tf}")

class UpstoxHistoricalDataRepository(HistoricalDataRepository):
    
    def _get_max_days_for_timeframe(self, timeframe: Timeframe) -> int:
        """Get maximum allowed days for a given timeframe based on Upstox API limits."""
        tf = timeframe.value if hasattr(timeframe, 'value') else str(timeframe)
        
        # For 1-60 minute intervals: 28 days
        if tf.endswith('min') or tf.endswith('m') or tf.isdigit():
            interval_value = int(tf.replace('min', '').replace('m', '') if not tf.isdigit() else tf)
            if 1 <= interval_value <= 60:
                return 28
        
        # For hour intervals (converted to minutes): 28 days  
        if tf.endswith('h'):
            hour_value = int(tf.replace('h', ''))
            if hour_value * 60 <= 60:  # Up to 1 hour (60 minutes)
                return 28
        
        # For 1-day interval: 9 years (approximately 3287 days)
        if tf.endswith('d'):
            day_value = int(tf.replace('d', ''))
            if day_value == 1:
                return 3287  # 9 years * 365.25 days
        
        # For 1-week interval: no limit (return a very large number)
        if tf.endswith('w'):
            return 999999
        
        # Default to 28 days for safety
        return 28
    
    def _split_date_range(self, start_date: date, end_date: date, max_days: int) -> List[Tuple[date, date]]:
        """Split a date range into smaller segments based on the maximum allowed days."""
        if max_days >= 999999:  # No limit
            return [(start_date, end_date)]
        
        segments = []
        current_start = start_date
        
        while current_start <= end_date:
            current_end = min(current_start + timedelta(days=max_days - 1), end_date)
            segments.append((current_start, current_end))
            current_start = current_end + timedelta(days=1)
        
        return segments
    
    def _fetch_historical_data_segment(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> List[dict]:
        """Fetch historical data for a single date segment."""
        date_str_from = start_date.strftime("%Y-%m-%d")
        date_str_to = end_date.strftime("%Y-%m-%d")
        interval, unit = parse_timeframe(timeframe)
        api_instance = self.api_instance()
        
        response = api_instance.get_historical_candle_data1(
            instrument_key=instrument.instrument_key,
            interval=interval,
            unit=unit,
            from_date=date_str_from,
            to_date=date_str_to
        )
        
        candles = response.data.candles if hasattr(response.data, 'candles') else []
        if not candles:
            return []
            
        data = [
            {
                "timestamp": datetime.fromisoformat(candle[0]),
                "open": candle[1],
                "high": candle[2],
                "low": candle[3],
                "close": candle[4],
                "volume": candle[5],
                "oi": candle[6] if len(candle) > 6 else None
            }
            for candle in reversed(candles)
        ]
        return data
    
    
    def get_historical_data(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> HistoricalData:
        try:
            # Calculate the maximum allowed days for this timeframe
            max_days = self._get_max_days_for_timeframe(timeframe)
            
            # Check if we need to split the date range
            total_days = (end_date - start_date).days + 1
            
            if total_days <= max_days:
                # Single API call is sufficient
                data = self._fetch_historical_data_segment(instrument, start_date, end_date, timeframe)
                return HistoricalData(data)
            else:
                # Split into multiple segments and merge results
                segments = self._split_date_range(start_date, end_date, max_days)
                all_data = []
                
                for segment_start, segment_end in segments:
                    segment_data = self._fetch_historical_data_segment(instrument, segment_start, segment_end, timeframe)
                    all_data.extend(segment_data)
                
                # Sort by timestamp to ensure chronological order
                all_data.sort(key=lambda x: x["timestamp"])
                
                return HistoricalData(all_data)
                
        except ApiException as e:
            raise RuntimeError(f"Exception when calling Upstox API: {e}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}")

    def api_instance(self):
        configuration = upstox_client.Configuration(sandbox=False)
        configuration.access_token = AccessToken().get_token()
        
        configuration.verify_ssl = False
        api_instance = upstox_client.HistoryV3Api(upstox_client.ApiClient(configuration))
        return api_instance
