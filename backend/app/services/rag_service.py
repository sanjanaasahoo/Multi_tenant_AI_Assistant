"""
app/services/rag_service.py
──────────────────────────────────────────────────────────────────────
Hybrid RAG pipeline with confidence-based routing.

Routes every question through Qdrant first (cheap, local, fast).
Based on the top similarity score:
  - High confidence  → pure RAG answer
  - Medium confidence → RAG context + LLM general knowledge blend
  - Low confidence    → general LLM answer, no company context

chat_service.py calls answer_query() — the only entry point.
──────────────────────────────────────────────────────────────────────
"""

import logging
from functools import lru_cache

from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

from app.config import (
    EMBEDDING_MODEL, QDRANT_COLLECTION,
    TOP_K_CHUNKS, GROQ_API_KEY, GROQ_MODEL, LLM_TEMPERATURE,
    CONTACT, RAG_CONFIDENCE_HIGH, RAG_CONFIDENCE_LOW
)
from app.vectorstore.qdrant_client import get_qdrant_client
from app.services.exceptions import RetrievalError, GenerationError

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
    model = SentenceTransformer(EMBEDDING_MODEL)
    logger.info("Embedding model loaded. Dimension: %d",
                model.get_sentence_embedding_dimension())
    return model


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:
    logger.info("Initializing Groq LLM: %s", GROQ_MODEL)
    return ChatGroq(
        api_key     = GROQ_API_KEY,
        model_name  = GROQ_MODEL,
        temperature = LLM_TEMPERATURE,
        max_tokens  = 512,
    )


# ── System prompts for each routing branch ────────────────────────────

SYSTEM_PROMPT = """You are a professional and helpful AI assistant for Crushaders Tech Solutions, \
a full-service digital marketing agency based in Bhubaneswar, India.

Your job is to answer questions from website visitors using ONLY the information provided \
in the CONTEXT section below.

Rules you must follow:
1. Answer ONLY from the provided context. Do not use any knowledge from outside the context.
2. If the answer is not in the context, say exactly: \
"I don't have that specific information here. Please contact our team at \
{email} or call {phone} — they'll be happy to help."
3. Be professional, warm, and concise. Keep responses under 150 words unless listing items.
4. Never make up facts, numbers, statistics, or client names not in the context.
5. If the question is completely unrelated to digital marketing or Crushaders Tech, \
politely redirect: "That's outside my area. I'm here to help with Crushaders Tech's \
services and digital marketing questions."

CONTEXT:
{{context}}""".format(email=CONTACT["email"], phone=CONTACT["phone"])

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human",  "{question}"),
])

GENERAL_SYSTEM_PROMPT = """You are a helpful AI assistant embedded on the Crushaders Tech \
Solutions website. A visitor has asked a general question that isn't specifically about \
Crushaders Tech.

Answer the question helpfully and accurately using your own knowledge.
Keep the response concise — under 100 words unless the question needs more detail.
If it's natural to do so, you may briefly mention that Crushaders Tech can help with \
digital marketing related needs, but do not force this if it doesn't fit the question.
Do not invent any specific facts about Crushaders Tech itself — you have no company \
context for this question."""

HYBRID_SYSTEM_PROMPT = """You are a professional AI assistant for Crushaders Tech Solutions.

Some relevant company context is provided below, but it may not fully answer the \
question. Use the context where it applies, and supplement with your own general \
knowledge where the context is incomplete. Be clear in your own reasoning about what \
comes from Crushaders Tech specifically versus general knowledge.

Keep the response under 150 words. Be professional and helpful.

CONTEXT:
{context}"""


# ── Embedding ──────────────────────────────────────────────────────────

def embed_query(question: str) -> list[float]:
    model = get_embedding_model()
    vector = model.encode(question, normalize_embeddings=True)
    return vector.tolist()


# ── Qdrant retrieval ───────────────────────────────────────────────────

def search_qdrant(
    query_vector: list[float],
    website_id:   str,
    top_k:        int = TOP_K_CHUNKS
) -> list[dict]:
    """
    Search Qdrant, filtered by website_id.
    Raises RetrievalError on failure — caller must handle it.
    Attaches similarity score to each returned chunk as "_score".
    """
    client = get_qdrant_client()

    website_filter = Filter(
        must=[FieldCondition(key="website_id", match=MatchValue(value=website_id))]
    )

    try:
        results = client.search(
            collection_name = QDRANT_COLLECTION,
            query_vector    = query_vector,
            query_filter    = website_filter,
            limit           = top_k,
            with_payload    = True,
            with_vectors    = False,
        )
    except Exception as e:
        logger.error("Qdrant search failed | website_id=%s | error=%s", website_id, str(e))
        raise RetrievalError(f"Qdrant search failed: {e}") from e

    logger.info(
        "Qdrant retrieval | website_id=%s | results=%d | top_score=%s",
        website_id, len(results),
        round(results[0].score, 3) if results else "N/A"
    )

    return [{**r.payload, "_score": r.score} for r in results if r.payload]


