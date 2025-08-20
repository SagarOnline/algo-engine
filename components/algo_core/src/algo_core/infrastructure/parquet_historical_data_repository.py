import os
from datetime import date, timedelta
import pandas as pd
from typing import List, Dict, Any
from algo_core.domain.backtest.historical_data_repository import HistoricalDataRepository
from algo_core.domain.strategy import Instrument
from algo_core.domain.timeframe import Timeframe

class ParquetHistoricalDataRepository(HistoricalDataRepository):
    def __init__(self, data_path: str = "data"):
        self.data_path = os.getenv("HISTORICAL_DATA_DIRECTORY", data_path)

    def get_historical_data(self, instrument: Instrument, start_date: date, end_date: date, timeframe: Timeframe) -> List[Dict[str, Any]]:
        dfs = []
        current_date = start_date
        while current_date <= end_date:
            sanitized_key = instrument.instrument_key.replace("|", ".")
            file_path = (
                f"{self.data_path}/{timeframe.value}/{sanitized_key}/"
                f"{current_date.year}/{current_date.month:02d}/"
                f"{current_date.strftime('%Y-%m-%d')}.parquet"
            )
            if os.path.exists(file_path):
                dfs.append(pd.read_parquet(file_path))
            current_date += timedelta(days=1)

        if not dfs:
            return []

        df = pd.concat(dfs, ignore_index=True)

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]
        
        return df.to_dict('records')
