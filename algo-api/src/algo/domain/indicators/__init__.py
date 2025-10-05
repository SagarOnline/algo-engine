"""
Indicators package - automatically discovers and imports all indicator modules.
"""
import os
import importlib
from pathlib import Path

# Get the directory containing this __init__.py file
indicators_dir = Path(__file__).parent

# Import all Python files in this directory (except __init__.py and registry.py)
for file_path in indicators_dir.glob("*.py"):
    if file_path.name not in ["__init__.py", "registry.py"] and not file_path.name.startswith("_"):
        module_name = file_path.stem
        try:
            importlib.import_module(f".{module_name}", package=__name__)
        except ImportError as e:
            print(f"Warning: Could not import indicator module {module_name}: {e}")

# Import registry functions for convenience
from .registry import get_indicator, list_indicators, IndicatorRegistry

