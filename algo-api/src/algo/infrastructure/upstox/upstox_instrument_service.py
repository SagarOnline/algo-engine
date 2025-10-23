import csv
import os
from typing import Optional, Dict, Any
from algo.domain.instrument.broker_instrument import BrokerInstrumentService, BrokerInstrument
from algo.domain.instrument.instrument import Instrument, Type, Exchange, Expiry
from algo.config_context import get_config


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
        Load broker instrument data from CSV file.
        
        Args:
            instrument: The Instrument object to find mapping for
            
        Returns:
            BrokerInstrument object if found in CSV, None otherwise
        """
        csv_file_path = self._get_csv_file_path(instrument)
        
        if not os.path.exists(csv_file_path):
            return None
            
        try:
            with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # Assuming the CSV has the first row with broker instrument data
                # You may need to adjust this logic based on your CSV structure
                for row in reader:
                    # Map CSV columns to BrokerInstrument fields
                    # Adjust column names based on your actual CSV structure
                    broker_instrument = BrokerInstrument(
                        instrument_key=row.get('instrument_key', instrument.instrument_key),
                        trading_key=row.get('trading_key', ''),
                        instrument_type=Type(row.get('instrument_type', instrument.type.value)) if row.get('instrument_type') else instrument.type,
                        exchange=Exchange(row.get('exchange', instrument.exchange.value)) if row.get('exchange') else instrument.exchange,
                        trading_symbol=row.get('trading_symbol', ''),
                        underlying_key=row.get('underlying_key') if row.get('underlying_key') else None,
                        expiry=Expiry(row.get('expiry')) if row.get('expiry') and row.get('expiry') != '' else instrument.expiry,
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
