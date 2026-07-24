"""
app/services/exceptions.py
──────────────────────────────────────────────────────────────────────
Custom exceptions for the RAG pipeline.

Why custom exceptions instead of catching generic Exception everywhere?
Specific exceptions let chat_service.py respond differently to
different failure types — a Qdrant outage should give a different
user message than a Groq rate limit.
──────────────────────────────────────────────────────────────────────
"""


class RetrievalError(Exception):
    """Raised when Qdrant search fails (connection issue, timeout, etc.)"""
    pass


class GenerationError(Exception):
    """Raised when the LLM call fails (rate limit, API error, timeout)"""
    pass