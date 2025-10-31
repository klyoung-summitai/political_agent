from fastapi import APIRouter, Request, Depends
##from app.schemas.query_schema import QueryRequest, QueryResponse
from app.domain.orchestration.services.base_orchestration_service import OrchestratorAsync
from pydantic import BaseModel
from app.domain.agents.responses.mediator_response import MediatorResponse

router = APIRouter()

@router.post("/")
async def handle_conversation(request: Request, orchestration_service: OrchestratorAsync = Depends(lambda: OrchestratorAsync())):
    body = await request.json()
    res : MediatorResponse = await orchestration_service.route_and_execute(body.get("topic"))
    return res
