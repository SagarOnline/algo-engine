from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .historical_data import HistoricalData
from algo_core.domain.strategy import Instrument
from datetime import date
from algo_core.domain.timeframe import Timeframe


class HistoricalDataRepository(ABC):
    @abstractmethod
    def get_historical_data(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> HistoricalData:
        pass
