import os
import pandas as pd
import shutil
import tempfile
from datetime import date, datetime
import pytest
from unittest.mock import patch

from algo_core.domain.strategy import Instrument, InstrumentType, Exchange
from algo_core.domain.timeframe import Timeframe
from algo_core.infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository
from algo_core.domain.config import HistoricalDataBackend
from algo_core.domain.backtest.historical_data import HistoricalData

@pytest.fixture
def temp_data_dir():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def instrument():
    return Instrument(
        type=InstrumentType.STOCK,
        exchange=Exchange.NSE,
        instrument_key="TEST_INSTRUMENT"
    )

@pytest.fixture
def timeframe():
    return Timeframe.ONE_MINUTE

@pytest.fixture
def repository(temp_data_dir) -> ParquetHistoricalDataRepository: 
    os.environ["BACKTEST_ENGINE.PARQUET_FILES_BASE_DIR"] = temp_data_dir
    os.environ["HISTORICAL_DATA_BACKEND"] = HistoricalDataBackend.PARQUET_FILES.value
    return ParquetHistoricalDataRepository()

def create_dummy_data(base_path, instrument, timeframe):
    dates = [date(2023, 1, 1), date(2023, 1, 2), date(2023, 1, 3)]
    for d in dates:
        dir_path = f"{base_path}/{timeframe.value}/{instrument.instrument_key}/{d.year}/{d.month:02d}"
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

def test_get_historical_data_range(repository: ParquetHistoricalDataRepository, instrument: Instrument, timeframe: Timeframe, temp_data_dir: str):
    create_dummy_data(temp_data_dir, instrument, timeframe)
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 2)
    hd = repository.get_historical_data(instrument, start_date, end_date, timeframe)
    assert len(hd.data) == 4  # 2 records per file * 2 files
    timestamps = [pd.to_datetime(d['timestamp']) for d in hd.data]
    assert all(start_date <= ts.date() <= end_date for ts in timestamps)
    assert any(ts.date() == date(2023, 1, 1) for ts in timestamps)
    assert any(ts.date() == date(2023, 1, 2) for ts in timestamps)
    assert not any(ts.date() == date(2023, 1, 3) for ts in timestamps)

def test_get_historical_data_no_files(repository, instrument, timeframe):
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 2)
    hd = repository.get_historical_data(instrument, start_date, end_date, timeframe)
    assert len(hd.data) == 0

# def test_get_historical_data_single_day(repository, instrument, timeframe, temp_data_dir):
#     create_dummy_data(temp_data_dir, instrument, timeframe)
#     start_date = date(2023, 1, 1)
#     end_date = date(2023, 1, 1)
#     hd = repository.get_historical_data(instrument, start_date, end_date, timeframe)
#     assert len(hd.data) == 2
#     timestamps = [pd.to_datetime(d['timestamp']) for d in hd.data]
#     assert all(ts.date() == date(2023, 1, 1) for ts in timestamps)

@patch("algo_core.infrastructure.parquet_historical_data_repository.os.path.exists")
@patch("algo_core.infrastructure.parquet_historical_data_repository.pd.read_parquet")
def test_get_historical_data_found(mock_read_parquet, mock_exists, repository, instrument, timeframe):
    mock_exists.side_effect = [True, True]
    df1 = pd.DataFrame([
        {"timestamp": "2024-01-01T09:15:00", "open": 100, "high": 110, "low": 95, "close": 105, "volume": 1000, "oi": 10}
    ])
    df2 = pd.DataFrame([
        {"timestamp": "2024-01-02T09:15:00", "open": 105, "high": 115, "low": 100, "close": 110, "volume": 1200, "oi": 12}
    ])
    mock_read_parquet.side_effect = [df1, df2]
    start = date(2024, 1, 1)
    end = date(2024, 1, 2)
    result = repository.get_historical_data(instrument, start, end, timeframe)
    assert isinstance(result, HistoricalData)
    assert len(result.data) == 2
    assert result.data[0]["open"] == 100
    assert result.data[1]["close"] == 110

@patch("algo_core.infrastructure.parquet_historical_data_repository.os.path.exists")
def test_get_historical_data_not_found(mock_exists, repository, instrument, timeframe):
    mock_exists.return_value = False
    start = date(2024, 1, 1)
    end = date(2024, 1, 2)
    result = repository.get_historical_data(instrument, start, end, timeframe)
    assert isinstance(result, HistoricalData)
    assert result.data == []

# @patch("algo_core.infrastructure.parquet_historical_data_repository.os.path.exists")
# @patch("algo_core.infrastructure.parquet_historical_data_repository.pd.read_parquet")
# def test_get_historical_data_date_filtering(mock_read_parquet, mock_exists, repository, instrument, timeframe):
#     mock_exists.side_effect = [True]
#     df = pd.DataFrame([
#         {"timestamp": "2024-01-01T09:15:00", "open": 100, "high": 110, "low": 95, "close": 105, "volume": 1000, "oi": 10},
#         {"timestamp": "2024-01-03T09:15:00", "open": 120, "high": 130, "low": 115, "close": 125, "volume": 1500, "oi": 15}
#     ])
#     mock_read_parquet.return_value = df
#     start = date(2024, 1, 1)
#     end = date(2024, 1, 2)
#     result = repository.get_historical_data(instrument, start, end, timeframe)
#     assert isinstance(result, HistoricalData)
#     assert len(result.data) == 1
#     assert result.data[0]["open"] == 100
