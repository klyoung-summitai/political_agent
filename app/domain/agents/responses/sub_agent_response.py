from pydantic import BaseModel

class SubAgentResponse(BaseModel):
    party: str
    content: str
    