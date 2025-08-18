from typing import Dict, Any, List,Union
from domain.indicators.registry import register_indicator
import pandas as pd

@register_indicator("price")
def indicator_price(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    price_col = params.get("price", "close")
    return float(historical_data[price_col].iloc[-1])
