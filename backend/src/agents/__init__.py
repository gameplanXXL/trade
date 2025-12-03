"""Agent module for trading platform."""

from src.agents.analyst import LLMSignalAnalyst, LLMSignalResponse, SignalAction
from src.agents.base import AgentDecision, AgentStatus, BaseAgent
from src.agents.crash_detector import CrashDetector
from src.agents.factory import (
    AGENT_REGISTRY,
    create_agent,
    get_available_agents,
    register_agent,
)
from src.agents.risk_manager import RejectionReason, RiskDecision, RiskManager
from src.agents.trader import Order, OrderSide, PositionSizing, Trader, TraderMode

__all__ = [
    "AGENT_REGISTRY",
    "AgentDecision",
    "AgentStatus",
    "BaseAgent",
    "CrashDetector",
    "LLMSignalAnalyst",
    "LLMSignalResponse",
    "Order",
    "OrderSide",
    "PositionSizing",
    "RejectionReason",
    "RiskDecision",
    "RiskManager",
    "SignalAction",
    "Trader",
    "TraderMode",
    "create_agent",
    "get_available_agents",
    "register_agent",
]
