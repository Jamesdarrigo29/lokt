from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from rag.chat import ask

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    company: str | None = None


@router.post("/chat")
async def chat(request: Request, body: ChatRequest):
    try:
        return ask(question=body.question, company=body.company, workspace_id=request.state.workspace_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
