"""Agent interface defining the contract for all political agents."""

from abc import ABC, abstractmethod
from typing import TypeVar, Generic
from pydantic import BaseModel

# Generic type for agent responses
TResponse = TypeVar('TResponse', bound=BaseModel)


class IAgent(ABC, Generic[TResponse]):
    """Interface for all political agents."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Agent's unique identifier."""
        pass
    
    @property
    @abstractmethod
    def party(self) -> str:
        """Political party this agent represents."""
        pass
    
    @abstractmethod
    def execute(self, query: str) -> TResponse:
        """
        Execute the agent's analysis on the given query.
        
        Args:
            query: The political question to analyze
            
        Returns:
            Structured response from the agent
        """
        pass
    
    @abstractmethod
    def validate_response(self, response: TResponse) -> bool:
        """
        Validate that the response meets quality standards.
        
        Args:
            response: The response to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass


class IPoliticalAgent(IAgent[TResponse]):
    """Extended interface for political agents with party affiliation."""
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt that defines this agent's perspective."""
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


class IMediatorAgent(IAgent[TResponse]):
    """Interface for mediator agents that synthesize multiple responses."""
    
    @abstractmethod
    def select_agents(self, query: str) -> list[str]:
        """
        Determine which agents should respond to the query.
        
        Args:
            query: User's question
            
        Returns:
            List of agent names to invoke
        """
        pass
    
    @abstractmethod
    def synthesize(self, query: str, responses: list[TResponse]) -> TResponse:
        """
        Synthesize multiple agent responses into a unified response.
        
        Args:
            query: Original user question
            responses: List of agent responses
            
        Returns:
            Synthesized response
        """
        pass
