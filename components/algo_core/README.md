# Algo Core

The **Algo Core** component is the central engine for **algorithmic trading**.  
It provides functionality for both **backtesting** strategies using historical data and **executing live trades** through broker integrations.

---

## 📌 Overview

- **Backtesting**  
  Uses the historical market data provided by the [`historical-data`](../historical_data/README.md) component to simulate strategies, analyze performance, and optimize trading rules.

- **Live Trading**  
  Connects to brokers such as **Upstox** and **Zerodha** to:
  - Fetch real-time instrument price feeds.
  - Execute buy/sell orders based on strategy signals.
  - Manage positions and monitor PnL.

- **Strategy Integration**  
  Allows you to define trading strategies that can run in either backtest mode or live execution mode.

---

## ⚙️ Features

- Core engine for running strategies in **backtest** or **live** mode.
- Integration with multiple brokers (currently supports **Upstox** and **Zerodha**).
- Modular architecture to allow easy extension for new brokers.
- Unified interface for strategy developers (write once, run in both backtest and live).
- Logging and error handling for trade execution and data feeds.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+  
- [`historical-data`](../historical_data/README.md) component set up for backtesting.  
- Broker account (Upstox / Zerodha) with API credentials for live trading.

### Installation

Navigate to the algo-core project directory:  

```bash
cd components/algo-core
```

Create Vitual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

Create Environment File (for developement)
```bash
python - <<EOF
 A_DIRECTORY=../../data
BACKTEST_REPORT_DIRECTORY=../../report
STRATEGIES_CONFIG_DIRECTORY=../../strategies
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

Run tests

```bash
python -m pytest
```

Run Test Strategy

```bash
python .\src\algo_core\main.py
```
