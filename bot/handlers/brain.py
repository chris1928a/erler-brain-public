"""Brain (RAG) and direct AI handlers."""
import logging
from services.rag import search as rag_search
from services.gemini import call_gemini_direct
from services.claude import call_claude
from services.session import load_session, format_history

logger = logging.getLogger("handler.brain")


async def handle_brain(query: str, user_id: str) -> str:
    """Search brain via FAISS RAG, then answer with Gemini."""
    chunks = await rag_search(query, top_k=5)
    if not chunks:
        return "No relevant documents found."

    context = "\n\n---\n\n".join(
        f"[{c['source']}] (Score: {c['score']:.3f})\n{c['text']}" for c in chunks
    )

    prompt = f"""Answer the question based on these documents from the knowledge base.

DOCUMENTS:
{context}

QUESTION: {query}

Be precise and cite the sources."""

    response = await call_gemini_direct(prompt)
    sources = ", ".join(set(c["source"] for c in chunks))
    return f"{response}\n\nSources: {sources}"


async def handle_ask(query: str, user_id: str) -> str:
    """Direct AI query without RAG."""
    return await call_gemini_direct(query)


async def handle_smart(text: str, user_id: str, history: str = "", model: str = "gemini-flash") -> str:
    """Smart search: try RAG first, fall back to direct AI."""
    # Try RAG
    chunks = await rag_search(text, top_k=3)

    if chunks and chunks[0]["score"] < 1.0:
        # Good RAG match
        context = "\n\n".join(c["text"] for c in chunks[:3])
        prompt = f"""Context from the knowledge base:
{context}

Conversation:
{history}

Question: {text}

Answer helpfully."""

        if model == "claude-sonnet-4-6":
            return await call_claude(prompt, history=history)
        return await call_gemini_direct(prompt)
    else:
        # No good RAG match, direct AI
        prompt = f"""Conversation:
{history}

Question: {text}

Answer helpfully."""

        if model == "claude-sonnet-4-6":
            return await call_claude(prompt, history=history)
        return await call_gemini_direct(prompt)
