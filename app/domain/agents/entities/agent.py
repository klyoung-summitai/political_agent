from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI

class BaseAgent(ABC):
    def __init__(self, name: str, model_name: str = "gpt-4o-mini", system_prompt: str = None):
        if not name:
            raise ValueError("Agent must have a name.")
        self.name = name
        self.model_name = model_name
        self.system_prompt = system_prompt or self.default_system_prompt()
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """LLM initialization — can be swapped or subclassed."""
        return ChatOpenAI(model=self.model_name, max_tokens=200)

    def default_system_prompt(self) -> str:
        """Fallback system prompt for dynamically created agents."""
        return "You are a generic agent that can respond to arbitrary queries."
    
    def get_response(self, response) -> str:
        return response

    @abstractmethod
    def construct_user_query(self, user_query: str) -> str:
        pass

    def execute(self, user_query: str) -> str:
        from langchain.schema import SystemMessage, HumanMessage
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=self.construct_user_query(user_query))
        ]
        response = self.llm.invoke(messages)
        return self.get_response(response.content)