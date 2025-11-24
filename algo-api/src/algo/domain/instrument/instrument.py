from enum import Enum
from typing import Any, Dict,Optional


class Segment(Enum):
    FNO = "FNO"
    EQ = "EQ"


class Type(Enum):
    FUT = "FUT"
    CE = "CE"
    PE = "PE"
    EQ = "EQ"
    INDEX = "INDEX"


class Exchange(Enum):
    NSE = "NSE"
    BSE = "BSE"


class Expiry(Enum):
    MONTHLY = "MONTHLY"
    WEEKLY = "WEEKLY"


class Expiring(Enum):
    CURRENT = "CURRENT"
    NEXT1 = "NEXT1"
    NEXT2 = "NEXT2"


class Instrument:
    def __init__(self,
        exchange: Exchange,
        type: Type,
        instrument_key: str,
        expiry: Optional[Expiry] = None,
        expiring: Optional[Expiring] = None,
        atm: Optional[int] = None,

    ):
        self.exchange = Exchange(exchange)
        self.instrument_key = instrument_key
        self.expiry = Expiry(expiry) if expiry else None
        self.expiring = Expiring(expiring) if expiring else None
        self.atm = atm
        self.type = Type(type) if type else None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exchange": self.exchange.value,
            "instrument_key": self.instrument_key,
            "expiry": self.expiry.value if self.expiry else None,
            "expiring": self.expiring.value if self.expiring else None,
            "atm": self.atm,
            "type": self.type.value if self.type else None
        }


    def __eq__(self, other):
        if not isinstance(other, Instrument):
            return False
        return (
            self.exchange == other.exchange and
            self.instrument_key == other.instrument_key and
            self.expiry == other.expiry and
            self.expiring == other.expiring and
            self.atm == other.atm and
            self.type == other.type
        )