"""
app/services/chat_service.py
──────────────────────────────────────────────────────────────────────
Orchestration layer.

Phase 1:  Called intent_service → response_builder
Phase 2:  Calls rag_service.answer_query()

Everything else (router, schemas, frontend) is unchanged.
──────────────────────────────────────────────────────────────────────
"""

import logging
from app.services.rag_service import answer_query

logger = logging.getLogger(__name__)


async def handle_message(
    message:    str,
    website_id: str,
    session_id: str
) -> dict:
    """
    Process a user message and return a response dict.
    Returns { "reply": str, "sources": list[str] }
    """
    logger.info(
        "Handling message | website_id=%s | session_id=%s | message=%r",
        website_id, session_id, message[:80]
    )

    # Phase 2: RAG pipeline
    # This is the only line that changed from Phase 1
    return await answer_query(
        question   = message,
        website_id = website_id,
        session_id = session_id,
    )