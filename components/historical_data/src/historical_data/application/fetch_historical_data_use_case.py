from datetime import date
from domain.historical_data_repository import HistoricalDataRepository
from infrastructure.parquet_storage import ParquetStorage

class FetchHistoricalDataUseCase:
    """
    Use case for fetching and storing historical data.
    """

    def __init__(
        self,
        historical_data_repository: HistoricalDataRepository,
        data_storage: ParquetStorage
    ):
        self.historical_data_repository = historical_data_repository
        self.data_storage = data_storage

    def execute(
        self,
        instrument_key: str,
        date: date,
        timeframe: str
    ):
        """
        Executes the use case.
        """
        print(f"[FETCHING] {timeframe}-minute data for {instrument_key} on {date.strftime('%Y-%m-%d')}...")

        data = self.historical_data_repository.get_historical_data(
            instrument_key=instrument_key,
            from_date=date,
            to_date=date,
            timeframe=timeframe
        )

        self.data_storage.store_data(
            instrument_key=instrument_key,
            timeframe=timeframe,
            date=date,
            data=data
        )
