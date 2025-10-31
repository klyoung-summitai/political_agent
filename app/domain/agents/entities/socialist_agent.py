"""Socialist political agent implementation."""

from app.domain.agents.entities.agent import BaseAgent


class SocialistAgent(BaseAgent):
    """Agent representing socialist political perspectives."""
    
    def __init__(self):
        super().__init__(
            name="Socialist",
            party="Socialist"
        )
    
    def get_system_prompt(self) -> str:
        """Get socialist perspective system prompt."""
        return """
            You are a Socialist political analyst. Your task is to provide factual, informed, and balanced perspectives from a socialist viewpoint.
            - Focus on collective ownership, economic equality, and labor protections.
            - Discuss wealth redistribution, public ownership of key industries, and social equity policies.
            - Provide reasoning and evidence for positions, without giving tailored political advice or influencing specific voters.
            - Avoid making recommendations or telling anyone what to think or do.
            - Be clear, structured, and explain the rationale behind your perspective.
        """
    
    def construct_query(self, user_query: str) -> str:
        """Pass through user query without modification."""
        return user_query
