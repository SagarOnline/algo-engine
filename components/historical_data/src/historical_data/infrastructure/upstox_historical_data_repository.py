import os
from datetime import date
from typing import List, Tuple
import upstox_client
from upstox_client.rest import ApiException
from historical_data.domain.historical_data import Candle
from historical_data.domain.historical_data_repository import HistoricalDataRepository

class UpstoxHistoricalDataRepository(HistoricalDataRepository):
    """
    A repository for fetching historical data from the Upstox API.
    """

    def __init__(self):
        configuration = upstox_client.Configuration(sandbox=False)
        configuration.access_token = os.getenv('UPSTOX_TOKEN')
        configuration.verify_ssl = False
        self.api_instance = upstox_client.HistoryV3Api(upstox_client.ApiClient(configuration))

    def _parse_timeframe(self, timeframe: str) -> Tuple[str, str]:
        """Parses a timeframe string like '15min', '1h' into interval and unit for Upstox API."""
        if timeframe.endswith('min'):
            return (timeframe.replace('min', ''), 'minutes')
        if timeframe.endswith('m'):
            return (timeframe.replace('m', ''), 'minutes')
        if timeframe.endswith('h'):
            return (str(int(timeframe.replace('h', '')) * 60), 'minutes')
        if timeframe.isdigit():
            return (timeframe, 'minutes')
        raise ValueError(f"Invalid timeframe format: {timeframe}")

    def get_historical_data(
        self,
        instrument_key: str,
        from_date: date,
        to_date: date,
        timeframe: str
    ) -> List[Candle]:
        """
        Fetches historical candle data from the Upstox API.
        """
        try:
            date_str_from = from_date.strftime("%Y-%m-%d")
            date_str_to = to_date.strftime("%Y-%m-%d")
            
            interval, unit = self._parse_timeframe(timeframe)

            response = self.api_instance.get_historical_candle_data1(
                instrument_key=instrument_key,
                interval=interval,
                unit=unit,
                from_date=date_str_from,
                to_date=date_str_to
            )

            candles = response.data.candles
            if not candles:
                return []

            return [
                Candle(
                    timestamp=candle[0],
                    open=candle[1],
                    high=candle[2],
                    low=candle[3],
                    close=candle[4],
                    volume=candle[5],
                    oi=candle[6]
                )
                for candle in candles
            ]

        except ApiException as e:
            print(f"❌ API Error: {e}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return []
