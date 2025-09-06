import datetime
import os
from datetime import datetime,date
from typing import Tuple
from algo.domain.backtest.historical_data import HistoricalData
from algo.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo.domain.strategy import Instrument
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
    
    
    def get_historical_data(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> HistoricalData:
        try:
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
                return HistoricalData([])
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
            return HistoricalData(data)
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
