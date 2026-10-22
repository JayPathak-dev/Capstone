from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.assistant import ChatRequest, ChatResponse
from backend.app.services.assistant import process_assistant_chat

router = APIRouter(prefix="/assistant", tags=["AI Assistant"])


@router.post("/chat", response_model=ChatResponse)
def chat_with_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Grounded AI Assistant endpoint using controlled backend tools."""
    return process_assistant_chat(db=db, request=request)
