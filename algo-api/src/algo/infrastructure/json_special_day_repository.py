"""
JSON implementation of the SpecialDayRepository interface.

This module provides a concrete implementation that loads special day data
from a JSON file and caches it in memory for efficient access.
"""

import json
import logging
from datetime import date, time, datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..domain.strategy.special_day_repository import SpecialDayRepository, SpecialDay, DayType
from ..domain.strategy.strategy import Exchange


logger = logging.getLogger(__name__)


class JsonSpecialDayRepository(SpecialDayRepository):
    """
    JSON file-based implementation of SpecialDayRepository.
    
    This implementation supports two modes:
    1. Single file mode: Load from a single JSON file (legacy support)
    2. Directory mode: Load from exchange-year specific files (e.g., nse_2025.json)
    
    For directory mode, files should be named as: {exchange}_{year}.json
    Example: nse_2025.json, bse_2024.json
    
    Each JSON file should contain an array of special day objects with the following structure:
    
    [
        {
            "date": "2023-01-01",
            "day_type": "HOLIDAY",
            "description": "New Year's Day",
            "metadata": {"category": "national"}
        },
        {
            "date": "2023-12-24",
            "day_type": "SPECIAL_TRADING_DAY",
            "description": "Christmas Eve - Early Close",
            "trading_start": "09:15:00",
            "trading_end": "13:00:00",
            "metadata": {"early_close": true}
        }
    ]
    """
    
    def __init__(self, json_path: str, exchange: Exchange = Exchange.NSE):
        """
        Initialize the repository with a JSON file path or directory path.
        
        Args:
            json_path: Path to the JSON file or directory containing special day data
            exchange: Exchange enum value (defaults to NSE)
            
        Raises:
            FileNotFoundError: If the JSON file/directory doesn't exist
            ValueError: If the JSON file format is invalid
        """
        self.json_path = Path(json_path)
        self.exchange = exchange
        self._cache: Dict[str, Dict[int, List[SpecialDay]]] = {}  # {exchange: {year: [SpecialDay]}}
        self._last_modified: Dict[str, float] = {}  # {file_path: timestamp}
        self._is_directory_mode = self.json_path.is_dir()
        
        if not self.json_path.exists():
            raise FileNotFoundError(f"JSON path not found: {json_path}")
        
        # Load initial data
        self.refresh_cache()
    
    def _exchange_from_filename(self, filename: str) -> Optional[Exchange]:
        """
        Convert filename exchange part to Exchange enum.
        
        Args:
            filename: The filename part (e.g., 'nse' from 'nse_2025.json')
            
        Returns:
            Exchange enum value or None if not found
        """
        filename_lower = filename.lower()
        for exchange in Exchange:
            if exchange.value.lower() == filename_lower:
                return exchange
        return None
    
    def _exchange_to_filename(self, exchange: Exchange) -> str:
        """
        Convert Exchange enum to filename format.
        
        Args:
            exchange: Exchange enum value
            
        Returns:
            Lowercase exchange name for filename
        """
        return exchange.value.lower()
    
    def refresh_cache(self) -> None:
        """
        Refresh the internal cache by reloading data from the JSON file(s).
        
        For directory mode, this method loads all exchange-year files.
        For single file mode, it loads the single JSON file.
        
        Raises:
            ValueError: If the JSON file format is invalid
            FileNotFoundError: If required files no longer exist
        """
        try:
            if self._is_directory_mode:
                self._refresh_directory_cache()
            else:
                self._refresh_single_file_cache()
                
            logger.info(f"Cache refreshed. Total special days: {self._get_total_cached_days()}")
            
        except Exception as e:
            logger.error(f"Error refreshing cache: {e}")
            raise
    
    def _refresh_directory_cache(self) -> None:
        """Refresh cache for directory mode (exchange-year specific files)."""
        # Find all JSON files in the directory
        json_files = list(self.json_path.glob("*.json"))
        
        for json_file in json_files:
            # Parse exchange and year from filename (e.g., nse_2025.json)
            file_stem = json_file.stem
            if '_' not in file_stem:
                logger.warning(f"Skipping file with invalid name format: {json_file.name}")
                continue
            
            try:
                exchange_name, year_str = file_stem.split('_', 1)
                exchange = self._exchange_from_filename(exchange_name)
                if exchange is None:
                    logger.warning(f"Skipping file with unsupported exchange: {json_file.name}")
                    continue
                year = int(year_str)
            except (ValueError, AttributeError):
                logger.warning(f"Skipping file with invalid name format: {json_file.name}")
                continue
            
            # Check if file has been modified
            file_path_str = str(json_file)
            current_modified = json_file.stat().st_mtime
            if (file_path_str in self._last_modified and 
                current_modified <= self._last_modified[file_path_str]):
                continue
            
            # Load and parse the file
            logger.debug(f"Loading special days from {json_file}")
            
            try:
                with open(json_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in file {json_file}: {e}")
            
            if not isinstance(data, list):
                raise ValueError(f"JSON file {json_file} must contain an array of special day objects")
            
            # Initialize exchange cache if needed
            exchange_key = exchange.value
            if exchange_key not in self._cache:
                self._cache[exchange_key] = {}
            
            # Parse and cache special days
            self._cache[exchange_key][year] = []
            for item in data:
                special_day = self._parse_special_day(item)
                if special_day.date.year != year:
                    logger.warning(f"Date {special_day.date} in file {json_file} doesn't match year {year}")
                self._cache[exchange_key][year].append(special_day)
            
            # Sort by date
            self._cache[exchange_key][year].sort(key=lambda x: x.date)
            self._last_modified[file_path_str] = current_modified
    
    def _refresh_single_file_cache(self) -> None:
        """Refresh cache for single file mode (legacy support)."""
        current_modified = self.json_path.stat().st_mtime
        file_path_str = str(self.json_path)
        
        if (file_path_str in self._last_modified and 
            current_modified <= self._last_modified[file_path_str]):
            logger.debug(f"JSON file {self.json_path} not modified, skipping cache refresh")
            return
        
        logger.info(f"Loading special days from {self.json_path}")
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in file {self.json_path}: {e}")
        
        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of special day objects")
        
        # Clear existing cache for this exchange
        exchange_key = self.exchange.value
        if exchange_key not in self._cache:
            self._cache[exchange_key] = {}
        else:
            self._cache[exchange_key].clear()
        
        # Parse and cache special days by year
        for item in data:
            special_day = self._parse_special_day(item)
            year = special_day.date.year
            
            if year not in self._cache[exchange_key]:
                self._cache[exchange_key][year] = []
            
            self._cache[exchange_key][year].append(special_day)
        
        # Sort each year's data by date
        for year_data in self._cache[exchange_key].values():
            year_data.sort(key=lambda x: x.date)
        
        self._last_modified[file_path_str] = current_modified
    
    def _get_total_cached_days(self) -> int:
        """Get total number of cached special days across all exchanges and years."""
        total = 0
        for exchange_data in self._cache.values():
            for year_data in exchange_data.values():
                total += len(year_data)
        return total
    
    def _parse_special_day(self, data: Dict[str, Any]) -> SpecialDay:
        """
        Parse a special day object from JSON data.
        
        Args:
            data: Dictionary containing special day data from JSON
            
        Returns:
            SpecialDay object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        try:
            # Parse required fields
            date_str = data.get('date')
            if not date_str:
                raise ValueError("Missing required field 'date'")
            
            special_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            day_type_str = data.get('day_type')
            if not day_type_str:
                raise ValueError("Missing required field 'day_type'")
            
            try:
                day_type = DayType(day_type_str)
            except ValueError:
                raise ValueError(f"Invalid day_type: {day_type_str}")
            
            description = data.get('description', '')
            if not description:
                raise ValueError("Missing required field 'description'")
            
            # Parse optional trading hours
            trading_start = None
            trading_end = None
            
            trading_start_str = data.get('trading_start')
            if trading_start_str:
                trading_start = datetime.strptime(trading_start_str, '%H:%M:%S').time()
            
            trading_end_str = data.get('trading_end')
            if trading_end_str:
                trading_end = datetime.strptime(trading_end_str, '%H:%M:%S').time()
            
            # Parse optional metadata
            metadata = data.get('metadata', {})
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary")
            
            return SpecialDay(
                date=special_date,
                day_type=day_type,
                description=description,
                trading_start=trading_start,
                trading_end=trading_end,
                metadata=metadata
            )
            
        except KeyError as e:
            raise ValueError(f"Missing required field: {e}")
        except ValueError as e:
            raise ValueError(f"Invalid special day data: {e}")
    
    def get_special_days_for_year(self, year: int, exchange: Optional[Exchange] = None) -> List[SpecialDay]:
        """
        Retrieve all special days for a given year and exchange.
        
        Args:
            year: The year for which to retrieve special days
            exchange: The exchange for which to retrieve special days (if None, uses the default exchange)
            
        Returns:
            List of SpecialDay objects for the specified year and exchange, sorted by date
            
        Raises:
            ValueError: If year is invalid (before 1900 or after 2100)
        """
        if year < 1900 or year > 2100:
            raise ValueError(f"Invalid year: {year}. Year must be between 1900 and 2100")
        
        target_exchange = exchange or self.exchange
        
        # Check if cache needs refresh
        if self._is_directory_mode:
            # For directory mode, check if the specific file exists and needs refresh
            expected_file = self.json_path / f"{self._exchange_to_filename(target_exchange)}_{year}.json"
            if expected_file.exists():
                current_modified = expected_file.stat().st_mtime
                file_path_str = str(expected_file)
                if (file_path_str not in self._last_modified or 
                    current_modified > self._last_modified[file_path_str]):
                    self.refresh_cache()
        else:
            # For single file mode, check the main file
            if self.json_path.exists():
                current_modified = self.json_path.stat().st_mtime
                file_path_str = str(self.json_path)
                if (file_path_str not in self._last_modified or 
                    current_modified > self._last_modified[file_path_str]):
                    self.refresh_cache()
        
        return self._cache.get(target_exchange.value, {}).get(year, []).copy()
    
    def get_special_day(self, target_date: date, exchange: Optional[Exchange] = None) -> Optional[SpecialDay]:
        """
        Retrieve special day information for a specific date and exchange.
        
        Args:
            target_date: The date to check for special day information
            exchange: The exchange to check (if None, uses the default exchange)
            
        Returns:
            SpecialDay object if the date is a special day, None otherwise
        """
        year = target_date.year
        special_days = self.get_special_days_for_year(year, exchange)
        
        for special_day in special_days:
            if special_day.date == target_date:
                return special_day
        
        return None
    
    def get_holidays(self, year: int, exchange: Optional[Exchange] = None) -> List[SpecialDay]:
        """
        Retrieve all holidays for a given year and exchange.
        
        Args:
            year: The year for which to retrieve holidays
            exchange: The exchange for which to retrieve holidays (if None, uses the default exchange)
            
        Returns:
            List of SpecialDay objects with day_type HOLIDAY for the specified year and exchange
            
        Raises:
            ValueError: If year is invalid
        """
        all_special_days = self.get_special_days_for_year(year, exchange)
        return [day for day in all_special_days if day.day_type == DayType.HOLIDAY]
    
    def get_special_trading_days(self, year: int, exchange: Optional[Exchange] = None) -> List[SpecialDay]:
        """
        Retrieve all special trading days for a given year and exchange.
        
        Args:
            year: The year for which to retrieve special trading days
            exchange: The exchange for which to retrieve special trading days (if None, uses the default exchange)
            
        Returns:
            List of SpecialDay objects with day_type SPECIAL_TRADING_DAY for the specified year and exchange
            
        Raises:
            ValueError: If year is invalid
        """
        all_special_days = self.get_special_days_for_year(year, exchange)
        return [day for day in all_special_days if day.day_type == DayType.SPECIAL_TRADING_DAY]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current cache.
        
        Returns:
            Dictionary with cache statistics including exchanges loaded,
            years per exchange, total special days, holidays, and special trading days
        """
        stats = {
            'mode': 'directory' if self._is_directory_mode else 'single_file',
            'exchanges': {},
            'total_special_days': 0,
            'total_holidays': 0,
            'total_special_trading_days': 0,
            'last_modified_files': list(self._last_modified.keys())
        }
        
        for exchange, years_data in self._cache.items():
            exchange_stats = {
                'years_loaded': sorted(years_data.keys()),
                'special_days': 0,
                'holidays': 0,
                'special_trading_days': 0
            }
            
            for year_data in years_data.values():
                exchange_stats['special_days'] += len(year_data)
                exchange_stats['holidays'] += len([d for d in year_data if d.day_type == DayType.HOLIDAY])
                exchange_stats['special_trading_days'] += len([d for d in year_data if d.day_type == DayType.SPECIAL_TRADING_DAY])
            
            stats['exchanges'][exchange] = exchange_stats
            stats['total_special_days'] += exchange_stats['special_days']
            stats['total_holidays'] += exchange_stats['holidays']
            stats['total_special_trading_days'] += exchange_stats['special_trading_days']
        
        return stats
    
    def get_available_exchanges(self) -> List[str]:
        """
        Get list of available exchanges in the cache.
        
        Returns:
            List of exchange names that have data loaded
        """
        return list(self._cache.keys())
    
    def get_available_years(self, exchange: Optional[Exchange] = None) -> List[int]:
        """
        Get list of available years for a specific exchange.
        
        Args:
            exchange: The exchange (if None, uses the default exchange)
            
        Returns:
            List of years that have data loaded for the exchange
        """
        target_exchange = exchange or self.exchange
        return sorted(self._cache.get(target_exchange.value, {}).keys())
