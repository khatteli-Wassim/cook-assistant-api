from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from app.chains.prompts import chat_chain

router = APIRouter()

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []

def build_history(history: List[Message]):
    result = []
    for msg in history:
        if msg.role == "user":
            result.append(HumanMessage(content=msg.content))
        else:
            result.append(AIMessage(content=msg.content))
    return result

async def stream_response(message: str, history: List[Message]):
    lc_history = build_history(history)
    async for chunk in chat_chain.astream({
        "input": message,
        "history": lc_history
    }):
        if chunk.content:
            yield chunk.content

@router.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        stream_response(request.message, request.history or []),
        media_type="text/plain"
    )