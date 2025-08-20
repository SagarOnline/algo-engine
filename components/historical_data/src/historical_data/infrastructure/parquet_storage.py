import os
import pandas as pd
from typing import List
from historical_data.domain.historical_data import Candle
from datetime import date

class ParquetStorage:
    """
    A class for storing historical data in Parquet files.
    """

    def __init__(self, base_directory: str):
        if not base_directory:
            raise ValueError("Base directory for storage cannot be empty.")
        self.base_directory = base_directory

    def get_file_path(self, instrument_key: str, timeframe: str, date: date) -> str:
        """
        Generates the full path for a Parquet file for a given instrument, timeframe, and date.
        """
        year_str = date.strftime("%Y")
        month_str = date.strftime("%m")
        file_date_str = date.strftime("%Y-%m-%d")

        output_dir = os.path.join(
            self.base_directory,
            timeframe,
            instrument_key.replace("|", "."),
            year_str,
            month_str
        )
        
        return os.path.join(output_dir, f"{file_date_str}.parquet")

    def store_data(
        self,
        instrument_key: str,
        timeframe: str,
        date: date,
        data: List[Candle]
    ):
        """
        Stores a list of Candle objects to a Parquet file.
        """
        if not data:
            print(f"⚠️ No data to store for {instrument_key} on {date.strftime('%Y-%m-%d')}")
            return

        try:
            df = pd.DataFrame([candle.__dict__ for candle in data])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values(by='timestamp', ascending=True).reset_index(drop=True)

            output_file = self.get_file_path(instrument_key, timeframe, date)
            output_dir = os.path.dirname(output_file)
            
            os.makedirs(output_dir, exist_ok=True)

            df.to_parquet(output_file, index=False)
            print(f"✅ Saved: {output_file}")

        except Exception as e:
            print(f"❌ Error storing data: {e}")
