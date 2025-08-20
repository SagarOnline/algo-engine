# 🧠 Algo Engine

An extensible and testable **algorithmic trading engine** designed to **run and backtest trading strategies** defined in JSON format. The platform is built to support real-time execution and historical backtesting using the same core engine, enabling seamless transition from testing to live deployment.

---

## 🚀 Features

- Define trading strategies in JSON
- Run strategies on live data or historical data (backtesting)
- Shared engine logic for backtest and live trading
- Modular and maintainable project structure
- Unit test coverage for core components

---

## ⚙️ Getting Started

### 1. Clone the Repository
```bash
git clone git@github.com:SagarOnline/algo-engine.git
cd algo-engine
```

### 3. Create Vitual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

### 2. Create Environment File
```bash
python - <<EOF
content = """HISTORICAL_DATA_DIRECTORY=<historical-data-directory-path-on-local-machine>
BACKTEST_REPORT_DIRECTORY=<-report-direcotry-path-on-local-machine>
"""
with open(".env", "w") as f:
    f.write(content)
EOF

```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```


### 4. Running Unit Tests
```bash
python -m pytest
```

### 4. Running The Application
```bash
python main.py
```


