from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional
from .instrument import Instrument, Type, Exchange, Expiry


class BrokerInstrument:
    def __init__(self,
        instrument_key: str,
        trading_key: str,
        instrument_type: Type,
        exchange: Exchange,
        trading_symbol: str,
        underlying_key: Optional[str] = None,
        expiry: Optional[Expiry] = None,
        lot_size: Optional[int] = None,
        tick_size: Optional[float] = None,
        strike_price: Optional[float] = None
    ):
        self.instrument_key = instrument_key
        self.trading_key = trading_key
        self.instrument_type = Type(instrument_type)
        self.exchange = Exchange(exchange)
        self.trading_symbol = trading_symbol
        self.underlying_key = underlying_key
        self.expiry = Expiry(expiry) if expiry else None
        self.lot_size = lot_size
        self.tick_size = tick_size
        self.strike_price = strike_price

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument_type": self.instrument_type.value,
            "exchange": self.exchange.value,
            "instrument_key": self.instrument_key,
            "trading_key": self.trading_key,
            "trading_symbol": self.trading_symbol,
            "expiry": self.expiry.value if self.expiry else None,
            "lot_size": self.lot_size,
            "underlying_key": self.underlying_key,
            "tick_size": self.tick_size,
            "strike_price": self.strike_price
        }

    def __eq__(self, other):
        if not isinstance(other, BrokerInstrument):
            return False
        return (
            self.instrument_type == other.instrument_type and
            self.exchange == other.exchange and
            self.instrument_key == other.instrument_key and
            self.trading_key == other.trading_key and
            self.trading_symbol == other.trading_symbol and
            self.expiry == other.expiry and
            self.lot_size == other.lot_size and
            self.underlying_key == other.underlying_key and
            self.tick_size == other.tick_size and
            self.strike_price == other.strike_price
        )


class BrokerInstrumentService(ABC):
    """
    Abstract interface for broker-specific instrument services.
    Implement this interface to provide broker-specific mapping logic
    for converting Instrument objects to BrokerInstrument objects.
    """
    
    @abstractmethod
    def get_broker_instrument(self, instrument: Instrument) -> Optional[BrokerInstrument]:
        """
        Convert an Instrument object to a BrokerInstrument object.
        This method must be implemented by broker-specific services.
        
        Args:
            instrument: The Instrument object to convert
            
        Returns:
            BrokerInstrument object if mapping is successful, None otherwise
        """
        pass
    
    def get_broker_instruments_for_instruments(self, instruments: list[Instrument]) -> list[BrokerInstrument]:
        """
        Convert multiple Instrument objects to BrokerInstrument objects.
        This default implementation can be overridden by subclasses if needed.
        
        Args:
            instruments: List of Instrument objects to convert
            
        Returns:
            List of BrokerInstrument objects (excludes failed conversions)
        """
        broker_instruments = []
        for instrument in instruments:
            broker_instrument = self.get_broker_instrument(instrument)
            if broker_instrument:
                broker_instruments.append(broker_instrument)
        return broker_instruments
