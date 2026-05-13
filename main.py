"""AI Personal Trainer FastAPI backend — routes only.

Configuration lives in config.py, prompts in prompts/, schemas in schemas/,
and helpers in helpers/. See CLAUDE.md for the architectural overview.
"""

from __future__ import annotations

import base64
import json
import logging

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from langchain_core.runnables import RunnableSequence
from sqlalchemy.orm import Session

import dbSQLAlchemy as db
from config import (
    OPENAI_VISION_MAX_TOKENS,
    OPENAI_VISION_MODEL,
    SUPPORTED_DOC_EXTENSIONS,
    llm,
    openai_client,
    text_splitter,
)
from helpers import (
    build_prompt,
    extract_docx_text,
    extract_pdf_text,
    messages_to_history,
    retrieve_relevant_chunks,
    store_document_chunks,
)
from prompts import IMAGE_ANALYSIS_PROMPT, UPLOAD_CONFIRMATION_TEMPLATE
from schemas import AuthInput, ChatInput, UserInput

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.post("/login/")
def login(data: AuthInput, db_sess: Session = Depends(db.get_db)):
    user = db.get_user(db_sess, data.username)
    if not user:
        return {"exists": False}
    db.update_session(db_sess, data.username, data.session_id)
    return {"exists": True}


@app.post("/signup/")
def signup(data: AuthInput, db_sess: Session = Depends(db.get_db)):
    if db.get_user(db_sess, data.username):
        return {"exists": True}
    db.create_user(db_sess, data.username, data.session_id)
    return {"exists": False}


@app.post("/update_preferences/")
def update_preferences(data: UserInput, db_sess: Session = Depends(db.get_db)):
    preferences_json = json.dumps({
        "age": data.age,
        "gender": data.gender,
        "goal": data.goal,
        "experience": data.experience,
        "days_per_week": data.days_per_week,
        "equipment": data.equipment,
        "tone": data.tone,
        "weight": data.weight,
        "height": data.height,
    })
    if db.get_user_preferences(db_sess, data.username):
        db.update_user_preferences(db_sess, data.username, preferences_json)
    else:
        db.create_user_preferences(db_sess, data.username, preferences_json)


@app.get("/chat_history/{username}")
def get_chat_history(username: str, db_sess: Session = Depends(db.get_db)):
    messages = db.get_chat_messages(db_sess, username)
    return {"messages": [{"role": m.role, "content": m.content} for m in messages]}


@app.post("/chat/")
def chat(data: ChatInput, db_sess: Session = Depends(db.get_db)):
    user_preferences = db.get_user_preferences(db_sess, data.username)
    if not user_preferences:
        raise HTTPException(status_code=400, detail="Please set your preferences first.")

    history = messages_to_history(db.get_chat_messages(db_sess, data.username))
    rag_context = retrieve_relevant_chunks(data.username, data.message)
    logger.info("chat user=%s rag_applied=%s", data.username, rag_context is not None)

    chain = RunnableSequence(build_prompt(rag_context), llm)
    preferences = json.loads(user_preferences.preferences_json)

    response = chain.invoke({
        "goal": preferences["goal"],
        "experience": preferences["experience"],
        "days_per_week": preferences["days_per_week"],
        "equipment": preferences["equipment"],
        "tone": preferences["tone"],
        "chat_history": history,
        "input": data.message,
    })
    assistant_reply = str(response.content)

    db.create_chat_message(db_sess, data.username, "user", data.message)
    db.create_chat_message(db_sess, data.username, "assistant", assistant_reply)
    return {"response": assistant_reply}


@app.post("/analyze_image/")
async def analyze_image(
    file: UploadFile = File(...),
    username: str = Form(...),
    db_sess: Session = Depends(db.get_db),
):
    image_bytes = await file.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    mime_type = file.content_type or "image/jpeg"

    response = openai_client.chat.completions.create(
        model=OPENAI_VISION_MODEL,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": IMAGE_ANALYSIS_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}},
            ],
        }],
        max_tokens=OPENAI_VISION_MAX_TOKENS,
    )
    analysis = response.choices[0].message.content or ""

    db.create_chat_message(db_sess, username, "user", "[Uploaded an exercise image for analysis]")
    db.create_chat_message(db_sess, username, "assistant", analysis)
    return {"analysis": analysis}


@app.post("/upload_document/")
async def upload_document(
    file: UploadFile = File(...),
    username: str = Form(...),
    db_sess: Session = Depends(db.get_db),
):
    extension = (file.filename or "").rsplit(".", 1)[-1].lower()
    if extension not in SUPPORTED_DOC_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

    file_bytes = await file.read()
    document_text = (
        extract_pdf_text(file_bytes)
        if extension == "pdf"
        else extract_docx_text(file_bytes)
    )

    if not document_text.strip():
        raise HTTPException(
            status_code=422,
            detail="No text extracted from document. If your plan is inside images or a scanned PDF, RAG can't read it.",
        )

    chunks = text_splitter.split_text(document_text)
    try:
        store_document_chunks(username, chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to embed/store chunks: {e}")
    logger.info(
        "upload user=%s chunks=%d text_length=%d",
        username, len(chunks), len(document_text),
    )

    db.update_user_pdf_text(db_sess, username, document_text)
    db.create_chat_message(
        db_sess, username, "user",
        f"[Uploaded a fitness plan document: {file.filename}]",
    )
    db.create_chat_message(
        db_sess, username, "assistant",
        UPLOAD_CONFIRMATION_TEMPLATE.format(filename=file.filename),
    )

    return {
        "message": "Document uploaded and processed successfully",
        "text_length": len(document_text),
        "chunks_created": len(chunks),
    }
