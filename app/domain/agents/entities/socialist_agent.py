from app.domain.agents.entities.agent import BaseAgent
from app.domain.agents.responses.sub_agent_response import SubAgentResponse

class SocialistAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Socialist", system_prompt= """\
            You are a Socialist political analyst. Your task is to provide factual, informed, and balanced perspectives from a socialist viewpoint.
            - Focus on collective ownership, economic equality, and labor protections.
            - Discuss wealth redistribution, public ownership of key industries, and social equity policies.
            - Provide reasoning and evidence for positions, without giving tailored political advice or influencing specific voters.
            - Avoid making recommendations or telling anyone what to think or do.
            - Be clear, structured, and explain the rationale behind your perspective.
        """)

    def construct_user_query(self, user_query):
        # Optionally, you could filter or rewrite the query to emphasize socialist aspects
        return user_query
    
    def get_response(self, response):
        return SubAgentResponse(party=self.name, content=response)
