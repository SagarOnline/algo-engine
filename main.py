import os
from datetime import date
from domain.strategy import Instrument
from domain.timeframe import Timeframe
from infrastructure.parquet_historical_data_repository import ParquetHistoricalDataRepository


def main():
    """
    This function contains the main logic of the program.
    """
    data_path = os.environ.get("HISTORICAL_DATA_DIRECTORY", "data")
    print(f"Using historical data from: {data_path}")

    repo = ParquetHistoricalDataRepository(data_path=data_path)

    instrument = Instrument(instrument_key="NIFTY 50", exchange="NSE", type="STOCK")
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 5)
    timeframe = Timeframe.MINUTE

    historical_data = repo.get_historical_data(instrument, start_date, end_date, timeframe)

    if historical_data:
        print(f"Successfully fetched {len(historical_data)} records.")
        # print("First record:", historical_data[0])
        # print("Last record:", historical_data[-1])
    else:
        print("No historical data found for the given parameters.")


if __name__ == "__main__":
    main()
