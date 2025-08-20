import json
from typing import Dict, Any
from algo_core.domain.strategy import Instrument, Position, Strategy
from algo_core.domain.strategy import RuleSet,Condition,Expression
from algo_core.domain.timeframe import Timeframe


class JsonStrategy(Strategy):
    def __init__(self, json_data: Dict[str, Any]):
        self.strategy_name = json_data.get("strategy_name")
        self.timeframe = Timeframe(json_data.get("timeframe"))
        self.capital = json_data.get("capital")
        self.instrument = self._get_parsed_instrument(json_data.get("instrument", {}))
        # Parse Position
        self._parse_position(json_data)

        self.entry_rules = self._parse_rules(json_data.get("entry_rules", {}))
        self.exit_rules = self._parse_rules(json_data.get("exit_rules", {}))

    def _parse_position(self, json_data):
        position_data = json_data.get("position", {})
        instrument = self._get_parsed_instrument(position_data.get("instrument", {})) 
        self.position = Position(
            action=position_data.get("action"),
            instrument=instrument
        )

    def _get_parsed_instrument(self, instrument_data: Dict[str, Any]) -> Instrument:
        instrument = Instrument(
            type=instrument_data.get("type"),
            exchange=instrument_data.get("exchange"),
            expiry=instrument_data.get("expiry"),
            expiring=instrument_data.get("expiring"),
            atm=instrument_data.get("atm"),
            instrument_key=instrument_data.get("instrument_key"),
        )
        return instrument

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

    

    def get_timeframe(self) -> Timeframe:
        return self.timeframe

    def get_capital(self) -> int:
        return self.capital

    def get_entry_rules(self) -> RuleSet:
        return self.entry_rules

    def get_exit_rules(self) -> RuleSet:
        return self.exit_rules
    
    def get_position(self) -> Position:
        return self.position
    
    def get_instrument(self) -> Instrument:
        return self.instrument
