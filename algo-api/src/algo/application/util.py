from datetime import datetime
from babel.numbers import format_currency
from babel.dates import format_datetime
import pytz

def fmt_currency(value, currency='INR', locale='en_IN'):
    """
    Format a number as currency using Babel.

    Args:
        value (float): The amount to format.
        currency (str): The currency code (default 'INR').
        locale (str): The locale code (default 'en_IN').

    Returns:
        str: The formatted currency string.
    """
    return format_currency(value, currency, locale=locale)

def fmt_percent(value, locale='en_IN'):
    """
    Format a number as a percentage using Babel.

    Args:
        value (float): The percentage value to format (e.g., 0.15 for 15%).
        locale (str): The locale code (default 'en_IN').

    Returns:
        str: The formatted percentage string.
    """
    from babel.numbers import format_percent
    return format_percent(value, format='#,##0.00%', locale=locale)

def fmt_datetime(dt: datetime, fmt: str = "EEE, dd MMM yyyy HH:mm") -> str:
    """
    Format a datetime object into Indian Standard Time (IST)
    using Babel.

    Args:
        dt (datetime): The datetime object (naive or timezone-aware).
        fmt (str): The format string for Babel (default: "EEE, dd MMM yyyy HH:mm").

    Returns:
        str: Formatted datetime string in IST.
    """
    # Ensure datetime is timezone-aware in UTC if naive
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=pytz.utc)

    # Convert to IST
    ist = pytz.timezone("Asia/Kolkata")
    dt_ist = dt.astimezone(ist)

    # Format with Babel
    return format_datetime(dt_ist, fmt, locale="en_IN", tzinfo=ist)