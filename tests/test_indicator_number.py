import pytest
import pandas as pd
from domain.indicators.registry import register_indicator
from domain.indicators.number import indicator_number  # replace with actual module path


def test_indicator_number():
    # Arrange
    df = pd.DataFrame(
        [
            {"open": 100, "high": 110, "low": 95, "close": 105},
            {"open": 106, "high": 112, "low": 100, "close": 108},
        ]
    )
    params = {"value": 100}

    # Act
    result = indicator_number(df, params)

    # Assert
    assert result == 100.0