from langchain_core.prompts import ChatPromptTemplate
from app.domain.agents.entities.agent import BaseAgent
from langchain_core.output_parsers import PydanticOutputParser
from app.domain.agents.entities.liberal_agent import LiberalAgent
from app.domain.agents.responses.mediator_response import MediatorResponse
from app.domain.agents.entities.conservative_agent import ConservativeAgent
from app.domain.agents.entities.socialist_agent import SocialistAgent

class MediatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Mediator", model_name="gpt-4o", system_prompt='You are a neutral mediator deciding which agents to invoke.')

    def construct_user_query(self, user_query):
        return f"""
        You are a mediator. Determine which agents should respond to the query.
        Agents: {list(self.get_available_agents())}
        Return a JSON object like:
        {{ "agents_to_invoke": ["liberal", "conservative"] }}
        User query: {user_query}
        """
    
    def get_available_agents(self):
        return {
            "conservative": ConservativeAgent(),
            "liberal": LiberalAgent(),
            "socialist": SocialistAgent()
        }
    
    def get_synthesize_prompt(self):
        parser = PydanticOutputParser(pydantic_object=MediatorResponse)

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a neutral political mediator. You will receive responses from multiple political agents, 
                    each representing a different political party. Your task is to:

                        1. Summarize the main points from all political parties involved in a neutral and concise way.
                        2. List all political parties included in the summary.
                        3. If there are contradictions between parties' positions, explicitly highlight them under 'contradictions'.
                    
                    CRITICAL: You MUST include ALL THREE fields in your response:
                    - "summary": string with the neutral summary
                    - "contradictions": string describing conflicts (use empty string "" if none)
                    - "political_parties": array of party names (e.g., ["Conservative", "Liberal", "Socialist"])
                    
                    OUTPUT FORMAT: Return ONLY raw JSON. Do NOT wrap it in markdown code blocks (```json).
                    
                    {format_instructions}
                    """,
                ),
              ##TODO  ("placeholder", "{chat_history}"),
                ("human",
                """
                The user asked the following question:
                "{query}"

                Here are the responses from each political agent:
                {sub_agent_responses}

                Please synthesize these into one structured MediatorResponse.
                
                IMPORTANT: Extract ALL party names from the responses above and include them in the "political_parties" array.
                For example, if you see "Conservative:", "Liberal:", and "Socialist:" in the responses, 
                your political_parties field MUST be: ["Conservative", "Liberal", "Socialist"]
                """,),
                
               #TODO ("placeholder", "{agent_scratchpad}"),
            ]
        ).partial(format_instructions=parser.get_format_instructions())

        return prompt, parser