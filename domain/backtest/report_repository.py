from abc import ABC, abstractmethod
from domain.backtest.report import BacktestReport


class BacktestReportRepository(ABC):

    @abstractmethod
    def save(self, report: BacktestReport) -> None:
        pass
