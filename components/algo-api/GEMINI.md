# Gemini Code Context

This document provides context for the Gemini CLI to understand the project.

## Project Overview

This project is a Python-based algorithmic trading engine. It is designed to backtest trading strategies against historical market data and deploy the strategies in live market. The engine will also expose the REST apis to interact with it.

The project is structured as follows:

- **`main.py`**: The entry point of the application.
- **`domain`**: Contains the core business logic of the application.
- **`infrastructure`**: Contains the implementation details of how the domain logic is persisted and executed. It also contains the API implementation logic such as REST APIs
- **`application`**: Contains the use case implementation logic of the application. 
- **`tests`**: Contains the tests for the project.

## How it Works

The core of the engine is built around the `Strategy` abstract base class. This class defines the interface for all trading strategies. The engine supports strategies defined in JSON files. The `JsonStrategy` class parses these JSON files and creates a `Strategy` object. The `BackTestEngine` is the core backtest engine which uses `BackTest` to run the backtest and return `BackTestReport`. `HistoricalDataRepository` is responsible for fetching the Historical Data required for runnning the BackTest. `BackTestEngine` can either work on the historical data stored in parquet files locally or can fetch the data by calling broker API such as Upstox.


## Components of Engine

### Strategy
This component deals with defining the strategy and which can allow defining the strategy based on technical indicators ,price, date, etc. 

### Backtesting Engine
The Engine allows backtesting the strategy on historical data. The engine also generates the peroformance report of the strategy. Currently the backtesting engine reads the historical data from parquet files,however in future, it will be updated to get historical data from timeseries database.  For the Parquet implementation, files are read from the directory specified by the HISTORICAL_DATA_DIRECTORY environment variable. The directory structure follows the format {timeframe}/{instrument_key}/{year}/{month}, and files are named as yyyy-mm-dd.parquet. 

### Execution Engine
The Execution Engine allows executing the strategy on live data in live market. 

### REST Interface
The Engine also exposes the REST interface for interacting with Algo Engine

## Instructions
Please do not use emojies in code.
