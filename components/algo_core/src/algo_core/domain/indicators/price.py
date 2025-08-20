
from typing import Dict, Any, List, Union
from algo_core.domain.indicators.registry import register_indicator
from algo_core.domain.indicators.exceptions import InvalidStrategyConfiguration
import pandas as pd

@register_indicator("price")
def indicator_price(historical_data: Union[List[Dict[str, Any]], pd.DataFrame], params: Dict[str, Any]) -> float:
    if not isinstance(historical_data, pd.DataFrame):
        historical_data = pd.DataFrame(historical_data)

    if historical_data.empty:
        raise RuntimeError("historical_data is empty in price indicator")

    if "price" not in params:
        raise InvalidStrategyConfiguration("price param missing in price indicator")
    
    price_col = params["price"]
    return float(historical_data[price_col].iloc[-1])
