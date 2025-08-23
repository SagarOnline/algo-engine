import pandas as pd
import talib
from typing import Dict, Any, List, Union
from algo_core.domain.indicators.registry import register_indicator

@register_indicator("atr")
def indicator_atr(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    """Calculate ATR (Average True Range) using TA-Lib."""
    # Convert to DataFrame if needed
    if not isinstance(historical_data, pd.DataFrame):
        historical_data = pd.DataFrame(historical_data)

    if historical_data.empty:
        raise RuntimeError("historical_data is empty in atr indicator")
    
    period = params.get("period", 14)

    # Ensure required columns exist
    for col in ["high", "low", "close"]:
        if col not in historical_data.columns:
            raise ValueError(f"Missing required column '{col}' in historical_data")

    # TA-Lib expects NumPy arrays
    atr_series = talib.ATR(
        historical_data["high"].astype(float).values,
        historical_data["low"].astype(float).values,
        historical_data["close"].astype(float).values,
        timeperiod=period
    )

    return float(atr_series[-1])  # last ATR value
