# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AI Personal Trainer: FastAPI backend + Streamlit frontend + Groq LLM (`llama-3.1-8b-instant`) via LangChain, persisted to SQLite through SQLAlchemy. OpenAI is used for two side-channels: GPT-4o vision (`/analyze_image/`) and `text-embedding-3-small` embeddings for the document RAG pipeline (`/upload_document/` → ChromaDB → retrieval injected into `/chat/`).

## Setup & run

- Python deps: `pip install -r requirements.txt` (note: `requirements.txt` lists both `dotenv` and `python-dotenv` — only `python-dotenv` is the real package; `dotenv` is a separate, unrelated PyPI shim). RAG stack adds `pypdf`, `python-docx`, `chromadb`, `langchain-text-splitters`.
- `.env` must define `GROQ_API` **and** `OPENAI_API_KEY` (see `.env.example`). `main.py` raises on startup if either is missing — even endpoints that don't need OpenAI won't start without the key.
- `API_BASE` env var (defaults to `http://localhost:8001`) is read by both Streamlit pages.
- Recommended local start: `bash start.sh` — runs `uvicorn main:app` on `:8001` and Streamlit `app.py` on `:8081`. (CLAUDE.md previously documented `:8000` — that's stale; `start.sh` and the frontend both use `:8001`.)
- `run.py` is a Python launcher that **currently targets a deleted file** (`streamlit run auth.py`). Don't use it without first repointing it at `app.py`. (See "Known broken refs" below.)
- The SQLite DB file `my_database.db` is created in the working dir on first import of `dbSQLAlchemy.py` — there are no migrations.

## Architecture

Three-process flow: **Streamlit (UI) → FastAPI (HTTP) → SQLAlchemy (SQLite) + Groq (LLM) + OpenAI (vision + embeddings) + ChromaDB (vector store)**.

### File layout

```
main.py            # FastAPI app + routes only — no business logic
config.py          # env loading, tunables (model names, RAG params), shared clients (llm, openai_client, chroma_client, text_splitter)
dbSQLAlchemy.py    # SQLAlchemy models, CRUD helpers, get_db() request-scoped session factory
prompts/
  chat.py          # SYSTEM_PROMPT_BASE, SYSTEM_PROMPT_RAG_SUFFIX, UPLOAD_CONFIRMATION_TEMPLATE
  image.py         # IMAGE_ANALYSIS_PROMPT
schemas/
  auth.py          # AuthInput
  chat.py          # ChatInput
  user.py          # UserInput  (preferences submission)
helpers/
  chat.py          # build_prompt(pdf_context), messages_to_history(orm_rows)
  extraction.py    # extract_pdf_text(bytes), extract_docx_text(bytes)  — docx walks tables too
  rag.py           # _collection_name(username), _embed(text), store_document_chunks(), retrieve_relevant_chunks()
app.py             # Streamlit login/signup entry
pages/frontend.py  # Streamlit chat + preferences + uploads UI
```

Each subpackage's `__init__.py` re-exports its public names so `main.py` can do `from helpers import build_prompt, retrieve_relevant_chunks, ...`. Keep the re-exports up to date when you add a new helper/prompt/schema.

### Per-endpoint summary

- **`main.py`** holds the 7 routes (`/login/`, `/signup/`, `/update_preferences/`, `/chat/`, `/chat_history/{username}`, `/analyze_image/`, `/upload_document/`). The `/chat/` endpoint is the core: loads `UserPreferences` + `ChatMessage` history, converts messages via `helpers.chat.messages_to_history`, **retrieves the top-3 RAG chunks** via `helpers.rag.retrieve_relevant_chunks`, builds a `ChatPromptTemplate` via `helpers.chat.build_prompt` whose system message interpolates the user's preferences (goal/experience/days/equipment/tone) and optionally the retrieved fitness-plan context, runs `RunnableSequence(prompt, llm)`, then persists both the user message and the assistant reply.
- **`dbSQLAlchemy.py`** — Models (`User`, `ChatMessage`, `UserPreferences`) and CRUD helpers. Uses `declarative_base()` and creates tables eagerly via `Base.metadata.create_all()` at import time. Exposes `get_db()` as a FastAPI dependency.
- **`app.py`** — Streamlit login/signup entry. Calls FastAPI on `API_BASE` (default `:8001`). On success, `st.switch_page("pages/frontend.py")`.
- **`pages/frontend.py`** — Tabbed UI (Preferences form + Chat). Loads chat history once on first render via `/chat_history/`, then appends locally. Chat tab also exposes an image-upload expander (→ `/analyze_image/`) and a document-upload expander (→ `/upload_document/`).

### RAG pipeline (document upload)

The `/upload_document/` endpoint is the ingestion side of a per-user RAG pipeline:

1. **Extract text** — PDF via `helpers.extraction.extract_pdf_text` (pypdf), DOCX via `helpers.extraction.extract_docx_text`, which reads **both** `doc.paragraphs` and `doc.tables` — table extraction is essential because fitness plans are commonly laid out as tables and `doc.paragraphs` alone returns empty in that case. Unsupported extensions raise `HTTPException(400)`; documents that produce no extractable text raise `HTTPException(422)`. Don't go back to swallowing these as 200 + `{"error": ...}` — the frontend will say "success" while RAG is silently broken.
2. **Chunk** — `config.text_splitter` is a `RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, ...)` singleton. Tunable via the constants at the top of `config.py`.
3. **Embed + store** — `helpers.rag.store_document_chunks()` **deletes the user's existing collection first** (so re-uploads don't collide on `chunk_i` IDs and a shorter new doc fully replaces a longer old one), creates a fresh collection named by `_collection_name(username)`, embeds each non-empty chunk with `openai_client.embeddings.create(model=OPENAI_EMBEDDING_MODEL)`, and inserts it. Chunks are keyed `chunk_0`…`chunk_N` and tagged with `{chunk_index, username}` metadata. Raises if every chunk is empty (caught and rethrown as `HTTPException(500)` by the endpoint). **Always use `_collection_name(username)` on both write and read paths** — usernames may contain spaces or punctuation that ChromaDB's `[a-zA-Z0-9._-]{3,512}` collection-name regex rejects, so the helper slugifies them to `user_<safe>_fitness_plan`.
4. **Backup** — the raw concatenated text is also written to `UserPreferences.pdf_text` via `db.update_user_pdf_text()`. This column is **not read anywhere**; the live retrieval path goes through ChromaDB. Treat `pdf_text` as a debug/forensic backup, not a source of truth.

