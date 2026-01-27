# db_sqlalchemy.py
from sqlalchemy import Column, String, DateTime, create_engine, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import create_engine

#connrct to db or create if not exists
engine = create_engine('sqlite:///my_database.db', echo=True)
Base = declarative_base()

# User model
class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, ForeignKey("users.username"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreferences(Base):
    __tablename__ = "user_preferences"
    username = Column(String, ForeignKey("users.username"), primary_key=True)
    preferences_json = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)


# Create tables
Base.metadata.create_all(bind=engine)

#Session factory to interact with db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# CRUD helpers
def get_user(db_session, username: str):
    return db_session.query(User).filter_by(username=username).first()


def create_user(db_session, username: str, session_id: str):
    user = User(username=username, session_id=session_id)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def update_session(db_session, username: str, session_id: str):
    user = get_user(db_session, username)
    if user:
        user.session_id = session_id
        db_session.commit()
        db_session.refresh(user)
    return username
    

def create_chat_message(db_session, username: str, role: str, content: str):
     chat_message = ChatMessage(username=username, role=role, content=content)
     db_session.add(chat_message)
     db_session.commit()
     db_session.refresh(chat_message)

def create_plan(db_session, username: str, session_id: str, content: str):
     plan = Plan(username=username, session_id=session_id, content=content)
     db_session.add(plan)
     db_session.commit()
     db_session.refresh(plan)
     return plan

def create_user_preferences(db_session, username: str, preferences_json: str):
     user_preferences = UserPreferences(username=username, preferences_json=preferences_json)
     db_session.add(user_preferences)
     db_session.commit()
     db_session.refresh(user_preferences)
     return user_preferences

def get_user_preferences(db_session, username: str):
     return db_session.query(UserPreferences).filter_by(username=username).first()

def update_user_preferences(db_session, username: str, preferences_json: str):
     user_preferences = get_user_preferences(db_session, username)
     if user_preferences:
          user_preferences.preferences_json = preferences_json
          db_session.commit()
          db_session.refresh(user_preferences)
          return user_preferences
     return None

def get_chat_messages(db_session, username: str):
     return db_session.query(ChatMessage).filter_by(username=username).order_by(ChatMessage.created_at.asc()).all()

def get_plans(db_session, username: str):
     return db_session.query(Plan).filter_by(username=username).all()

