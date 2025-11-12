import csv
import os
from typing import Optional, Dict, Any
from datetime import datetime
from algo.domain.instrument.broker_instrument import BrokerInstrumentService, BrokerInstrument
from algo.domain.instrument.instrument import Expiring, Instrument, Type, Exchange, Expiry
from algo.config_context import get_config
from algo.domain.trading import nse


class UpstoxInstrumentService(BrokerInstrumentService):
    """
    Upstox-specific implementation of BrokerInstrumentService.
    Maps Instrument objects to BrokerInstrument objects using CSV mapping files.
    """
    
    def __init__(self):
        """Initialize the Upstox instrument service."""
        config = get_config()
        base_dir = config.instrument_mapping_config.config_dir
        broker_dir = "UPSTOX_API"
        self._mapping_dir = os.path.join(base_dir, broker_dir)
        
    def _get_csv_file_path(self, instrument: Instrument) -> str:
        """
        Get the CSV file path for the given instrument.
        
        Args:
            instrument: The Instrument object
            
        Returns:
            Full path to the CSV file containing broker instrument mapping
        """
        filename = f"{instrument.instrument_key}.csv"
        return os.path.join(self._mapping_dir, filename)
    
    def _load_broker_instrument_from_csv(self, instrument: Instrument) -> Optional[BrokerInstrument]:
        """
        Load broker instrument data from CSV file with matching logic based on instrument type.
        
        Args:
            instrument: The Instrument object to find mapping for
            
        Returns:
            BrokerInstrument object if found in CSV with matching criteria, None otherwise
        """
        csv_file_path = self._get_csv_file_path(instrument)
        
        if not os.path.exists(csv_file_path):
            return None
            
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Apply matching logic based on instrument type
                for row in reader:
                    if self._matches_instrument(instrument, row):
                        # Map CSV columns to BrokerInstrument fields
                        broker_instrument = BrokerInstrument(
                            instrument_key=row.get('instrument_key', instrument.instrument_key),
                            trading_key=row.get('exchange_token', ''),
                            instrument_type=Type(row.get('instrument_type', instrument.type.value)) if row.get('instrument_type') else instrument.type,
                            exchange=Exchange(row.get('exchange', instrument.exchange.value)) if row.get('exchange') else instrument.exchange,
                            trading_symbol=row.get('trading_symbol', ''),
                            underlying_key=row.get('underlying_key') if row.get('underlying_key') else None,
                            expiry= instrument.expiry,
                            lot_size=int(row.get('lot_size')) if row.get('lot_size') and row.get('lot_size') != '' else None,
                            tick_size=float(row.get('tick_size')) if row.get('tick_size') and row.get('tick_size') != '' else None,
                            strike_price=float(row.get('strike_price')) if row.get('strike_price') and row.get('strike_price') != '' else None
                        )
                        return broker_instrument
                    
        except Exception as e:
            # Log error in production - for now, return None
            print(f"Error loading broker instrument from {csv_file_path}: {e}")
            return None
            
        return None
    
    def get_broker_instrument(self, instrument: Instrument) -> Optional[BrokerInstrument]:
        """
        Convert an Instrument object to a BrokerInstrument object using Upstox mapping.
        Always reads fresh data from CSV file.
        
        Args:
            instrument: The Instrument object to convert
            
        Returns:
            BrokerInstrument object if mapping is successful, None otherwise
        """
        # Always load from CSV file (no caching)
        return self._load_broker_instrument_from_csv(instrument)
    
    def _parse_expiry_date(self, date_str: str) -> Optional[datetime]:
        """Parse expiry date from milliseconds timestamp format."""
        if not date_str or not date_str.strip():
            return None
        
        date_str = date_str.strip()
        
        try:
            expiry_ms = int(date_str)
            return datetime.fromtimestamp(expiry_ms / 1000)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Unable to parse expiry timestamp: {date_str}") from e
    
    def _matches_fut_expiry(self, instrument: Instrument, row: Dict[str, Any]) -> bool:
        """Check if FUT instrument expiry matches CSV row expiry."""
        if not instrument.expiry or instrument.expiry != Expiry.MONTHLY:
            return True  # No specific expiry requirement
        
        if not instrument.expiring:
            raise ValueError(f"Expiring is required for FUT instruments with MONTHLY expiry. Instrument: {instrument.instrument_key}")
        
        # Get the appropriate NSE expiry function
        expiry_functions = {
            Expiring.CURRENT: nse.get_current_monthly_expiry,
            Expiring.NEXT1: nse.get_next1_monthly_expiry,
            Expiring.NEXT2: nse.get_next2_monthly_expiry
        }
        
        expiry_func = expiry_functions.get(instrument.expiring)
        if not expiry_func:
            return True  # Unknown expiring type, fallback to type matching
        
        try:
            # Get expected expiry date
            expected_expiry = expiry_func(
                exchange=instrument.exchange,
                instrument_type=instrument.type
            )
            
            # Parse row expiry date from milliseconds timestamp
            expiry_str = row.get('expiry', '')
            if not expiry_str:
                return False
            
            row_expiry = self._parse_expiry_date(expiry_str)
            
            # Compare dates
            return expected_expiry.date() == row_expiry.date()
            
        except Exception as e:
            # Propagate NSE function exceptions to caller
            raise e
    
    def _matches_index_instrument(self, instrument: Instrument, row: Dict[str, Any]) -> bool:
        """Match INDEX instrument by type only."""
        row_type = row.get('instrument_type', '').upper()
        return row_type == Type.INDEX.value.upper()

    def _matches_fut_instrument(self, instrument: Instrument, row: Dict[str, Any]) -> bool:
        """Match FUT instrument by type and expiry."""
        row_type = row.get('instrument_type', '').upper()
        
        # First check type match
        if row_type != Type.FUT.value.upper():
            return False
        
        # Then check expiry match
        return self._matches_fut_expiry(instrument, row)

    def _matches_option_instrument(self, instrument: Instrument, row: Dict[str, Any]) -> bool:
        """Match option instruments (CE/PE) - can be extended later."""
        row_type = row.get('instrument_type', '').upper()
        target_type = instrument.type.value.upper()
        
        if row_type != target_type:
            return False
        
        # TODO: Add strike price, expiry matching for options
        return True

    def _matches_default_instrument(self, instrument: Instrument, row: Dict[str, Any]) -> bool:
        """Default matching by instrument type only."""
        row_type = row.get('instrument_type', '').upper()
        target_type = instrument.type.value.upper()
        return row_type == target_type
    
    def _matches_instrument(self, instrument: Instrument, row: Dict[str, Any]) -> bool:
        """
        Check if a CSV row matches the given instrument based on instrument type-specific criteria.
        
        Args:
            instrument: The Instrument object to match
            row: CSV row data as dictionary
            
        Returns:
            True if the row matches the instrument, False otherwise
        """
        # Dispatch to type-specific matchers
        matchers = {
            Type.INDEX: self._matches_index_instrument,
            Type.FUT: self._matches_fut_instrument,
            Type.CE: self._matches_option_instrument,
            Type.PE: self._matches_option_instrument,
            # Add more types as needed
        }
        
        matcher = matchers.get(instrument.type, self._matches_default_instrument)
        return matcher(instrument, row)
