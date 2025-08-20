# Historical Data Component

The **historical-data** component is part of the **Algo Engine** project. It is responsible for fetching, managing, and storing historical market data for various instruments. This data is a critical dependency for the **algo-core** component, which uses it to perform **backtesting** and validate algorithmic trading strategies before live execution.  

---

## Features
- Fetches historical data for different instruments and timeframes.  
- Stores data in **Parquet files** for efficient querying and compression.  
- Organizes data in a structured directory hierarchy:  

  ```
  {market}/{timeframe}/{instrument}/{year}/{month}/{date}.parquet
  ```

- Easily extendable to support future storage backends like **time-series databases** (e.g., InfluxDB, TimescaleDB).  
- Ensures consistent and reusable data access for the **algo-core** backtesting engine.  

---

## Getting Started

### Prerequisites
- Python 3.9+  
- [pip](https://pip.pypa.io/en/stable/)  
- Virtual environment (recommended)  

### Installation
Navigate to the historical-data project directory:  

```bash
cd components/historical-data
```

Create Vitual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

Create Environment File (for developement)
```bash
python - <<EOF
content = """UPSTOX_TOKEN=<your-upstox-token>
HISTORICAL_DATA_DIRECTORY=..\..\data
"""
with open(".env", "w") as f:
    f.write(content)
EOF

```

Install dependencies ( for production ):  

```bash
python -m pip install -e .   
```

Install dependencies ( for development ):  

```bash
python -m pip install -e .[dev]   
```

Run application to fetch historical data

```bash
python src/algo-core/main.py
```

---


### Environment Variables
Set the base directory where historical data should be stored:  

```bash
export HISTORICAL_DATA_DIRECTORY=/path/to/data
```

---

## Relationship with Other Components

- **algo-core**:  
  The `algo-core` component depends on this historical data for **backtesting trading strategies**.  
  - Without valid historical data, backtests cannot be executed.  
  - The `algo-core` engine directly reads data produced by the **historical-data** component.  


