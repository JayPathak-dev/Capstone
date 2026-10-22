from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    history: List[ChatMessage] = []


class ReferencedProject(BaseModel):
    project_id: str
    project_code: str
    project_name: str
    sector: str
    risk_score: float
    risk_level: str


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    tools_used: List[str] = []
    referenced_projects: List[ReferencedProject] = []
    suggested_followups: List[str] = []
