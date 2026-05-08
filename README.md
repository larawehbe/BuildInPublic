# AI Personal Trainer

A simple full-stack AI app that acts as a personalized fitness coach. Users sign up, set their training preferences, and chat with an AI trainer that adapts to their goals, experience level, equipment, and preferred coaching tone.

## Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **LLM:** Groq (`llama-3.1-8b-instant`) via LangChain
- **Database:** SQLite via SQLAlchemy

## Project structure

```
.
├── main.py              # FastAPI backend (auth, preferences, chat endpoints)
├── dbSQLAlchemy.py      # SQLAlchemy models + CRUD helpers
├── app.py               # Streamlit entry: login / signup
├── pages/frontend.py    # Streamlit page: preferences form + chat UI
├── start.sh             # Launch backend + frontend together
├── requirements.txt
└── .env.example
```

## Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy `.env.example` to `.env` and fill in your Groq API key:

```bash
cp .env.example .env
```

```env
GROQ_API=your_groq_api_key_here
```

You can get an API key from [console.groq.com](https://console.groq.com/).

## Running the app

### Option A — `start.sh` (recommended)

```bash
bash start.sh
```

This starts:
- FastAPI on `http://localhost:8000`
- Streamlit on `http://localhost:8081`

Open the Streamlit URL in your browser.

### Option B — run the two services manually

In one terminal:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

In another:

```bash
streamlit run app.py
```

## API endpoints

| Method | Path                        | Purpose                                  |
|--------|-----------------------------|------------------------------------------|
| POST   | `/signup/`                  | Create a new user                        |
| POST   | `/login/`                   | Look up an existing user                 |
| POST   | `/update_preferences/`      | Save / update training preferences       |
| POST   | `/chat/`                    | Send a message to the AI trainer        |
| GET    | `/chat_history/{username}`  | Fetch a user's full chat history         |

## How chat works

On every `/chat/` call the backend:

1. Loads the user's saved preferences and full chat history from SQLite.
2. Rebuilds LangChain memory from the stored messages.
3. Builds a system prompt that interpolates the user's `goal`, `experience`, `days_per_week`, `equipment`, and `tone`.
4. Runs the prompt + history + new message through the Groq LLM.
5. Persists both the user's message and the assistant's reply.

## Notes

- The database file `my_database.db` is created automatically on first run; there are no migrations.
- Authentication is username-only (no passwords) — this project is intended as a demo, not a production deployment.

## License

MIT — see [LICENSE](LICENSE).
