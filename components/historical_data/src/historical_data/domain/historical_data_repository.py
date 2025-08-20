from abc import ABC, abstractmethod
from datetime import date
from typing import List
from .historical_data import Candle

class HistoricalDataRepository(ABC):
    """
    Abstract base class for a historical data repository.
    Defines the interface for fetching historical candle data.
    """

    @abstractmethod
    def get_historical_data(
        self,
        instrument_key: str,
        from_date: date,
        to_date: date,
        timeframe: str
    ) -> List[Candle]:
        """
        Fetches historical candle data for a given instrument and date range.

        Args:
            instrument_key (str): The instrument key (e.g., 'NSE_INDEX|Nifty 50').
            from_date (date): The start date of the data range.
            to_date (date): The end date of the data range.
            timeframe (str): The candle interval (e.g., '15min', '1h').

        Returns:
            A list of Candle objects.
        """
        pass
