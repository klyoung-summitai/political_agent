"""Factory for creating and managing political agents."""

from typing import Dict, Type, Optional
from app.domain.agents.interfaces.agent_interface import IPoliticalAgent
from app.domain.agents.responses.sub_agent_response import SubAgentResponse


class AgentRegistry:
    """Registry for managing available agent types."""
    
    def __init__(self):
        self._agents: Dict[str, Type[IPoliticalAgent]] = {}
    
    def register(self, name: str, agent_class: Type[IPoliticalAgent]) -> None:
        """
        Register an agent class.
        
        Args:
            name: Unique identifier for the agent
            agent_class: The agent class to register
        """
        self._agents[name.lower()] = agent_class
    
    def get(self, name: str) -> Optional[Type[IPoliticalAgent]]:
        """
        Get an agent class by name.
        
        Args:
            name: Agent identifier
            
        Returns:
            Agent class or None if not found
        """
        return self._agents.get(name.lower())
    
    def list_available(self) -> list[str]:
        """Get list of all registered agent names."""
        return list(self._agents.keys())
    
    def exists(self, name: str) -> bool:
        """Check if an agent is registered."""
        return name.lower() in self._agents


class AgentFactory:
    """Factory for creating political agent instances."""
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        """
        Initialize factory with optional registry.
        
        Args:
            registry: Agent registry to use. Creates new one if None.
        """
        self._registry = registry or AgentRegistry()
        self._instances: Dict[str, IPoliticalAgent] = {}  # Singleton cache
    
    @property
    def registry(self) -> AgentRegistry:
        """Get the agent registry."""
        return self._registry
    
    def create(self, name: str, **kwargs) -> IPoliticalAgent[SubAgentResponse]:
        """
        Create an agent instance.
        
        Args:
            name: Agent identifier
            **kwargs: Additional arguments for agent initialization
            
        Returns:
            Agent instance
            
        Raises:
            ValueError: If agent not found in registry
        """
        agent_class = self._registry.get(name)
        if not agent_class:
            raise ValueError(
                f"Agent '{name}' not found. Available agents: {self._registry.list_available()}"
            )
        
        return agent_class(**kwargs)
    
    def get_or_create(self, name: str, **kwargs) -> IPoliticalAgent[SubAgentResponse]:
        """
        Get existing instance or create new one (singleton pattern).
        
        Args:
            name: Agent identifier
            **kwargs: Additional arguments for agent initialization
            
        Returns:
            Agent instance
        """
        key = name.lower()
        if key not in self._instances:
            self._instances[key] = self.create(name, **kwargs)
        return self._instances[key]
    
    def create_batch(self, names: list[str]) -> Dict[str, IPoliticalAgent[SubAgentResponse]]:
        """
        Create multiple agents at once.
        
        Args:
            names: List of agent identifiers
            
        Returns:
            Dictionary mapping agent names to instances
        """
        return {name: self.get_or_create(name) for name in names}
    
    def clear_cache(self) -> None:
        """Clear the singleton instance cache."""
        self._instances.clear()


# Global registry instance
_global_registry = AgentRegistry()


def get_global_registry() -> AgentRegistry:
    """Get the global agent registry."""
    return _global_registry


def register_agent(name: str, agent_class: Type[IPoliticalAgent]) -> None:
    """
    Register an agent in the global registry.
    
    Args:
        name: Agent identifier
        agent_class: Agent class to register
    """
    _global_registry.register(name, agent_class)
