from typing import List, Dict, Any, Optional
from datetime import datetime

class HistoricalData:
    def __init__(self, data: List[Dict[str, Any]]):
        self.data = data

    def getCandleBy(self, timestamp: str):
        for candle in self.data:
            # Support both string and datetime in data
            candle_ts = candle.get("timestamp")
            if isinstance(candle_ts, str):
                if candle_ts == timestamp:
                    return candle
            else:
                # Assume datetime, compare isoformat
                if hasattr(candle_ts, 'isoformat') and candle_ts.isoformat() == timestamp:
                    return candle
        return None

    def filter(self, start: Optional[datetime] = None, end: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Filter historical data by timestamp range.
        
        Args:
            start: Start datetime (inclusive). If None, no start filtering is applied.
            end: End datetime (inclusive). If None, no end filtering is applied.
            
        Returns:
            List[Dict[str, Any]]: Filtered list of candle data
        """
        if start is None and end is None:
            return self.data
        
        filtered_data = []
        for candle in self.data:
            candle_timestamp = candle.get("timestamp")
            
            # Skip if timestamp is missing
            if candle_timestamp is None:
                continue
                
            # Apply filtering logic
            if start is None:
                # Only end filtering
                if candle_timestamp <= end:
                    filtered_data.append(candle)
            elif end is None:
                # Only start filtering
                if candle_timestamp >= start:
                    filtered_data.append(candle)
            else:
                # Both start and end filtering
                if start <= candle_timestamp <= end:
                    filtered_data.append(candle)
                    
        return filtered_data
