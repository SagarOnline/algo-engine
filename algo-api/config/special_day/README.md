# Special Day Configuration

This directory contains exchange and year-specific special day configurations for the algorithmic trading system.

## Directory Structure

```
config/special_day/
├── nse_2023.json      # NSE holidays and special trading days for 2023
├── nse_2024.json      # NSE holidays and special trading days for 2024
├── nse_2025.json      # NSE holidays and special trading days for 2025
├── bse_2025.json      # BSE holidays and special trading days for 2025
└── README.md          # This file
```

## File Naming Convention

Files should be named using the following pattern:
```
{exchange}_{year}.json
```

Where:
- `exchange`: Lowercase exchange identifier (e.g., `nse`, `bse`, `nasdaq`, `nyse`)
- `year`: 4-digit year (e.g., `2023`, `2024`, `2025`)

Examples:
- `nse_2025.json` - NSE special days for 2025
- `bse_2024.json` - BSE special days for 2024
- `nasdaq_2025.json` - NASDAQ special days for 2025

## JSON File Format

Each JSON file should contain an array of special day objects with the following structure:

```json
[
    {
        "date": "2025-01-01",
        "day_type": "HOLIDAY",
        "description": "New Year's Day",
        "metadata": {
            "category": "national",
            "recurring": true
        }
    },
    {
        "date": "2025-12-24",
        "day_type": "SPECIAL_TRADING_DAY",
        "description": "Christmas Eve - Early Close",
        "trading_start": "09:15:00",
        "trading_end": "13:00:00",
        "metadata": {
            "early_close": true,
            "reason": "Christmas Eve"
        }
    }
]
```

### Field Descriptions

#### Required Fields
- **date**: Date in ISO format (YYYY-MM-DD)
- **day_type**: Either "HOLIDAY" or "SPECIAL_TRADING_DAY"
- **description**: Human-readable description of the special day

#### Optional Fields
- **trading_start**: Trading start time for special trading days (HH:MM:SS format)
- **trading_end**: Trading end time for special trading days (HH:MM:SS format)
- **metadata**: Additional key-value pairs for categorization and filtering

### Day Types

1. **HOLIDAY**: Market is completely closed
   - Cannot have `trading_start` or `trading_end` fields
   - Represents days when no trading occurs

2. **SPECIAL_TRADING_DAY**: Market operates with modified hours
   - Must have both `trading_start` and `trading_end` fields (or neither)
   - Represents days with early close, late open, or other schedule modifications

### Metadata Categories

Common metadata fields include:

- **category**: Type of holiday (e.g., "national", "religious", "state")
- **recurring**: Whether the holiday occurs annually on the same date
- **country/region**: Geographic scope of the holiday
- **early_close**: Boolean indicating if it's an early close day
- **reason**: Explanation for the special trading schedule
- **exchange_specific**: Exchange-specific notes or policies

## Usage Examples

### Loading Special Days

```python
from algo.domain.strategy import JsonSpecialDayRepository
from datetime import date

# Initialize repository with config directory
repo = JsonSpecialDayRepository("config/special_day", exchange="nse")

# Get all special days for NSE 2025
nse_2025_days = repo.get_special_days_for_year(2025, "nse")

# Get only holidays for BSE 2025
bse_holidays = repo.get_holidays(2025, "bse")

# Check if a specific date is a holiday
is_holiday = repo.is_holiday(date(2025, 1, 1), "nse")

# Get custom trading hours for a special trading day
trading_hours = repo.get_trading_hours(date(2025, 12, 24), "nse")
```

### Multi-Exchange Support

The system supports multiple exchanges simultaneously:

```python
# Check the same date across different exchanges
test_date = date(2025, 12, 25)

nse_special = repo.get_special_day(test_date, "nse")
bse_special = repo.get_special_day(test_date, "bse")

# Different exchanges may have different holiday schedules
```

## Adding New Exchanges

To add support for a new exchange:

1. Create JSON files for each year following the naming convention
2. Populate with exchange-specific holidays and special trading days
3. The repository will automatically detect and load the new files

Example for adding NASDAQ support:
```
config/special_day/
├── nasdaq_2024.json
├── nasdaq_2025.json
└── ...
```

## Data Sources

Special day data should be sourced from official exchange calendars:

- **NSE**: [NSE Holiday Calendar](https://www.nseindia.com/regulations/holiday-calendar)
- **BSE**: [BSE Trading Calendar](https://www.bseindia.com/markets/market_info/trading_holiday.html)
- **NASDAQ**: [NASDAQ Trading Calendar](https://www.nasdaq.com/market-activity/trading-calendar)
- **NYSE**: [NYSE Trading Calendar](https://www.nyse.com/markets/hours-calendars)

## Validation

The system validates:
- File naming conventions
- JSON structure and required fields
- Date formats and consistency
- Trading hours for special trading days
- Logical constraints (holidays cannot have trading hours)

## Performance

- Files are loaded on-demand and cached in memory
- File modification timestamps are monitored for automatic cache refresh
- Large datasets are efficiently organized by exchange and year
- O(1) lookup time for date-specific queries after initial load

## Backup and Versioning

- Keep historical special day data for backtesting purposes
- Version control all configuration files
- Regular backups of the config directory are recommended
- Consider maintaining separate configs for different environments (dev, test, prod)
