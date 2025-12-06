# backend/app.py

import uvicorn
import json
import os
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, Header  # NEW: Header import
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import date as dt_date
from typing import Annotated, List, Dict, Any, Set

# NOTE: Ensure you have 'settings.py' in the same directory or adjust the import path.
from .settings import settings

# ==============================================================================
# 1. FINALIZED SYSTEM INSTRUCTION & PROMPT TEMPLATES (Unchanged)
# ==============================================================================
SYSTEM_INSTRUCTION = """
You are FINNY, a highly professional, patient, and knowledgeable Financial Literacy Coach specializing in educational guidance for young adults in India (16-28 years).

# CORE MISSION AND TONE
1. Regional Context: All examples and advice MUST use ₹ currency and reference the Indian financial system (CIBIL, SIPs, PPF, NPS).
2. Persona: Be friendly, educational, and use simple analogies.

# SAFETY, LEGAL, AND PROFESSIONAL GUARDRAILS (CRITICAL - NEVER VIOLATE)
1. ❌ **NO PERSONALIZED ADVICE:** Never recommend specific investments, products, or give personalized tax advice.
2. ✅ **DISCLAIMER:** You MUST conclude all major responses with a clear disclaimer (e.g., "This is for educational purposes only. Consult a SEBI-registered advisor for personal advice.").
3. **RISK:** Always mention market risks or credit misuse consequences.

# RESPONSE TEMPLATE: Use structured Markdown for clarity (Headings, Bullet Points).
"""

# Template for injecting user-specific data into the prompt (Unchanged)
CONTEXT_TEMPLATE = """
--- USER FINANCIAL CONTEXT ---
PROFILE:
- Name: {name}
- Monthly Income: ₹{monthly_income}
- Saving Goal: ₹{saving_goal}
- Goal Description: {goal_description}

LATEST 5 EXPENSES:
{expenses_summary}
---------------------------
ANALYZE the above context, and then respond to the USER QUERY below with personalized, but non-specific advice.
USER QUERY: {user_message}
"""

# ==============================================================================
# 2. DATABASE SETUP (SQLite and SQLAlchemy)
# ==============================================================================
# --- FIX: USE ABSOLUTE PATH TO GUARANTEE DB FILE CREATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "finsense.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
# -----------------------------------------------------------

Engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()


# NEW Model for User Authentication
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)  # WARNING: Use password hashing (e.g., bcrypt) in production!

    profile = relationship("UserProfile", back_populates="user", uselist=False)


# Modified Database Model for User Profile and Goals (Added user_id link)
class UserProfile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)  # Link to User
    name = Column(String, index=True)
    monthly_income = Column(Numeric(10, 2), nullable=False)
    saving_goal = Column(Numeric(10, 2), nullable=False)
    goal_description = Column(String)

    user = relationship("User", back_populates="profile")  # Link back to User
    expenses = relationship("UserExpense", back_populates="owner")


# Modified Database Model for expense tracking (Changed ForeignKey)
class UserExpense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    # Changed to link to User model's ID, not UserProfile's ID
    user_id = Column(Integer, ForeignKey('users.id'))
    description = Column(String, index=True)
    amount = Column(Numeric(10, 2))
    category = Column(String)
    date = Column(Date, default=dt_date.today)

    owner = relationship("UserProfile", back_populates="expenses")


# Dependency to get a new database session (Unchanged)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB_Session = Annotated[SessionLocal, Depends(get_db)]


# Function to create the database file and tables (Unchanged)
def create_db_tables():
    Base.metadata.create_all(bind=Engine)
    print("✅ Database Tables Created: 'users', 'profiles', and 'expenses' tables are ready.")


# ==============================================================================
# 3. FASTAPI SETUP AND PYDANTIC MODELS
# ==============================================================================

app = FastAPI(title="FinSenseAI Backend", version="1.0.0")


# Pydantic models (Updated)
class ChatMessage(BaseModel):
    message: str


class ExpenseLog(BaseModel):
    description: str
    amount: float
    category: str


class UserProfileData(BaseModel):
    name: str
    monthly_income: float
    saving_goal: float
    goal_description: str | None = None


