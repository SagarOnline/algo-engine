# Service Registry Usage Guide

This document explains how to use the service registry for dependency injection in the algo trading application.

## Overview

The service registry provides a centralized way to manage singleton services throughout the application. It ensures that services are properly initialized and can be accessed from anywhere in the codebase.

## Configuration

Services are configured through the main application configuration file `config/config.json`. The configuration includes settings for various service components:

### Trading Window Configuration
```json
{
  "trading_window_config": {
    "config_dir": "./config/trading_window/"
  }
}
```

### Special Day Configuration
```json
{
  "special_day_config": {
    "config_dir": "./config/special_day/"
  }
}
```

### Full Configuration Example
```json
{
  "backtest_engine": {
    "historical_data_backend": "PARQUET_FILES",
    "reports_dir": "./reports",
    "parquet_files_base_dir": "./historical-data",
    "strategy_json_config_dir": "./strategies"
  },
  "broker_api": {
    "upstox": {
      "redirect_url": "http://localhost:5000/auth/callback"
    }
  },
  "special_day_config": {
    "config_dir": "./config/special_day/"
  },
  "trading_window_config": {
    "config_dir": "./config/trading_window/"
  }
}
```

## Key Components

### 1. ServiceRegistry (`infrastructure/service_registry.py`)
- Thread-safe singleton registry
- Manages service instances and factories
- Provides registration and retrieval methods

### 2. Service Configuration (`infrastructure/service_configuration.py`)
- Handles registration of all application services
- Called during app startup to initialize services
- Contains factory functions for service creation

### 3. Service Accessors (`infrastructure/services.py`)
- Convenient functions to access specific services
- Type-safe service retrieval
- Reduces boilerplate code

## Usage Examples

### Registering a Service

#### Option 1: Using Factory Function
```python
from algo.infrastructure.service_registry import register_service_factory

def create_my_service():
    return MyService(config="value")

register_service_factory(MyService, create_my_service)
```

#### Option 2: Using Direct Instance
```python
from algo.infrastructure.service_registry import service_registry

instance = MyService(config="value")
service_registry.register_instance(MyService, instance)
```

### Accessing Services

#### Using Service Accessor (Recommended)
```python
from algo.infrastructure.services import get_trading_window_service

def my_function():
    trading_service = get_trading_window_service()
    window = trading_service.get_trading_window(date.today(), "NSE", "EQ")
    return window
```

#### Using Registry Directly
```python
from algo.infrastructure.service_registry import get_service
from algo.domain.trading.trading_window_service import TradingWindowService

def my_function():
    trading_service = get_service(TradingWindowService)
    window = trading_service.get_trading_window(date.today(), "NSE", "EQ")
    return window
```

### Using in Controllers

```python
from flask import Blueprint, jsonify
from algo.infrastructure.services import get_trading_window_service

my_bp = Blueprint('my_controller', __name__)

@my_bp.route('/trading-status')
def get_trading_status():
    service = get_trading_window_service()
    # Use service here
    return jsonify({"status": "ok"})
```

## Available Services

### TradingWindowService
- **Purpose**: Manages trading windows, holidays, and special trading days
- **Accessor**: `get_trading_window_service()`
- **Configuration**: Loads from `config/trading_window/*.json`

## API Endpoints

The service registry provides several API endpoints for monitoring:

### Service Status
- **GET** `/services/status` - Get overall service registry status
- **GET** `/api/trading-window/status` - Get TradingWindowService specific status

### Trading Window APIs
- **GET** `/api/trading-window/window/<exchange>/<segment>?date=YYYY-MM-DD`
- **GET** `/api/trading-window/holidays/<exchange>/<segment>/<year>`
- **GET** `/api/trading-window/special-days/<exchange>/<segment>/<year>`
- **GET** `/api/trading-window/exchanges-segments`

## Adding New Services

### Step 1: Create the Service
```python
class MyNewService:
    def __init__(self, config_value: str):
        self.config_value = config_value
    
    def do_something(self) -> str:
        return f"Doing something with {self.config_value}"
```

### Step 2: Add Factory Function
In `infrastructure/service_configuration.py`:
```python
def _create_my_new_service() -> MyNewService:
    # Load configuration as needed
    config_value = "loaded_from_config"
    return MyNewService(config_value)
```

### Step 3: Register in `register_all_services()`
```python
def register_all_services() -> None:
    # ... existing registrations ...
    register_service_factory(MyNewService, _create_my_new_service)
    logger.info("Registered MyNewService factory")
```

### Step 4: Add Service Accessor
In `infrastructure/services.py`:
```python
def get_my_new_service() -> MyNewService:
    return get_service(MyNewService)
```

### Step 5: Use in Application
```python
from algo.infrastructure.services import get_my_new_service

def some_function():
    service = get_my_new_service()
    result = service.do_something()
    return result
```

## Testing with Service Registry

### Setup Test Environment
```python
import pytest
from algo.infrastructure.service_registry import service_registry

class TestMyClass:
    def setup_method(self):
        service_registry.clear_all()  # Clear for isolated tests
    
    def test_with_mock_service(self):
        # Register mock service for testing
        mock_service = MagicMock()
        service_registry.register_instance(MyService, mock_service)
        
        # Test code that uses the service
        result = my_function_that_uses_service()
        assert result == expected_value
```

## Best Practices

1. **Use Service Accessors**: Always use the accessor functions in `services.py` rather than calling the registry directly.

2. **Register on Startup**: All services should be registered in `register_all_services()` which is called from `app.py`.

3. **Lazy Initialization**: Services are created only when first accessed, improving startup time.

4. **Thread Safety**: The registry is thread-safe, so services can be accessed from multiple threads.

5. **Testing**: Always clear the registry in test setup to ensure isolated tests.

6. **Error Handling**: Handle `ValueError` when accessing services that might not be registered.

## Configuration

Services are configured through factory functions that can:
- Load configuration from files
- Read environment variables
- Initialize with default values
- Perform dependency resolution

The TradingWindowService example shows how to load configuration from JSON files in the factory function.
