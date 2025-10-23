import os
import csv
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from algo.infrastructure.upstox.upstox_instrument_service import UpstoxInstrumentService
from algo.domain.instrument.broker_instrument import BrokerInstrument
from algo.domain.instrument.instrument import Instrument, Type, Exchange, Expiry


class TestUpstoxInstrumentService:
    """Test suite for UpstoxInstrumentService"""

    @pytest.fixture
    def mock_config(self):
        """Mock configuration with temporary directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            upstox_dir = os.path.join(temp_dir, "UPSTOX_API")
            os.makedirs(upstox_dir, exist_ok=True)
            
            mock_config = MagicMock()
            mock_config.instrument_mapping_config.config_dir = temp_dir
            
            with patch('algo.infrastructure.upstox.upstox_instrument_service.get_config', return_value=mock_config):
                yield temp_dir, upstox_dir

    @pytest.fixture
    def sample_instrument(self):
        """Create a sample instrument for testing"""
        return Instrument(
            exchange=Exchange.NSE,
            type=Type.INDEX,
            instrument_key="NSE_NIFTY"
        )

    @pytest.fixture
    def sample_instrument_with_expiry(self):
        """Create a sample instrument with expiry for testing"""
        return Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            instrument_key="NSE_NIFTY24JAN",
            expiry=Expiry.MONTHLY
        )

    def create_csv_file(self, csv_dir, filename, data):
        """Helper method to create CSV files for testing"""
        csv_path = os.path.join(csv_dir, filename)
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            if data:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        return csv_path

    def test_init_creates_mapping_dir_path(self, mock_config):
        """Test that initialization creates correct mapping directory path"""
        temp_dir, upstox_dir = mock_config
        service = UpstoxInstrumentService()
        
        expected_path = os.path.join(temp_dir, "UPSTOX_API")
        assert service._mapping_dir == expected_path

    def test_get_csv_file_path(self, mock_config, sample_instrument):
        """Test CSV file path generation"""
        temp_dir, upstox_dir = mock_config
        service = UpstoxInstrumentService()
        
        csv_path = service._get_csv_file_path(sample_instrument)
        expected_path = os.path.join(upstox_dir, "NSE_NIFTY.csv")
        
        assert csv_path == expected_path

    def test_get_broker_instrument_success(self, mock_config, sample_instrument):
        """Test successful broker instrument retrieval from CSV"""
        temp_dir, upstox_dir = mock_config
        
        # Create CSV file with sample data
        csv_data = [{
            'instrument_key': 'NSE_NIFTY',
            'trading_key': 'NIFTY_INDEX',
            'instrument_type': 'INDEX',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY',
            'underlying_key': 'NIFTY',
            'expiry': '',
            'lot_size': '',
            'tick_size': '0.05',
            'strike_price': ''
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(sample_instrument)
        
        assert broker_instrument is not None
        assert broker_instrument.instrument_key == 'NSE_NIFTY'
        assert broker_instrument.trading_key == 'NIFTY_INDEX'
        assert broker_instrument.instrument_type == Type.INDEX
        assert broker_instrument.exchange == Exchange.NSE
        assert broker_instrument.trading_symbol == 'NIFTY'
        assert broker_instrument.underlying_key == 'NIFTY'
        assert broker_instrument.expiry is None
        assert broker_instrument.lot_size is None
        assert broker_instrument.tick_size == 0.05
        assert broker_instrument.strike_price is None

    def test_get_broker_instrument_with_all_fields(self, mock_config):
        """Test broker instrument retrieval with all fields populated"""
        temp_dir, upstox_dir = mock_config
        
        instrument = Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            instrument_key="NSE_NIFTY24JAN",
            expiry=Expiry.MONTHLY
        )
        
        # Create CSV file with all fields
        csv_data = [{
            'instrument_key': 'NSE_NIFTY24JAN',
            'trading_key': 'NIFTY24JAN',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY24JAN',
            'underlying_key': 'NIFTY',
            'expiry': 'MONTHLY',
            'lot_size': '50',
            'tick_size': '0.05',
            'strike_price': '22000.0'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY24JAN.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(instrument)
        
        assert broker_instrument is not None
        assert broker_instrument.instrument_key == 'NSE_NIFTY24JAN'
        assert broker_instrument.trading_key == 'NIFTY24JAN'
        assert broker_instrument.instrument_type == Type.FUT
        assert broker_instrument.exchange == Exchange.NSE
        assert broker_instrument.trading_symbol == 'NIFTY24JAN'
        assert broker_instrument.underlying_key == 'NIFTY'
        assert broker_instrument.expiry == Expiry.MONTHLY
        assert broker_instrument.lot_size == 50
        assert broker_instrument.tick_size == 0.05
        assert broker_instrument.strike_price == 22000.0

    def test_get_broker_instrument_file_not_found(self, mock_config, sample_instrument):
        """Test when CSV file doesn't exist"""
        temp_dir, upstox_dir = mock_config
        service = UpstoxInstrumentService()
        
        # Don't create the CSV file
        broker_instrument = service.get_broker_instrument(sample_instrument)
        
        assert broker_instrument is None

    def test_get_broker_instrument_empty_csv(self, mock_config, sample_instrument):
        """Test with empty CSV file"""
        temp_dir, upstox_dir = mock_config
        
        # Create empty CSV file
        self.create_csv_file(upstox_dir, "NSE_NIFTY.csv", [])

        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(sample_instrument)
        
        assert broker_instrument is None

    def test_get_broker_instrument_malformed_csv(self, mock_config, sample_instrument):
        """Test with malformed CSV file"""
        temp_dir, upstox_dir = mock_config
        
        # Create malformed CSV file
        csv_path = os.path.join(upstox_dir, "NSE_NIFTY.csv")
        with open(csv_path, 'w') as f:
            f.write("malformed,csv,data\nwithout,proper,headers")
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(sample_instrument)
        
        # Should handle gracefully and return a broker instrument with defaults
        assert broker_instrument is not None

    def test_get_broker_instrument_invalid_enum_values(self, mock_config, sample_instrument):
        """Test with invalid enum values in CSV"""
        temp_dir, upstox_dir = mock_config
        
        # Create CSV with invalid enum values
        csv_data = [{
            'instrument_key': 'NSE_NIFTY.csv',
            'trading_key': 'NIFTY_INDEX',
            'instrument_type': 'INVALID_TYPE',
            'exchange': 'INVALID_EXCHANGE',
            'trading_symbol': 'NIFTY',
            'underlying_key': 'NIFTY',
            'expiry': 'INVALID_EXPIRY',
            'lot_size': 'invalid_number',
            'tick_size': 'invalid_float',
            'strike_price': 'invalid_price'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(sample_instrument)
        
        # Should handle errors gracefully and return None
        assert broker_instrument is None

    def test_get_broker_instrument_partial_data(self, mock_config, sample_instrument):
        """Test with partial data in CSV"""
        temp_dir, upstox_dir = mock_config
        
        # Create CSV with only required fields
        csv_data = [{
            'instrument_key': 'NSE_NIFTY',
            'trading_key': 'NIFTY_INDEX',
            'instrument_type': 'INDEX',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY',
            'underlying_key': '',
            'expiry': '',
            'lot_size': '',
            'tick_size': '',
            'strike_price': ''
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(sample_instrument)
        
        assert broker_instrument is not None
        assert broker_instrument.instrument_key == 'NSE_NIFTY'
        assert broker_instrument.trading_key == 'NIFTY_INDEX'
        assert broker_instrument.instrument_type == Type.INDEX
        assert broker_instrument.exchange == Exchange.NSE
        assert broker_instrument.trading_symbol == 'NIFTY'
        assert broker_instrument.underlying_key is None
        assert broker_instrument.expiry is None
        assert broker_instrument.lot_size is None
        assert broker_instrument.tick_size is None
        assert broker_instrument.strike_price is None

    def test_get_broker_instrument_fallback_to_instrument_data(self, mock_config, sample_instrument_with_expiry):
        """Test fallback to original instrument data when CSV fields are missing"""
        temp_dir, upstox_dir = mock_config
        
        # Create CSV with missing fields - should fallback to instrument data
        csv_data = [{
            'trading_key': 'NSE_NIFTY24JAN',
            'trading_symbol': 'NIFTY24JAN',
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY24JAN.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(sample_instrument_with_expiry)
        
        assert broker_instrument is not None
        assert broker_instrument.instrument_key == sample_instrument_with_expiry.instrument_key
        assert broker_instrument.trading_key == 'NSE_NIFTY24JAN'
        assert broker_instrument.instrument_type == sample_instrument_with_expiry.type
        assert broker_instrument.exchange == sample_instrument_with_expiry.exchange
        assert broker_instrument.trading_symbol == 'NIFTY24JAN'
        assert broker_instrument.expiry == sample_instrument_with_expiry.expiry

    @patch('builtins.print')
    def test_error_handling_and_logging(self, mock_print, mock_config, sample_instrument):
        """Test error handling and logging when file operations fail"""
        temp_dir, upstox_dir = mock_config
        
        # Create a file with permission issues or corrupt data
        csv_path = os.path.join(upstox_dir, "NSE_NIFTY.csv")
        
        # Create a file but mock open to raise an exception
        with open(csv_path, 'w') as f:
            f.write("test")
        
        service = UpstoxInstrumentService()
        
        # Mock open to raise an exception
        with patch('builtins.open', side_effect=PermissionError("Access denied")):
            broker_instrument = service.get_broker_instrument(sample_instrument)
            
            assert broker_instrument is None
            mock_print.assert_called_once()
            assert "Error loading broker instrument" in mock_print.call_args[0][0]

    def test_multiple_calls_always_read_fresh_data(self, mock_config, sample_instrument):
        """Test that multiple calls always read fresh data (no caching)"""
        temp_dir, upstox_dir = mock_config
        
        # Create initial CSV file
        csv_data = [{
            'instrument_key': 'NSE_NIFTY',
            'trading_key': 'NIFTY_INDEX_OLD',
            'instrument_type': 'INDEX',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY_OLD',
        }]
        
        csv_path = self.create_csv_file(upstox_dir, "NSE_NIFTY.csv", csv_data)
        
        service = UpstoxInstrumentService()
        
        # First call
        broker_instrument1 = service.get_broker_instrument(sample_instrument)
        assert broker_instrument1.trading_key == 'NIFTY_INDEX_OLD'
        assert broker_instrument1.trading_symbol == 'NIFTY_OLD'
        
        # Update CSV file
        updated_csv_data = [{
            'instrument_key': 'NSE_NIFTY',
            'trading_key': 'NIFTY_INDEX_NEW',
            'instrument_type': 'INDEX',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY_NEW',
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY.csv", updated_csv_data)
        
        # Second call should read fresh data
        broker_instrument2 = service.get_broker_instrument(sample_instrument)
        assert broker_instrument2.trading_key == 'NIFTY_INDEX_NEW'
        assert broker_instrument2.trading_symbol == 'NIFTY_NEW'
