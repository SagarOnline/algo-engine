# Gemini Code Context

This document provides context for the Gemini CLI to understand the project.

## Project Overview

This project is a Python-based algorithmic trading engine. It is designed to backtest trading strategies against historical market data and deploy the strategies in live market. The engine will also expose the REST apis to interact with it.

The project is structured as follows:

- **`main.py`**: The entry point of the application.
- **`domain`**: Contains the core business logic of the application.
- **`infrastructure`**: Contains the implementation details of how the domain logic is persisted and executed.
- **`tests`**: Contains the tests for the project.

## How it Works

The core of the engine is built around the `Strategy` abstract base class. This class defines the interface for all trading strategies. The engine supports strategies defined in JSON files. The `JsonStrategy` class parses these JSON files and creates a `Strategy` object.


## Components of Engine

### Strategy
This component deals with defining the strategy and which can allow defining the strategy based on technical indicators ,price, date, etc. 

### Backtesting Engine
The Engine allows backtesting the strategy on historical data. The engine also generates the peroformance report of the strategy. 

### Execution Engine
The Execution Engine allows executing the strategy on live data in live market. 

### REST Interface
The Engine also exposes the REST interface for interacting with Algo Engine
