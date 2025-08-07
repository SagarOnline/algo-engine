import json
from typing import Dict, Any
from domain.strategy import Strategy
from domain.strategy import RuleSet,Condition,Expression


class JsonStrategy(Strategy):
    def __init__(self, json_data: Dict[str, Any]):
        self.strategy_name = json_data.get("strategy_name")
        self.symbol = json_data.get("symbol")
        self.exchange = json_data.get("exchange")
        self.timeframe = json_data.get("timeframe")
        self.capital = json_data.get("capital")

        self.entry_rules = self._parse_rules(json_data.get("entry_rules", {}))
        self.exit_rules = self._parse_rules(json_data.get("exit_rules", {}))

    def _parse_expression(self, expr_data: Dict[str, Any]) -> Expression:
        expr_type = expr_data.get("type")
        params = expr_data.get("params", {})
        return Expression(expr_type, params)

    def _parse_condition(self, cond_data: Dict[str, Any]) -> Condition:
        operator = cond_data.get("operator")
        left = self._parse_expression(cond_data.get("left"))
        right = self._parse_expression(cond_data.get("right"))
        return Condition(operator, left, right)

    def _parse_rules(self, rules_data: Dict[str, Any]) -> RuleSet:
        logic = rules_data.get("logic", "AND")
        condition_list = rules_data.get("conditions", [])
        conditions = [self._parse_condition(cond) for cond in condition_list]
        return RuleSet(logic, conditions)

    def get_name(self) -> str:
        return self.strategy_name

    def get_symbol(self) -> str:
        return self.symbol

    def get_exchange(self) -> str:
        return self.exchange

    def get_timeframe(self) -> str:
        return self.timeframe

    def get_capital(self) -> int:
        return self.capital

    def get_entry_rules(self) -> RuleSet:
        return self.entry_rules

    def get_exit_rules(self) -> RuleSet:
        return self.exit_rules
