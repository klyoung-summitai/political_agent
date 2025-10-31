"""Base agent implementation with improved OOP design."""

from abc import ABC, abstractmethod
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from app.domain.agents.interfaces.agent_interface import IPoliticalAgent
from app.domain.agents.responses.sub_agent_response import SubAgentResponse


class LLMConfig:
    """Configuration for LLM initialization."""
    
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        max_tokens: int = 200,
        temperature: float = 0.7,
        **kwargs
    ):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.extra_params = kwargs
    
    def create_llm(self) -> ChatOpenAI:
        """Create LLM instance from config."""
        return ChatOpenAI(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            **self.extra_params
        )


class BaseAgent(IPoliticalAgent[SubAgentResponse], ABC):
    """Base implementation for political agents."""
    
    def __init__(
        self,
        name: str,
        party: str,
        system_prompt: Optional[str] = None,
        llm_config: Optional[LLMConfig] = None
    ):
        """
        Initialize base agent.
        
        Args:
            name: Agent's unique identifier
            party: Political party this agent represents
            system_prompt: Custom system prompt (uses default if None)
            llm_config: LLM configuration (uses default if None)
            
        Raises:
            ValueError: If name or party is empty
        """
        if not name:
            raise ValueError("Agent must have a name.")
        if not party:
            raise ValueError("Agent must have a party affiliation.")
        
        self._name = name
        self._party = party
        self._system_prompt = system_prompt or self.get_system_prompt()
        self._llm_config = llm_config or self._default_llm_config()
        self._llm = self._llm_config.create_llm()
    
    @property
    def name(self) -> str:
        """Get agent's name."""
        return self._name
    
    @property
    def party(self) -> str:
        """Get agent's political party."""
        return self._party
    
    def _default_llm_config(self) -> LLMConfig:
        """Get default LLM configuration."""
        return LLMConfig(model_name="gpt-4o-mini", max_tokens=200)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines this agent's perspective.
        
        Returns:
            System prompt string
        """
        pass
    
    @abstractmethod
    def construct_query(self, user_query: str) -> str:
        """
        Transform user query into agent-specific format.
        
        Args:
            user_query: Original user question
            
        Returns:
            Formatted query for this agent
        """
        pass
    
    def execute(self, query: str) -> SubAgentResponse:
        """
        Execute the agent's analysis on the given query.
        
        Args:
            query: The political question to analyze
            
        Returns:
            Structured response from the agent
        """
        messages = [
            SystemMessage(content=self._system_prompt),
            HumanMessage(content=self.construct_query(query))
        ]
        
        raw_response = self._llm.invoke(messages)
        response = SubAgentResponse(
            party=self.party,
            content=raw_response.content
        )
        
        if not self.validate_response(response):
            raise ValueError(f"Agent {self.name} produced invalid response")
        
        return response
    
    def validate_response(self, response: SubAgentResponse) -> bool:
        """
        Validate that the response meets quality standards.
        
        Args:
            response: The response to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation: check that content is not empty
        return bool(response.content and len(response.content.strip()) > 0)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', party='{self.party}')"


# Backward compatibility alias
class BasePoliticalAgent(BaseAgent):
    """Alias for backward compatibility."""
    pass