from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import conversation_routes

# Load .env once
load_dotenv()

app = FastAPI(title="AI Political Debate Mediator API")

app.include_router(conversation_routes.router, prefix="/api/v1/conversation")