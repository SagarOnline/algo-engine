import unittest
import os
import pandas as pd
from datetime import date, datetime
import shutil

from algo_core.domain.strategy import Instrument, InstrumentType, Exchange
from algo_core.domain.timeframe import Timeframe
from algo_core.infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository

class TestParquetHistoricalDataRepository(unittest.TestCase):
    def setUp(self):
        self.test_data_path = "tests/temp_data"
        os.environ["HISTORICAL_DATA_DIRECTORY"] = self.test_data_path
        self.repository = ParquetHistoricalDataRepository()
        self.instrument = Instrument(
            type=InstrumentType.STOCK,
            exchange=Exchange.NSE,
            instrument_key="TEST_INSTRUMENT"
        )
        self.timeframe = Timeframe.ONE_MINUTE

        # Create dummy data
        self.create_dummy_data()

    def tearDown(self):
        shutil.rmtree(self.test_data_path)
        

    def create_dummy_data(self):
        dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
        for d in dates:
            dir_path = f"{self.test_data_path}/{self.timeframe.value}/{self.instrument.instrument_key}/{d.year}/{d.month:02d}"
            os.makedirs(dir_path, exist_ok=True)
            file_path = f"{dir_path}/{d.strftime('%Y-%m-%d')}.parquet"
            
            timestamps = [
                datetime(d.year, d.month, d.day, 9, 15),
                datetime(d.year, d.month, d.day, 9, 16)
            ]
            df = pd.DataFrame({
                "timestamp": timestamps,
                "open": [100, 101],
                "high": [102, 102],
                "low": [99, 100],
                "close": [101, 101],
                "volume": [1000, 1200]
            })
            df.to_parquet(file_path)

    def test_get_historical_data_range(self):
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 2)
        
        hd = self.repository.get_historical_data(self.instrument, start_date, end_date, self.timeframe)
        self.assertEqual(len(hd.data), 4) # 2 records per file * 2 files
        timestamps = [pd.to_datetime(d['timestamp']) for d in hd.data]
        self.assertTrue(all(start_date <= ts.date() <= end_date for ts in timestamps))
        self.assertTrue(any(ts.date() == date(2023, 1, 1) for ts in timestamps))
        self.assertTrue(any(ts.date() == date(2023, 1, 2) for ts in timestamps))
        self.assertFalse(any(ts.date() == date(2023, 1, 3) for ts in timestamps))

    def test_get_historical_data_no_files(self):
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 2)
        
        hd = self.repository.get_historical_data(self.instrument, start_date, end_date, self.timeframe)
        self.assertEqual(len(hd.data), 0)

    def test_get_historical_data_single_day(self):
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 1)
        
        hd = self.repository.get_historical_data(self.instrument, start_date, end_date, self.timeframe)
        self.assertEqual(len(hd.data), 2)
        timestamps = [pd.to_datetime(d['timestamp']) for d in hd.data]
        self.assertTrue(all(ts.date() == date(2023, 1, 1) for ts in timestamps))

if __name__ == '__main__':
    unittest.main()