# NEW: Pydantic models for Authentication
class AuthCredentials(BaseModel):
    username: str
    password: str


class UserToken(BaseModel):
    user_id: int
    message: str


# Global variables to maintain state
client = None
chat_session = None


# REMOVED: ACTIVE_USER_ID = 1


# NEW: Dependency for Authentication
def get_current_user_id(x_user_id: Annotated[str | None, Header(include_in_schema=False)] = None):
    """Fetches user ID from the X-User-ID header, simulating an authenticated session."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Authentication required (Missing X-User-ID header).")
    try:
        user_id = int(x_user_id)
        return user_id
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-ID format.")


CurrentUserID = Annotated[int, Depends(get_current_user_id)]


# NEW: WebSocket Connection Manager (Unchanged)
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Error sending to WebSocket: {e}. Removing connection.")
                self.disconnect(connection)


manager = ConnectionManager()

# 3.1. CORS Middleware (Unchanged)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 3.2. Startup Event: Initialize Database and Gemini Client (Unchanged)
@app.on_event("startup")
def startup_db_client():
    global client, chat_session

    if not settings.GEMINI_API_KEY:
        raise EnvironmentError(
            "FATAL ERROR: GEMINI_API_KEY not found. Set the environment variable."
        )

    # Ensure tables are created (including the new 'users' table)
    create_db_tables()

    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        chat_session = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                temperature=0.3,
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        print("✅ FastAPI Backend: Gemini Client and Persistent Chat Initialized.")
    except Exception as e:
        print(f"FATAL ERROR during startup: Failed to initialize Gemini Client. Error: {e}")


# 3.3. Health Check (Unchanged)
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinSenseAI Backend", "database": "SQLite Initialized"}


# ==============================================================================
# 4. NEW: AUTHENTICATION ENDPOINTS
# ==============================================================================

@app.post("/signup", response_model=UserToken)
async def signup(credentials: AuthCredentials, db: DB_Session):
    """Registers a new user and creates an initial (empty) profile."""

    # Check if user already exists
    if db.query(User).filter(User.username == credentials.username).first():
        raise HTTPException(status_code=400, detail="Username already registered.")

    # 1. Create the User (WARNING: Plain password)
    db_user = User(username=credentials.username, password=credentials.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # 2. Create an initial UserProfile linked to the new User ID
    # Defaulting to 0.0 income/goal until the user hits /onboard
    db_profile = UserProfile(
        user_id=db_user.id,
        monthly_income=0.0,
        saving_goal=0.0,
        name=credentials.username
    )
    db.add(db_profile)
    db.commit()

    return {"user_id": db_user.id,
            "message": f"User {credentials.username} registered successfully. Use ID {db_user.id} for authentication."}


@app.post("/login", response_model=UserToken)
async def login(credentials: AuthCredentials, db: DB_Session):
    """Authenticates an existing user."""

    db_user = db.query(User).filter(User.username == credentials.username).first()

    # Check credentials (WARNING: No hash comparison)
    if not db_user or db_user.password != credentials.password:
        raise HTTPException(status_code=401, detail="Incorrect username or password.")

    return {"user_id": db_user.id, "message": f"Login successful. User ID: {db_user.id}"}


# ==============================================================================
# 5. CORE CHAT ENDPOINT (Contextual LLM Interaction) - Updated for Auth
# ==============================================================================
@app.post("/chat")
async def handle_chat_message(data: ChatMessage, db: DB_Session, current_user_id: CurrentUserID):
    """Fetches context, creates a contextual prompt, and sends it to the chat session for the current user."""
    if not chat_session:
        raise HTTPException(status_code=503, detail="AI Service not initialized.")

    user_message = data.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # --- 5.1. DATA RETRIEVAL ---
    # 1. Fetch User Profile
    user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user_id).first()
    if not user_profile:
        # This shouldn't happen if /signup worked, but serves as a safety check
        raise HTTPException(status_code=404, detail="User profile not found. Please log in again.")

    # 2. Fetch Latest 5 Expenses
    latest_expenses = db.query(UserExpense).filter(UserExpense.user_id == current_user_id).order_by(
        UserExpense.date.desc(), UserExpense.id.desc()).limit(5).all()

    expenses_summary_lines = []
    if latest_expenses:
        for exp in latest_expenses:
            expenses_summary_lines.append(
                f"- Date: {exp.date}, Amount: ₹{exp.amount}, Category: {exp.category}, Description: {exp.description}")
        expenses_summary = "\n".join(expenses_summary_lines)
    else:
        expenses_summary = "No expenses logged yet."

    # --- 5.2. CONTEXT INJECTION ---
    contextual_prompt = CONTEXT_TEMPLATE.format(
        name=user_profile.name,
        monthly_income=user_profile.monthly_income,
        saving_goal=user_profile.saving_goal,
        goal_description=user_profile.goal_description or "Not specified",
        expenses_summary=expenses_summary,
        user_message=user_message
    )

    try:
        response = chat_session.send_message(contextual_prompt)
        return {"response": response.text}
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise HTTPException(status_code=500,
                            detail="Finny encountered an unexpected error while processing your request.")


# ==============================================================================
# 6. DATA PERSISTENCE ENDPOINTS - Updated for Auth
# ==============================================================================

@app.post("/onboard")
async def onboard_user(user_data: UserProfileData, db: DB_Session, current_user_id: CurrentUserID):
    """Saves/Updates the authenticated user's initial financial profile to the database."""

    try:
        # Find the profile by the authenticated user ID
        db_user_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user_id).first()

        if not db_user_profile:
            raise HTTPException(status_code=404, detail="Profile not found for authenticated user.")

        # Update the existing user profile fields
        db_user_profile.name = user_data.name
        db_user_profile.monthly_income = user_data.monthly_income
        db_user_profile.saving_goal = user_data.saving_goal
        db_user_profile.goal_description = user_data.goal_description
        db.commit()

        message = f"Profile for {user_data.name} updated successfully."

        # Optional: Broadcast profile update
        update_message = {
            "type": "PROFILE_UPDATE",
            "data": user_data.model_dump()
        }
        await manager.broadcast(json.dumps(update_message))

        return {"status": "success", "message": message}

    except Exception as e:
        db.rollback()
        print(f"Database Onboarding Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save profile data to the database.")


