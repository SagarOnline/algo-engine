import os
import json
from datetime import datetime, timedelta, date
from dotenv import load_dotenv
from historical_data.application.fetch_historical_data_use_case import FetchHistoricalDataUseCase
from historical_data.infrastructure.upstox_historical_data_repository import UpstoxHistoricalDataRepository
from historical_data.infrastructure.parquet_storage import ParquetStorage

def main():
    """
    Main function to run the historical data fetcher.
    """
    load_dotenv()

    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)

    from_date_str = config['from_date']
    instruments = config['instruments']
    timeframes = config['timeframes']

    # Initialize dependencies
    historical_data_repository = UpstoxHistoricalDataRepository()
    data_storage = ParquetStorage(base_directory=os.getenv("HISTORICAL_DATA_DIRECTORY"))

    # Initialize use case
    fetch_historical_data_use_case = FetchHistoricalDataUseCase(
        historical_data_repository=historical_data_repository,
        data_storage=data_storage
    )

    # Determine date range
    start_date = datetime.strptime(from_date_str, "%Y-%m-%d").date()
    end_date = date.today()
    
    # Loop through instruments, timeframes, and dates
    for instrument in instruments:
        print(f"Processing instrument: {instrument}")
        for timeframe in timeframes:
            print(f"  Timeframe: {timeframe}")
            current_date = start_date
            while current_date <= end_date:
                file_path = data_storage.get_file_path(instrument, timeframe, current_date)
                
                if os.path.exists(file_path):
                    print(f"    [DONE] Data already exists for {current_date.strftime('%Y-%m-%d')}. Skipping.")
                else:
                    # Execute use case to fetch and store data
                    fetch_historical_data_use_case.execute(
                        instrument_key=instrument,
                        date=current_date,
                        timeframe=timeframe
                    )
                
                current_date += timedelta(days=1)
        print("-" * 30)


if __name__ == "__main__":
    main()
