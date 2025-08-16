from abc import ABC, abstractmethod
from typing import List, Dict, Any
from domain.strategy import Instrument
from datetime import date
from domain.timeframe import Timeframe


class HistoricalDataRepository(ABC):
    @abstractmethod
    def get_historical_data(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> List[Dict[str, Any]]:
        pass
