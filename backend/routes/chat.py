from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from rag.chat import ask

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    company: str | None = None


@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        return ask(question=request.question, company=request.company)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
