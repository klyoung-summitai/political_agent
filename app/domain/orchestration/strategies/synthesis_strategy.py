"""Strategy pattern for response synthesis."""

from abc import ABC, abstractmethod
from typing import List
from app.domain.agents.responses.sub_agent_response import SubAgentResponse
from app.domain.agents.responses.mediator_response import MediatorResponse


class ISynthesisStrategy(ABC):
    """Interface for synthesis strategies."""
    
    @abstractmethod
    def synthesize(
        self,
        query: str,
        responses: List[SubAgentResponse]
    ) -> MediatorResponse:
        """
        Synthesize multiple agent responses into a unified response.
        
        Args:
            query: Original user question
            responses: List of agent responses to synthesize
            
        Returns:
            Synthesized mediator response
            
        Raises:
            ValueError: If responses are invalid or synthesis fails
        """
        pass
    
    @abstractmethod
    def validate_inputs(self, responses: List[SubAgentResponse]) -> bool:
        """
        Validate that input responses are suitable for synthesis.
        
        Args:
            responses: List of responses to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass


class BaseSynthesisStrategy(ISynthesisStrategy):
    """Base implementation with common validation logic."""
    
    def validate_inputs(self, responses: List[SubAgentResponse]) -> bool:
        """
        Default validation: check that responses exist and have content.
        
        Args:
            responses: List of responses to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not responses:
            return False
        
        for response in responses:
            if not response.content or not response.content.strip():
                return False
            if not response.party:
                return False
        
        return True
    
    def _extract_parties(self, responses: List[SubAgentResponse]) -> List[str]:
        """
        Extract party names from responses.
        
        Args:
            responses: List of agent responses
            
        Returns:
            List of unique party names
        """
        return list(set(resp.party for resp in responses if resp.party))
    
    def _format_responses_text(self, responses: List[SubAgentResponse]) -> str:
        """
        Format responses into text for synthesis.
        
        Args:
            responses: List of agent responses
            
        Returns:
            Formatted text string
        """
        return "\n\n".join(
            f"{resp.party}: {resp.content}" for resp in responses
        )
