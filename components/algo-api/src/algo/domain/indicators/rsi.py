import pandas as pd
import talib
from typing import Dict, Any, List, Union
from algo.domain.indicators.registry import register_indicator

@register_indicator("rsi")
def indicator_rsi(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    """Calculate RSI value using TA-Lib."""
    # Convert to DataFrame if needed
    if not isinstance(historical_data, pd.DataFrame):
        historical_data = pd.DataFrame(historical_data)

    if historical_data.empty:
        raise RuntimeError("historical_data is empty in rsi indicator")
    
    period = params.get("period", 14)  # Default RSI period = 14
    price_col = "close"

    # TA-Lib expects a NumPy array
    rsi_series = talib.RSI(historical_data[price_col].astype(float).values, timeperiod=period)

    return float(rsi_series[-1])  # last RSI value
