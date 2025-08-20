import json
import os
from typing import Dict, Any
from datetime import date

from algo_core.domain.backtest.report_repository import BacktestReportRepository
from algo_core.domain.backtest.report import BacktestReport


class JsonBacktestReportRepository(BacktestReportRepository):
    def __init__(self, report_directory: str = "report"):
        self.report_directory = os.getenv("REPORT_DIRECTORY", report_directory)

    def save(self, report: BacktestReport) -> None:
        os.makedirs(self.report_directory, exist_ok=True)
        # The report object does not have start and end dates.
        # This is a temporary solution.
        # TODO: Add start and end dates to the report object.
        report_filename = f"{report.strategy_name}_report.json"
        report_filepath = os.path.join(self.report_directory, report_filename)

        with open(report_filepath, "w") as f:
            json.dump(report.to_dict(), f, indent=4, default=str)
            print(f"Report saved to {report_filepath}")
