"""Mediator agent for orchestrating political agent responses."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI
from app.domain.agents.responses.mediator_response import MediatorResponse


class MediatorAgent:
    """Mediator agent that determines which agents to invoke and synthesizes responses."""
    
    def __init__(self):
        self.name = "Mediator"
        self.llm = ChatOpenAI(model="gpt-4o", max_tokens=200)
    
    def execute(self, user_query: str) -> str:
        """Determine which agents should respond to the query."""
        from langchain.schema import SystemMessage, HumanMessage
        
        system_prompt = 'You are a neutral mediator deciding which agents to invoke.'
        user_message = f"""
        You are a mediator. Determine which agents should respond to the query.
        Available agents: ["conservative", "liberal", "socialist"]
        Return a JSON object like:
        {{ "agents_to_invoke": ["liberal", "conservative", "socialist"] }}
        User query: {user_query}
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_message)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def get_available_agents(self):
        """Get available agents using factory pattern."""
        # Import here to avoid circular dependency
        from app.domain.agents.factories.agent_factory import AgentFactory, get_global_registry
        
        factory = AgentFactory(get_global_registry())
        return factory.create_batch(["conservative", "liberal", "socialist"])
    
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