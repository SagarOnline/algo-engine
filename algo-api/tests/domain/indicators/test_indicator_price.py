import pytest
import pandas as pd
from algo.domain.indicators.exceptions import InvalidStrategyConfiguration
from algo.domain.indicators.registry import register_indicator
from algo.domain.indicators.price import indicator_price  # replace with actual module path


def test_indicator_price_with_dataframe():
    # Arrange
    df = pd.DataFrame(
        [
            {"open": 100, "high": 110, "low": 95, "close": 105},
            {"open": 106, "high": 112, "low": 100, "close": 108},
        ]
    )
    params = {"price": "close"}

    # Act
    result = indicator_price(df, params)

    # Assert
    assert result == 108.0


def test_indicator_price_with_no_price_param():
    df = pd.DataFrame(
        [
            {"open": 200, "high": 210, "low": 195, "close": 205},
            {"open": 206, "high": 212, "low": 200, "close": 208},
        ]
    )
    # no "price" key → should default to "close"
    with pytest.raises(InvalidStrategyConfiguration):
        indicator_price(df, {})

def test_indicator_price_with_no_historical_data():
    df = pd.DataFrame([])
    params = {"price": "close"}
    with pytest.raises(RuntimeError, match="historical_data is empty in price indicator"):
        indicator_price(df, params)

def test_indicator_price_with_list_of_dicts():
    data = [
        {"open": 300, "high": 310, "low": 295, "close": 305},
        {"open": 306, "high": 312, "low": 300, "close": 308},
    ]
    df = pd.DataFrame(data)
    params = {"price": "close"}

    result = indicator_price(df, params)

    assert result == 308.0
    
def test_indicator_price_high():
    data = [
        {"open": 300, "high": 310, "low": 295, "close": 305},
        {"open": 306, "high": 312, "low": 300, "close": 308},
    ]
    df = pd.DataFrame(data)
    params = {"price": "high"}

    result = indicator_price(df, params)

    assert result == 312.0