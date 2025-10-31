from pydantic import BaseModel

class MediatorResponse(BaseModel):
    summary: str
    contradictions: str
    political_parties: list[str]
    