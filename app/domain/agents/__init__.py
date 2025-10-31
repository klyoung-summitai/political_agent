"""Agent module initialization and registration."""

from app.domain.agents.factories.agent_factory import register_agent, get_global_registry
from app.domain.agents.entities.conservative_agent import ConservativeAgent
from app.domain.agents.entities.liberal_agent import LiberalAgent
from app.domain.agents.entities.socialist_agent import SocialistAgent

# Register all available agents
register_agent("conservative", ConservativeAgent)
register_agent("liberal", LiberalAgent)
register_agent("socialist", SocialistAgent)

__all__ = [
    "ConservativeAgent",
    "LiberalAgent",
    "SocialistAgent",
    "register_agent",
    "get_global_registry",
]
