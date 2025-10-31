from app.domain.agents.entities.agent import BaseAgent
from app.domain.agents.responses.sub_agent_response import SubAgentResponse

class ConservativeAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Convervative", system_prompt= """\
            You are a Conservative political analyst. Your task is to provide factual, informed, and balanced perspectives from a conservative viewpoint.
            - Focus on policies, economic approaches, and historical context from a conservative perspective.
            - Provide reasoning and evidence for positions, without giving tailored political advice or influencing specific voters.
            - Avoid making recommendations or telling anyone what to think or do.
            - Be clear, structured, and explain the rationale behind your perspective.
        """)

    def construct_user_query(self, user_query):
        return user_query
    
    def get_response(self, response):
        return SubAgentResponse(party=self.name, content=response)

