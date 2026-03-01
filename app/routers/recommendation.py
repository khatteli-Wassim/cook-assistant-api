from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from app.graph.workflow import recommendation_graph
import asyncio

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Message]] = []
    location: Optional[str] = None

def build_history(history: List[Message]):
    result = []
    for msg in history:
        if msg.role == "user":
            result.append(HumanMessage(content=msg.content))
        else:
            result.append(AIMessage(content=msg.content))
    return result

async def stream_response(message: str, history: List[Message], location: Optional[str]):
    lc_history = build_history(history)

    initial_state = {
        "message": message,
        "history": lc_history,
        "location": location or "",
        "agents": [],
        "agents_done": [],
    }

    # Run graph in thread to avoid blocking
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: recommendation_graph.invoke(initial_state)
    )

    final = result.get("final_response", "Sorry, something went wrong.")

    # Stream the final response word by word
    words = final.split(" ")
    for i, word in enumerate(words):
        yield word + (" " if i < len(words) - 1 else "")
        await asyncio.sleep(0.03)

@router.post("/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(
        stream_response(request.message, request.history or [], request.location),
        media_type="text/plain"
    )