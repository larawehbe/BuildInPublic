# AI Personal Trainer

## Overview
A full-stack AI application that generates personalized gym workout plans using OpenAI.

## Architecture
- **Frontend**: Streamlit (port 5000) - User interface for collecting fitness goals
- **Backend**: FastAPI with uvicorn (port 8000) - API for generating workout plans
- **AI**: OpenAI GPT-4o-mini via Replit AI Integrations

## Running the Application
The application is run via `python run.py` which:
1. Starts the FastAPI backend on localhost:8000
2. Starts the Streamlit frontend on 0.0.0.0:5000

## Project Structure
```
├── api.py          # FastAPI backend with OpenAI integration
├── frontend.py     # Streamlit frontend
├── run.py          # Launcher script for both services
├── main.py         # CLI version (not used in web app)
├── requirements.txt
└── replit.md
```

## Dependencies
- fastapi, uvicorn - Web API framework
- streamlit - Frontend framework  
- openai - AI integration (uses Replit AI Integrations)
- pydantic - Data validation

## Notes
- OpenAI access is provided through Replit AI Integrations (no API key needed)
- Backend runs on localhost, frontend binds to 0.0.0.0 for Replit proxy access
