import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.chat_service import handle_message
from app.config import ALLOWED_WEBSITE_IDS

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/chat", response_model=ChatResponse, summary="Send a message to the chatbot")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main chat endpoint.

    Validates the website_id against the whitelist, then delegates
    to chat_service for response generation. The router itself
    never contains business logic — it only handles HTTP concerns.
    """
    if request.website_id not in ALLOWED_WEBSITE_IDS:
        logger.warning("Rejected unknown website_id: %s", request.website_id)
        raise HTTPException(
            status_code=400,
            detail=f"Unknown website_id '{request.website_id}'. "
                   f"Allowed: {ALLOWED_WEBSITE_IDS}"
        )

    result = await handle_message(
        message=request.message,
        website_id=request.website_id,
        session_id=request.session_id,
    )

    return ChatResponse(reply=result["reply"], sources=result["sources"])   