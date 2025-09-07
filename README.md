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

## 🚀 Components

- [Algo UI Component](./algo-ui/README.md) : A cross-platform Flutter dashboard for visualizing strategy performance, managing trades, and interacting with the Algo Engine API.
- [Algo API Component](./algo-api/README.md) : It provides REST interface for both **backtesting** strategies using historical data and **executing live trades** through broker integrations.
- [Historical Data Component](./components/historical_data/README.md) : It is responsible for fetching, managing, and storing historical market data for various instruments. This data is a critical dependency for the **algo-core** component, which uses it to perform **backtesting** and validate algorithmic trading strategies before live execution.  


---
## ⚙️ Getting Started

### 1. Clone the Repository
```bash
git clone git@github.com:SagarOnline/algo-engine.git
```

### 3. Navigate to Components
Refer to the README.md file of that component for installation and setup details.