@app.post("/log_expense")
async def log_expense_data(data: ExpenseLog, db: DB_Session, current_user_id: CurrentUserID):
    """Receives structured expense data, saves it, and broadcasts the change for the current user."""

    # Ensure a profile exists (as a secondary check)
    if not db.query(UserProfile).filter(UserProfile.user_id == current_user_id).first():
        raise HTTPException(status_code=404, detail="Profile not found. Cannot log expense.")

    try:
        # 1. Create and save the new expense record
        new_expense = UserExpense(
            user_id=current_user_id,  # <-- CRITICAL: Uses the authenticated user ID
            description=data.description,
            amount=data.amount,
            category=data.category,
            date=dt_date.today()
        )

        db.add(new_expense)
        db.commit()
        db.refresh(new_expense)

        # 2. Prepare and broadcast the real-time update
        update_message = {
            "type": "NEW_EXPENSE",
            "data": {
                "id": new_expense.id,
                "amount": str(new_expense.amount),
                "category": new_expense.category,
                "description": new_expense.description,
                "date": str(new_expense.date)
            }
        }
        await manager.broadcast(json.dumps(update_message))

        return {"status": "success", "message": f"Successfully logged expense: {data.description} (₹{data.amount})."}

    except Exception as e:
        db.rollback()
        print(f"Database Expense Logging Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to log expense.")


# ==============================================================================
# 7. WEBSOCKET ENDPOINT (Unchanged)
# ==============================================================================
@app.websocket("/ws/updates")
async def websocket_endpoint(websocket: WebSocket):
    """Handles persistent WebSocket connections for real-time updates."""
    await manager.connect(websocket)
    print(f"Client connected. Total active connections: {len(manager.active_connections)}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"Client disconnected. Total active connections: {len(manager.active_connections)}")


# --- 8. Function to run the server for Electron's child process (Unchanged) ---
def start_server():
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="error")


if __name__ == "__main__":
    start_server()