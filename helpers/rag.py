"""ChromaDB-backed RAG: per-user chunk storage and semantic retrieval."""

from __future__ import annotations

import logging
import re

from config import OPENAI_EMBEDDING_MODEL, RAG_TOP_K, chroma_client, openai_client

logger = logging.getLogger(__name__)


def _collection_name(username: str) -> str:
    """Slugify a username into a ChromaDB-legal collection name.

    ChromaDB requires `[a-zA-Z0-9._-]{3,512}` starting and ending with an
    alphanumeric — usernames with spaces or punctuation would be rejected.
    """
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", username).strip("._-") or "user"
    return f"user_{safe}_fitness_plan"


def _embed(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        input=text,
        model=OPENAI_EMBEDDING_MODEL,
    )
    return response.data[0].embedding


def store_document_chunks(username: str, chunks: list[str]) -> None:
    """Replace any previously stored document for this user with new chunks."""
    name = _collection_name(username)
    chroma_client.delete_collection(name=name)
    collection = chroma_client.create_collection(name=name)

    non_empty = [c.strip() for c in chunks if c and c.strip()]
    if not non_empty:
        raise ValueError("Document produced no non-empty chunks after splitting")

    for i, chunk in enumerate(non_empty):
        collection.add(
            ids=[f"chunk_{i}"],
            embeddings=[_embed(chunk)],
            documents=[chunk],
            metadatas=[{"chunk_index": i, "username": username}],
        )


def retrieve_relevant_chunks(
    username: str, query: str, top_k: int = RAG_TOP_K
) -> str | None:
    """Return the top-k most relevant chunks joined by blank lines, or None
    when the user hasn't uploaded a document yet."""
    name = _collection_name(username)
    try:
        collection = chroma_client.get_collection(name=name)
    except Exception:
        logger.info("No RAG collection for user=%s yet", username)
        return None

    results = collection.query(
        query_embeddings=[_embed(query)],
        n_results=top_k,
    )
    docs = results.get("documents") or []
    if not docs or not docs[0]:
        return None
    return "\n\n".join(docs[0])
