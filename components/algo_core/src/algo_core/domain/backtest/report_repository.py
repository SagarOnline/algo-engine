from abc import ABC, abstractmethod
from algo_core.domain.backtest.report import BackTestReport


class BacktestReportRepository(ABC):

    @abstractmethod
    def save(self, report: BackTestReport) -> None:
        pass
