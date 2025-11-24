import os
import csv
import tempfile
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from algo.infrastructure.upstox.upstox_instrument_service import UpstoxInstrumentService
from algo.domain.instrument.broker_instrument import BrokerInstrument
from algo.domain.instrument.instrument import Expiring, Instrument, Type, Exchange, Expiry


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

    # TODO : add tests for all instrument types
    def test_get_broker_instrument_of_index_type_success(self, mock_config, sample_instrument):
        """Test successful broker instrument retrieval from CSV"""
        temp_dir, upstox_dir = mock_config
        
        # Create CSV file with sample data
        csv_data = [{
            'instrument_key': 'NSE_INDEX|Nifty 50',
            'exchange_token': '26000',
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
        assert broker_instrument.instrument_key == 'NSE_INDEX|Nifty 50'
        assert broker_instrument.trading_key == '26000'
        assert broker_instrument.instrument_type == Type.INDEX
        assert broker_instrument.exchange == Exchange.NSE
        assert broker_instrument.trading_symbol == 'NIFTY'
        assert broker_instrument.underlying_key is None
        assert broker_instrument.expiry is None
        assert broker_instrument.lot_size is None
        assert broker_instrument.tick_size is None
        assert broker_instrument.strike_price is None

    @patch('algo.domain.trading.nse.get_current_monthly_expiry')
    def test_get_broker_instrument_with_all_fields(self, mock_nse_expiry, mock_config):
        """Test broker instrument retrieval with all fields populated"""
        temp_dir, upstox_dir = mock_config
        
        # Mock NSE expiry function to return expected date
        # The CSV has timestamp 1761676199000 which corresponds to October 28, 2025
        expected_expiry_date = datetime(2025, 10, 28, 15, 29)  # October 28, 2025 15:29
        mock_nse_expiry.return_value = expected_expiry_date
        
        instrument = Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            instrument_key="NSE_NIFTY24JAN",
            expiry=Expiry.MONTHLY,
            expiring=Expiring.CURRENT
        )
        
        # Create CSV file with all fields - using original format
        csv_data = [{
            'instrument_key': 'NSE_FO|52168',
            'exchange_token': '52168',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY FUT 28 OCT 25',
            'underlying_key': 'NSE_INDEX|Nifty 50',
            'expiry': '1761676199000', # Tuesday, October 28, 2025 03:29:59 PM (GMT+05:30)
            'lot_size': '75',
            'tick_size': '10',
            'strike_price': '0'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY24JAN.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(instrument)
        
        # Verify NSE function was called with correct parameters
        mock_nse_expiry.assert_called_once_with(
            exchange=Exchange.NSE,
            instrument_type=Type.FUT
        )
        
        assert broker_instrument is not None
        assert broker_instrument.instrument_key == 'NSE_FO|52168'
        assert broker_instrument.trading_key == '52168'
        assert broker_instrument.instrument_type == Type.FUT
        assert broker_instrument.exchange == Exchange.NSE
        assert broker_instrument.trading_symbol == 'NIFTY FUT 28 OCT 25'
        assert broker_instrument.underlying_key == 'NSE_INDEX|Nifty 50'
        assert broker_instrument.lot_size == 75
        assert broker_instrument.tick_size == 10.0
        assert broker_instrument.strike_price == 0.0

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
        
        assert broker_instrument is None

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


    def test_get_broker_instrument_fallback_to_instrument_data(self, mock_config, sample_instrument_with_expiry):
        """Test fallback to original instrument data when CSV fields are missing"""
        temp_dir, upstox_dir = mock_config
        
        # Create CSV with missing fields - should return none
        csv_data = [{
            'trading_key': 'NSE_NIFTY24JAN',
            'trading_symbol': 'NIFTY24JAN',
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY24JAN.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(sample_instrument_with_expiry)
        
        assert broker_instrument is  None

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

    @patch('algo.domain.trading.nse.get_current_monthly_expiry')
    def test_multiple_calls_always_read_fresh_data(self, mock_nse_expiry, mock_config):
        """Test that multiple calls always read fresh data (no caching)"""
        temp_dir, upstox_dir = mock_config
        
        # Create initial CSV file
        csv_data = [{
            'instrument_key': 'NSE_FO|52168',
            'exchange_token': '52168',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY FUT 28 OCT 25',
            'underlying_key': 'NSE_INDEX|Nifty 50',
            'expiry': '1761676199000', # Tuesday, October 28, 2025 03:29:59 PM (GMT+05:30)
            'lot_size': '75',
            'tick_size': '10',
            'strike_price': '0'
        }]
        
        csv_path = self.create_csv_file(upstox_dir, "NSE_NIFTY.csv", csv_data)
        
        service = UpstoxInstrumentService()
        instrument = Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            expiry=Expiry.MONTHLY,
            expiring=Expiring.CURRENT,
            instrument_key="NSE_NIFTY"
        )
        
        # First call
        
        # Mock NSE expiry function to return expected date
        # The CSV has timestamp 1761676199000 which corresponds to October 28, 2025
        expected_expiry_date = datetime(2025, 10, 28, 15, 29)  # October 28, 2025 15:29
        mock_nse_expiry.return_value = expected_expiry_date
        
        broker_instrument1 = service.get_broker_instrument(instrument)
        assert broker_instrument1.trading_key == '52168'
        assert broker_instrument1.trading_symbol == 'NIFTY FUT 28 OCT 25'
        
        # Update CSV file
        updated_csv_data = [{
            'instrument_key': 'NSE_FO|37054',
            'exchange_token': '37054',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY FUT 25 NOV 25',
            'underlying_key': 'NSE_INDEX|Nifty 50',
            'expiry': '1764095399000', # Tuesday, November 25, 2025 03:29:59 PM (GMT+05:30)
            'lot_size': '75',
            'tick_size': '10',
            'strike_price': '0'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY.csv", updated_csv_data)
        
        # Mock NSE expiry function to return expected date
        # The CSV has timestamp 1764095399000 which corresponds to November 25, 2025
        expected_expiry_date = datetime(2025, 11, 25, 15, 29)  # November 25, 2025 15:29
        mock_nse_expiry.return_value = expected_expiry_date
        
        # Second call should read fresh data
        broker_instrument2 = service.get_broker_instrument(instrument)
        assert broker_instrument2.trading_key == '37054'
        assert broker_instrument2.trading_symbol == 'NIFTY FUT 25 NOV 25'

    @patch('algo.domain.trading.nse.get_next1_monthly_expiry')
    def test_get_broker_instrument_fut_next1_expiry(self, mock_nse_expiry, mock_config):
        """Test FUT instrument matching with NEXT1 expiry"""
        temp_dir, upstox_dir = mock_config
        
        # Mock NSE expiry function for NEXT1
        expected_expiry_date = datetime(2025, 11, 25, 15, 29)  # November 25, 2025
        mock_nse_expiry.return_value = expected_expiry_date
        
        instrument = Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            instrument_key="NSE_NIFTY_NEXT1",
            expiry=Expiry.MONTHLY,
            expiring=Expiring.NEXT1
        )
        
        # Create CSV with matching expiry date
        csv_data = [{
            'instrument_key': 'NSE_FO|52169',
            'trading_key': 'NIFTY_NEXT1_TRADING',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY FUT 25 NOV 25',
            'expiry': '1764095399000',  # Matches NEXT1 expiry
            'lot_size': '75'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY_NEXT1.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(instrument)
        
        # Verify NSE function was called with correct parameters
        mock_nse_expiry.assert_called_once_with(
            exchange=Exchange.NSE,
            instrument_type=Type.FUT
        )
        
        assert broker_instrument is not None
        assert broker_instrument.trading_symbol == 'NIFTY FUT 25 NOV 25'

    @patch('algo.domain.trading.nse.get_next2_monthly_expiry')
    def test_get_broker_instrument_fut_next2_expiry(self, mock_nse_expiry, mock_config):
        """Test FUT instrument matching with NEXT2 expiry"""
        temp_dir, upstox_dir = mock_config
        
        # Mock NSE expiry function for NEXT2
        expected_expiry_date = datetime(2025, 12, 30, 15, 29)  # December 30, 2025
        mock_nse_expiry.return_value = expected_expiry_date
        
        instrument = Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            instrument_key="NSE_NIFTY_NEXT2",
            expiry=Expiry.MONTHLY,
            expiring=Expiring.NEXT2
        )
        
        # Create CSV with matching expiry date
        csv_data = [{
            'instrument_key': 'NSE_FO|52170',
            'trading_key': 'NIFTY_NEXT2_TRADING',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY FUT 30 DEC 25',
            'expiry': '1767119399000',  # Matches NEXT2 expiry
            'lot_size': '75'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY_NEXT2.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(instrument)
        
        # Verify NSE function was called with correct parameters
        mock_nse_expiry.assert_called_once_with(
            exchange=Exchange.NSE,
            instrument_type=Type.FUT
        )
        
        assert broker_instrument is not None
        assert broker_instrument.trading_symbol == 'NIFTY FUT 30 DEC 25'

    @patch('algo.domain.trading.nse.get_current_monthly_expiry')
    def test_get_broker_instrument_fut_expiry_mismatch(self, mock_nse_expiry, mock_config):
        """Test FUT instrument when CSV expiry doesn't match NSE expiry"""
        temp_dir, upstox_dir = mock_config
        
        # Mock NSE expiry function
        expected_expiry_date = datetime(2025, 10, 28, 15, 29)
        mock_nse_expiry.return_value = expected_expiry_date
        
        instrument = Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            instrument_key="NSE_NIFTY_MISMATCH",
            expiry=Expiry.MONTHLY,
            expiring=Expiring.CURRENT
        )
        
        # Create CSV with non-matching expiry date
        csv_data = [{
            'instrument_key': 'NSE_FO|52171',
            'trading_key': 'NIFTY_MISMATCH_TRADING',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY FUT 15 OCT 25',
            'expiry': '2025-10-15',  # Different from expected 2025-10-28
            'lot_size': '75'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY_MISMATCH.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(instrument)
        
        # Should not find matching instrument due to expiry mismatch
        assert broker_instrument is None

    def test_get_broker_instrument_fut_no_expiry_requirement(self, mock_config):
        """Test FUT instrument without MONTHLY expiry requirement"""
        temp_dir, upstox_dir = mock_config
        
        instrument = Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            instrument_key="NSE_NIFTY_NO_EXP",
            expiry=None  # No expiry requirement
        )
        
        # Create CSV data
        csv_data = [{
            'instrument_key': 'NSE_FO|52172',
            'trading_key': 'NIFTY_NO_EXP_TRADING',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY FUT',
            'expiry': '2025-10-28',
            'lot_size': '75'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY_NO_EXP.csv", csv_data)
        
        service = UpstoxInstrumentService()
        broker_instrument = service.get_broker_instrument(instrument)
        
        # Should match since no expiry requirement
        assert broker_instrument is not None
        assert broker_instrument.trading_symbol == 'NIFTY FUT'

    @patch('algo.domain.trading.nse.get_current_monthly_expiry')
    def test_get_broker_instrument_fut_missing_expiring_returns_none(self, mock_nse_expiry, mock_config):
        """Test that missing expiring field returns None"""
        temp_dir, upstox_dir = mock_config
        
        instrument = Instrument(
            exchange=Exchange.NSE,
            type=Type.FUT,
            instrument_key="NSE_NIFTY_NO_EXPIRING",
            expiry=Expiry.MONTHLY,
            expiring=None  # Missing expiring field
        )
        
        # Create CSV data
        csv_data = [{
            'instrument_key': 'NSE_FO|52173',
            'trading_key': 'NIFTY_NO_EXPIRING_TRADING',
            'instrument_type': 'FUT',
            'exchange': 'NSE',
            'trading_symbol': 'NIFTY FUT',
            'expiry': '2025-10-28',
            'lot_size': '75'
        }]
        
        self.create_csv_file(upstox_dir, "NSE_NIFTY_NO_EXPIRING.csv", csv_data)
        
        service = UpstoxInstrumentService()
        
        broker_instrument = service.get_broker_instrument(instrument)
        assert broker_instrument is None

