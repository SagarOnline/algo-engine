# json_strategy.py

import json
from typing import Union, List, Optional
from domain.strategy import (
    Indicator, RuleGroup, Condition, RiskManagement,
    PositionSize, ActiveTimeWindow, Metadata
)
from domain.strategy import Strategy


class JsonStrategy(Strategy):
    def __init__(self, json_data: Union[str, dict]):
        if isinstance(json_data, str):
            self.raw = json.loads(json_data)
        else:
            self.raw = json_data

    def get_indicators(self) -> List[Indicator]:
        return [Indicator(**item) for item in self.raw.get("indicators", [])]

    def get_entry_rules(self) -> RuleGroup:
        return self._parse_rule_group(self.raw.get("entry_rules"))

    def get_exit_rules(self) -> RuleGroup:
        return self._parse_rule_group(self.raw.get("exit_rules"))

    def get_risk_management(self) -> RiskManagement:
        rm = self.raw["risk_management"]
        pos = PositionSize(**rm["position_size"])
        return RiskManagement(
            capital=rm["capital"],
            order_type=rm["order_type"],
            position_size=pos,
            stop_loss_percent=rm["stop_loss_percent"],
            take_profit_percent=rm["take_profit_percent"],
            trailing_stop_loss_percent=rm.get("trailing_stop_loss_percent")
        )

    def get_active_time_window(self) -> Optional[ActiveTimeWindow]:
        active_time = self.raw.get("active_time")
        if active_time:
            return ActiveTimeWindow(**active_time)
        return None

    def get_metadata(self) -> Metadata:
        return Metadata(**self.raw["metadata"])

    def _parse_rule_group(self, rule_data) -> RuleGroup:
        if "conditions" in rule_data:
            parsed_conditions = []
            for cond in rule_data["conditions"]:
                if "logic" in cond:
                    parsed_conditions.append(self._parse_rule_group(cond))
                else:
                    parsed_conditions.append(Condition(**cond))
            return RuleGroup(logic=rule_data["logic"], conditions=parsed_conditions)
        else:
            raise ValueError("Invalid rule format: missing 'conditions'")
