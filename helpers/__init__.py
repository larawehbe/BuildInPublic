"""Helpers grouped by concern: chat plumbing, document extraction, RAG."""

from helpers.chat import build_prompt, messages_to_history
from helpers.extraction import extract_docx_text, extract_pdf_text
from helpers.rag import retrieve_relevant_chunks, store_document_chunks

__all__ = [
    "build_prompt",
    "extract_docx_text",
    "extract_pdf_text",
    "messages_to_history",
    "retrieve_relevant_chunks",
    "store_document_chunks",
]
