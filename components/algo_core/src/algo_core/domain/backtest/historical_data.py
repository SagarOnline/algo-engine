from typing import List, Dict, Any

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
