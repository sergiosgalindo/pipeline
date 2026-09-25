import os

from fastapi import APIRouter, HTTPException

from app.models.assistant import AssistantError, answer_question
from app.models.schemas import ChatRequest, ChatResponse


router = APIRouter(prefix="/api", tags=["chat"])


@router.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True, "configured": bool(os.getenv("GROQ_API_KEY"))}


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        answer, sources = answer_question(payload)
    except AssistantError as error:
        raise HTTPException(status_code=error.status_code, detail=str(error)) from error
    return ChatResponse(answer=answer, sources=sources)