def build_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant information found in the knowledge base."
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk.get("url", "")
        text   = chunk.get("chunk_text", "")
        parts.append(f"[{i}] Source: {source}\n{text}")
    return "\n\n".join(parts)


def extract_sources(chunks: list[dict]) -> list[str]:
    seen, sources = set(), []
    for chunk in chunks:
        url = chunk.get("url", "")
        if url and url not in seen:
            sources.append(url)
            seen.add(url)
    return sources


# ── Main entry point — hybrid router ──────────────────────────────────

async def answer_query(question: str, website_id: str, session_id: str) -> dict:
    logger.info(
        "Query received | website_id=%s | session_id=%s | question=%r",
        website_id, session_id, question[:60]
    )

    try:
        query_vector = embed_query(question)
    except Exception as e:
        logger.error("Embedding failed | error=%s", str(e))
        return {
            "reply": (
                "I'm having trouble processing your question right now. "
                f"Please try again, or reach us at {CONTACT['email']}."
            ),
            "sources": []
        }

    try:
        chunks = search_qdrant(query_vector, website_id)
    except RetrievalError:
        logger.warning("Retrieval unavailable, falling back to general LLM | website_id=%s", website_id)
        return await _generate_general_answer(question)

    top_score = chunks[0]["_score"] if chunks else 0.0

    logger.info(
        "Routing decision | website_id=%s | top_score=%.3f | route=%s",
        website_id, top_score,
        "RAG" if top_score >= RAG_CONFIDENCE_HIGH
        else "HYBRID" if top_score >= RAG_CONFIDENCE_LOW
        else "GENERAL"
    )

    if not chunks or top_score < RAG_CONFIDENCE_LOW:
        return await _generate_general_answer(question)

    if top_score >= RAG_CONFIDENCE_HIGH:
        return await _generate_rag_answer(question, chunks, website_id)

    return await _generate_hybrid_answer(question, chunks, website_id)


async def _generate_rag_answer(question: str, chunks: list[dict], website_id: str) -> dict:
    context = build_context(chunks)
    sources = extract_sources(chunks)

    try:
        llm   = get_llm()
        chain = PROMPT | llm | StrOutputParser()
        reply = await chain.ainvoke({"context": context, "question": question})
    except Exception as e:
        logger.error("LLM generation failed (RAG route) | error=%s", str(e))
        return {
            "reply": (
                f"I found relevant information but I'm having trouble generating "
                f"a response right now. Please try again, or contact us at {CONTACT['email']}."
            ),
            "sources": sources
        }

    logger.info("RAG answer generated | website_id=%s | sources=%s", website_id, sources)
    return {"reply": reply.strip(), "sources": sources}


async def _generate_hybrid_answer(question: str, chunks: list[dict], website_id: str) -> dict:
    context = build_context(chunks)
    sources = extract_sources(chunks)

    hybrid_prompt = ChatPromptTemplate.from_messages([
        ("system", HYBRID_SYSTEM_PROMPT.format(context=context)),
        ("human",  "{question}"),
    ])

    try:
        llm   = get_llm()
        chain = hybrid_prompt | llm | StrOutputParser()
        reply = await chain.ainvoke({"question": question})
    except Exception as e:
        logger.error("LLM generation failed (hybrid route) | error=%s", str(e))
        return {
            "reply": (
                f"I'm having trouble generating a response right now. "
                f"Please try again, or contact us at {CONTACT['email']}."
            ),
            "sources": sources
        }

    logger.info("Hybrid answer generated | website_id=%s | sources=%s", website_id, sources)
    return {"reply": reply.strip(), "sources": sources}


async def _generate_general_answer(question: str) -> dict:
    general_prompt = ChatPromptTemplate.from_messages([
        ("system", GENERAL_SYSTEM_PROMPT),
        ("human",  "{question}"),
    ])

    try:
        llm   = get_llm()
        chain = general_prompt | llm | StrOutputParser()
        reply = await chain.ainvoke({"question": question})
    except Exception as e:
        logger.error("LLM generation failed (general route) | error=%s", str(e))
        return {
            "reply": (
                "I'm having trouble answering right now. Please try again shortly, "
                f"or contact us at {CONTACT['email']}."
            ),
            "sources": []
        }

    logger.info("General answer generated (no company context used)")
    return {"reply": reply.strip(), "sources": []}