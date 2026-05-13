from __future__ import annotations

import os

import chromadb
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
from pydantic import SecretStr

load_dotenv()

GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_TEMPERATURE = 0.7

OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_VISION_MODEL = "gpt-4o"
OPENAI_VISION_MAX_TOKENS = 1000

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RAG_TOP_K = 3
CHROMA_PATH = "./chroma_db"

SUPPORTED_DOC_EXTENSIONS = {"pdf", "docx"}


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"{name} not found in environment variables.")
    return value


_GROQ_API_KEY = _require_env("GROQ_API")
_OPENAI_API_KEY = _require_env("OPENAI_API_KEY")

llm = ChatGroq(
    temperature=GROQ_TEMPERATURE,
    model=GROQ_MODEL,
    api_key=SecretStr(_GROQ_API_KEY),
)
openai_client = OpenAI(api_key=_OPENAI_API_KEY)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
)
