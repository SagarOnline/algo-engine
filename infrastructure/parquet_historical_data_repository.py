import pandas as pd
from typing import List, Dict, Any
from domain.backtest.historical_data_repository import HistoricalDataRepository
from domain.strategy import Instrument
from datetime import date
from domain.timeframe import Timeframe

class ParquetHistoricalDataRepository(HistoricalDataRepository):
    def __init__(self, data_path: str = "data"):
        self.data_path = data_path

    def get_historical_data(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> List[Dict[str, Any]]:
        file_path = f"{self.data_path}/{instrument.symbol}/{timeframe.value}.parquet"
        df = pd.read_parquet(file_path)

        # Filter the DataFrame based on the date range
        df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]
        
        return df.to_dict('records')
