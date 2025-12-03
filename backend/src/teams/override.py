"""Override rule engine for conditional pipeline behavior - Story 003-02."""

import re
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import BaseModel, Field

from src.agents.base import AgentDecision, AgentStatus, BaseAgent
from src.core.exceptions import PipelineError
from src.teams.schemas import OverrideRule

log = structlog.get_logger()


class OverrideResult(BaseModel):
    """Result of override rule evaluation and execution."""

    rule_name: str = Field(..., description="Name of the triggered rule")
    triggered: bool = Field(..., description="Whether the rule was triggered")
    decision: AgentDecision | None = Field(
        default=None,
        description="Decision from the override action, if executed",
    )


class OverrideEngine:
    """Evaluates and executes override rules for pipeline control.

    Override rules allow critical situations to override normal
    pipeline execution by evaluating conditions and executing
    actions when conditions are met.
    """

    # Supported comparison operators
    OPERATORS = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">": lambda a, b: float(a) > float(b),
        "<": lambda a, b: float(a) < float(b),
        ">=": lambda a, b: float(a) >= float(b),
        "<=": lambda a, b: float(a) <= float(b),
    }

    def __init__(
        self, rules: list[OverrideRule], agents: dict[str, BaseAgent]
    ) -> None:
        """Initialize the override engine.

        Args:
            rules: List of override rules to evaluate.
            agents: Dictionary mapping role names to agent instances.
        """
        # Sort rules by priority (lower = higher priority)
        self.rules = sorted(rules, key=lambda r: r.priority)
        self.agents = agents

    def evaluate_condition(self, condition: str, context: dict[str, Any]) -> bool:
        """Evaluate a condition against the current context.

        Supports conditions like:
        - "crash_detector.status == CRASH"
        - "crash_detector.field_value > 50"
        - "context.drawdown > 0.1"

        Args:
            condition: Condition string to evaluate.
            context: Current pipeline context.

        Returns:
            True if condition is met, False otherwise.
        """
        try:
            # Parse condition: left_side operator right_side
            pattern = r"^(\w+)\.(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+)$"
            match = re.match(pattern, condition.strip())

            if not match:
                log.warning(
                    "override_condition_invalid_format",
                    condition=condition,
                )
                return False

            source, field, operator, value = match.groups()
            value = value.strip().strip("'\"")  # Remove quotes if present

            # Get the left-side value
            left_value: Any = None

            if source == "context":
                # Get value from context
                left_value = context.get(field)
            elif source in self.agents:
                # Get value from agent
                agent = self.agents[source]
                if field == "status":
                    left_value = agent.status.value
                elif hasattr(agent, field):
                    left_value = getattr(agent, field)
                else:
                    log.warning(
                        "override_condition_field_not_found",
                        agent=source,
                        field=field,
                    )
                    return False
            else:
                log.warning(
                    "override_condition_source_not_found",
                    source=source,
                    condition=condition,
                )
                return False

            if left_value is None:
                return False

            # Compare values
            op_func = self.OPERATORS.get(operator)
            if op_func is None:
                return False

            # Handle status comparisons
            if field == "status" and isinstance(left_value, str):
                # Convert value to status enum value for comparison
                try:
                    right_value = AgentStatus(value.lower()).value
                except ValueError:
                    right_value = value.lower()
                return op_func(left_value, right_value)

            # Handle boolean context values
            if isinstance(left_value, bool):
                if value.lower() == "true":
                    right_value = True
                elif value.lower() == "false":
                    right_value = False
                else:
                    right_value = value
                return op_func(left_value, right_value)

            # Handle numeric comparisons
            return op_func(left_value, value)

        except (ValueError, TypeError, AttributeError) as e:
            log.warning(
                "override_condition_evaluation_error",
                condition=condition,
                error=str(e),
            )
            return False

    async def execute_action(
        self, action: str, context: dict[str, Any]
    ) -> AgentDecision:
        """Execute an override action.

        Actions follow the format: agent.method() or agent.method(arg)

        Args:
            action: Action string to execute.
            context: Current pipeline context to pass to the action.

        Returns:
            AgentDecision from the executed action.

        Raises:
            PipelineError: If agent or method not found, or action format is invalid.
        """
        # Parse action: agent.method() or agent.method(arg)
        pattern = r"^(\w+)\.(\w+)\((.*)\)$"
        match = re.match(pattern, action.strip())

        if not match:
            raise PipelineError(
                f"Invalid action format: {action}",
                details={"action": action, "expected_format": "agent.method()"},
            )

        agent_name, method_name, _ = match.groups()

        # Validate agent exists
        if agent_name not in self.agents:
            raise PipelineError(
                f"Agent not found: {agent_name}",
                details={
                    "agent": agent_name,
                    "available_agents": list(self.agents.keys()),
                },
            )

        agent = self.agents[agent_name]

        # Validate method exists
        if not hasattr(agent, method_name):
            raise PipelineError(
                f"Method not found: {method_name}",
                details={
                    "agent": agent_name,
                    "method": method_name,
                    "available_methods": [
                        m for m in dir(agent) if not m.startswith("_")
                    ],
                },
            )

        method = getattr(agent, method_name)

        log.info(
            "override_action_executing",
            agent=agent_name,
            method=method_name,
            timestamp=datetime.now(UTC).isoformat(),
        )

        # Execute the action
        decision = await method(context)

        log.info(
            "override_action_completed",
            agent=agent_name,
            method=method_name,
            decision_type=decision.decision_type,
            timestamp=datetime.now(UTC).isoformat(),
        )

        return decision

    async def check_and_execute(
        self, context: dict[str, Any]
    ) -> OverrideResult | None:
        """Check all rules and execute the first matching one.

        Rules are checked in priority order (lower priority number = higher priority).
        Only the first matching rule is executed.

        Args:
            context: Current pipeline context.

        Returns:
            OverrideResult if a rule was triggered, None otherwise.
        """
        if not self.rules:
            return None

        log.debug(
            "override_check_starting",
            rule_count=len(self.rules),
            timestamp=datetime.now(UTC).isoformat(),
        )

        for rule in self.rules:
            if self.evaluate_condition(rule.condition, context):
                log.info(
                    "override_rule_triggered",
                    rule_name=rule.name,
                    condition=rule.condition,
                    priority=rule.priority,
                    timestamp=datetime.now(UTC).isoformat(),
                )

                decision = await self.execute_action(rule.action, context)

                log.info(
                    "override_rule_executed",
                    rule_name=rule.name,
                    action=rule.action,
                    decision_type=decision.decision_type,
                    timestamp=datetime.now(UTC).isoformat(),
                )

                return OverrideResult(
                    rule_name=rule.name,
                    triggered=True,
                    decision=decision,
                )

        log.debug(
            "override_check_completed",
            rules_checked=len(self.rules),
            triggered=False,
            timestamp=datetime.now(UTC).isoformat(),
        )

        return None
