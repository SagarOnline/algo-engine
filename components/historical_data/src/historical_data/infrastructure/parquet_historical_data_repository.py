import os
import pandas as pd
from datetime import date, timedelta
from typing import List
from historical_data.domain.historical_data import Candle
from historical_data.domain.historical_data_repository import HistoricalDataRepository
from historical_data.infrastructure.parquet_storage import ParquetStorage

class ParquetHistoricalDataRepository(HistoricalDataRepository):
    """
    A repository for reading historical data from Parquet files.
    """

    def __init__(self, storage: ParquetStorage):
        self.storage = storage

    def get_historical_data(
        self,
        instrument_key: str,
        from_date: date,
        to_date: date,
        timeframe: str
    ) -> List[Candle]:
        """
        Reads and merges historical candle data from Parquet files for a given date range.
        """
        all_candles: List[Candle] = []
        current_date = from_date
        
        while current_date <= to_date:
            file_path = self.storage.get_file_path(instrument_key, timeframe, current_date)
            
            if os.path.exists(file_path):
                try:
                    df = pd.read_parquet(file_path)
                    for _, row in df.iterrows():
                        all_candles.append(Candle(
                            timestamp=row['timestamp'],
                            open=row['open'],
                            high=row['high'],
                            low=row['low'],
                            close=row['close'],
                            volume=row['volume'],
                            oi=row['oi']
                        ))
                except Exception as e:
                    print(f"Error reading or processing file {file_path}: {e}")
            
            current_date += timedelta(days=1)
            
        return all_candles
