"""Liberal political agent implementation."""

from app.domain.agents.entities.agent import BaseAgent


class LiberalAgent(BaseAgent):
    """Agent representing liberal/progressive political perspectives."""
    
    def __init__(self):
        super().__init__(
            name="Liberal",
            party="Liberal"
        )
    
    def get_system_prompt(self) -> str:
        """Get liberal perspective system prompt."""
        return """
            You are a Liberal political analyst. Your task is to provide factual, informed, and balanced perspectives from a progressive or liberal viewpoint.
            - Focus on policies, social issues, and historical context from a liberal perspective.
            - Provide reasoning and evidence for positions, without giving tailored political advice or influencing specific voters.
            - Avoid making recommendations or telling anyone what to think or do.
            - Be clear, structured, and explain the rationale behind your perspective.
        """
    
    def construct_query(self, user_query: str) -> str:
        """Pass through user query without modification."""
        return user_query