The retrieval side lives in `/chat/`: every chat call invokes `helpers.rag.retrieve_relevant_chunks(username, query, top_k=RAG_TOP_K)`, which embeds the user's message with the same OpenAI model, queries the user's collection, and joins the top-k documents with `\n\n`. If the collection doesn't exist (no upload yet) the function catches the exception and returns `None`, and `helpers.chat.build_prompt()` skips the RAG-context block entirely.

**Storage location.** `chromadb.PersistentClient(path="./chroma_db")` persists collections to disk under `./chroma_db/` (gitignored). Uploads survive uvicorn restarts. Deleting the directory wipes everyone's documents; deleting a single user's data is `chroma_client.delete_collection(name=f"user_{username}_fitness_plan")`.

**Prompt template coupling.** `helpers.chat.build_prompt(pdf_context=...)` builds the RAG block by **f-string concatenation** of `prompts.chat.SYSTEM_PROMPT_RAG_SUFFIX` onto `prompts.chat.SYSTEM_PROMPT_BASE` *before* `ChatPromptTemplate.from_messages()` is called. This is deliberate — passing it through LangChain's `{var}` interpolation would force callers to pass `pdf_context` on every `chain.invoke()`. If you refactor this, also update the prompt to read `{pdf_context}` and add it to the `chain.invoke({...})` dict in `/chat/`. The hard-coded "user currently has NO GYM ACCESS" line inside `SYSTEM_PROMPT_RAG_SUFFIX` is a project-specific override, not a generic instruction — if a user does have gym access this prompt will fight their preferences.

