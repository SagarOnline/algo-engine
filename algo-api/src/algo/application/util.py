from babel.numbers import format_currency

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
    return format_percent(value, locale=locale)