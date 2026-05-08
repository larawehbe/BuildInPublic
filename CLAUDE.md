# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

AI Personal Trainer: FastAPI backend + Streamlit frontend + Groq LLM (`llama-3.1-8b-instant`) via LangChain, persisted to SQLite through SQLAlchemy.

## Setup & run

- Python deps: `pip install -r requirements.txt` (note: `requirements.txt` lists both `dotenv` and `python-dotenv` — only `python-dotenv` is the real package; `dotenv` is a separate, unrelated PyPI shim).
- `.env` must define `GROQ_API` (see `.env.example`). `main.py` raises on startup if it's missing.
- Recommended local start: `bash start.sh` — runs `uvicorn main:app` on `:8000` and Streamlit `app.py` on `:8081`.
- `run.py` is a Python launcher that **currently targets a deleted file** (`streamlit run auth.py`). Don't use it without first repointing it at `app.py`. (See "Known broken refs" below.)
- The SQLite DB file `my_database.db` is created in the working dir on first import of `dbSQLAlchemy.py` — there are no migrations.

## Architecture

Three-process flow: **Streamlit (UI) → FastAPI (HTTP) → SQLAlchemy (SQLite) + Groq (LLM)**.

- **`main.py`** — FastAPI app. Endpoints: `/login/`, `/signup/`, `/update_preferences/`, `/chat/`, `/chat_history/{username}`. The `/chat/` endpoint is the core: it loads `UserPreferences` + `ChatMessage` history from DB, converts messages into LangChain `HumanMessage`/`AIMessage` objects, builds a `ChatPromptTemplate` whose system message interpolates the user's preferences (goal/experience/days/equipment/tone), runs `RunnableSequence(prompt, llm)`, then persists both the user message and the assistant reply.
- **`dbSQLAlchemy.py`** — Models (`User`, `ChatMessage`, `UserPreferences`) and CRUD helpers. Uses `declarative_base()` and creates tables eagerly via `Base.metadata.create_all()` at import time.
- **`app.py`** — Streamlit login/signup entry. Calls FastAPI on `localhost:8000`. On success, `st.switch_page("pages/frontend.py")`.
- **`pages/frontend.py`** — Tabbed UI (Preferences form + Chat). Loads chat history once on first render via `/chat_history/`, then appends locally as the user sends messages.

### Auth model (important to understand)

There are no passwords. "Login" = "does this username exist?"; "Signup" = "create row with this username". Each Streamlit session generates a fresh `session_id` (UUID4) that's stored on `User.session_id` — it's overwritten on every login and never validated by the backend. Treat this as a demo-grade identity layer, not real auth.

### Session handling caveat

`dbSQLAlchemy.py` creates a single module-level `session = SessionLocal()` and `main.py` reuses it across all requests (`db.session`). This is not request-scoped and not thread-safe under real concurrency — fine for local dev with a single uvicorn worker, but don't assume FastAPI dependency-injected sessions exist here.

### Preferences storage quirk

`UserPreferences` has both a `preferences_json` string column **and** discrete `age`/`gender` columns on the model. The API only writes/reads `preferences_json` (a JSON-encoded blob containing all fields including age/gender). The discrete columns are dead schema — leave them alone unless deliberately migrating off the JSON blob.

## Known broken refs

These exist in tracked code and will surface as bugs if you exercise those paths — fix in place rather than replicating the pattern:

- `run.py` runs `streamlit run auth.py`, but `auth.py` has been deleted (visible in `git status` as `D auth.py`). The current Streamlit entry is `app.py`.
- `pages/frontend.py` calls `st.switch_page("auth.py")` when the user isn't logged in — same dangling reference; should be `app.py`.

## Conventions worth respecting

- All FastAPI request bodies are Pydantic `BaseModel` subclasses defined inline in `main.py` (`UserInput`, `ChatInput`, `AuthInput`). Add new ones the same way unless the file gets unwieldy.
- Chat history is the source of truth for LangChain memory — there's no in-memory `ConversationBufferMemory`. Every `/chat/` call rebuilds memory from the DB. Don't introduce a parallel in-process cache without removing the DB read.
- The system prompt in `build_prompt_template()` interpolates five preference keys (`goal`, `experience`, `days_per_week`, `equipment`, `tone`). If you add a preference, update both the prompt template and the `chain.invoke({...})` call site in `/chat/` together — they're coupled by string key.
