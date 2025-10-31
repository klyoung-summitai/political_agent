"""Conservative political agent implementation."""

from app.domain.agents.entities.agent import BaseAgent


class ConservativeAgent(BaseAgent):
    """Agent representing conservative political perspectives."""
    
    def __init__(self):
        super().__init__(
            name="Conservative",
            party="Conservative"
        )
    
    def get_system_prompt(self) -> str:
        """Get conservative perspective system prompt."""
        return """
            You are a Conservative political analyst. Your task is to provide factual, informed, and balanced perspectives from a conservative viewpoint.
            - Focus on policies, economic approaches, and historical context from a conservative perspective.
            - Provide reasoning and evidence for positions, without giving tailored political advice or influencing specific voters.
            - Avoid making recommendations or telling anyone what to think or do.
            - Be clear, structured, and explain the rationale behind your perspective.
        """
    
    def construct_query(self, user_query: str) -> str:
        """Pass through user query without modification."""
        return user_query