### Image analysis (`/analyze_image/`)

Multipart upload → base64 → OpenAI `gpt-4o` chat completion with a fixed expert-fitness-coach prompt → response is saved as an assistant message in chat history under a `[Uploaded an exercise image for analysis]` placeholder user message. This path **does not** use Groq, LangChain, or RAG — it's a one-shot OpenAI call independent of the chat chain.

### Auth model (important to understand)

There are no passwords. "Login" = "does this username exist?"; "Signup" = "create row with this username". Each Streamlit session generates a fresh `session_id` (UUID4) that's stored on `User.session_id` — it's overwritten on every login and never validated by the backend. Treat this as a demo-grade identity layer, not real auth.

### Session handling

DB sessions are **per-request via `Depends(db.get_db)`**. Every endpoint takes `db_sess: Session = Depends(db.get_db)` as a parameter and passes it to CRUD helpers. The previous module-level `session = SessionLocal()` was removed because a single failed write (e.g. a raised `HTTPException` mid-transaction) would close the shared transaction and break every subsequent request with `ResourceClosedError: This transaction is closed`. Don't reintroduce a module-level session — add new endpoints with the `Depends(db.get_db)` pattern.

### Preferences storage quirk

`UserPreferences` has `preferences_json` (string) **plus** discrete `age`/`gender`/`pdf_text` columns on the model. The API only writes/reads `preferences_json` (a JSON blob containing all preference fields including age/gender). `pdf_text` is written by `/upload_document/` but never read. The discrete columns are dead schema — leave them alone unless deliberately migrating off the JSON blob.

**Schema-drift hazard.** `Base.metadata.create_all()` only creates *missing* tables; it does **not** add new columns to existing tables. If `my_database.db` was created before `pdf_text` was added to the model (the column landed in the same uncommitted change that introduced RAG), writes to `pdf_text` will fail with `OperationalError: no such column`. Fix by deleting the DB file and re-creating, or by issuing an `ALTER TABLE user_preferences ADD COLUMN pdf_text TEXT`.

## Known broken refs

These exist in tracked code and will surface as bugs if you exercise those paths — fix in place rather than replicating the pattern:

- `run.py` runs `streamlit run auth.py`, but `auth.py` has been deleted (visible in `git status` as `D auth.py`). The current Streamlit entry is `app.py`.
- `pages/frontend.py` calls `st.switch_page("auth.py")` when the user isn't logged in — same dangling reference; should be `app.py`.

## Conventions worth respecting

- **Where things go.** New Pydantic request bodies → `schemas/<name>.py` + re-export from `schemas/__init__.py`. New prompt strings → `prompts/<topic>.py` + re-export from `prompts/__init__.py`. New helpers → group by concern under `helpers/` (rag / extraction / chat) and re-export. Tunables (model names, sizes, paths) → `config.py`. `main.py` stays thin: routes only, no business logic.
- Multipart endpoints (`/analyze_image/`, `/upload_document/`) use `UploadFile = File(...)` + `Form(...)` instead of a Pydantic body — don't try to wrap those in a `schemas/` model.
- Chat history is the source of truth for LangChain memory — there's no in-memory `ConversationBufferMemory`. Every `/chat/` call rebuilds memory from the DB. Don't introduce a parallel in-process cache without removing the DB read.
- The system prompt in `prompts.chat.SYSTEM_PROMPT_BASE` interpolates five preference keys (`goal`, `experience`, `days_per_week`, `equipment`, `tone`). If you add a preference, update both the prompt template and the `chain.invoke({...})` call site in `main.py:/chat/` together — they're coupled by string key.
- RAG context is the **only** other thing in the system prompt — it's appended via f-string before template construction (see "Prompt template coupling" above), not via LangChain interpolation. Keep it that way unless you're also rewriting the invoke site.
