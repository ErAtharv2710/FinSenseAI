import uvicorn
import os  # Used to read MySQL credentials
from fastapi import FastAPI, HTTPException, status, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from datetime import date as dt_date
from typing import Annotated, Optional

# --- SQLAlchemy and Database Imports ---
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, ForeignKey, select
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Import secure settings
from .settings import settings

# ==============================================================================
# 1. SYSTEM INSTRUCTION
# ==============================================================================
SYSTEM_INSTRUCTION = """
You are FINNY, a highly professional, patient, and knowledgeable Financial Literacy Coach specializing in educational guidance for young adults in India (16-28 years).

# CORE MISSION AND TONE
1. Always use ₹ currency and Indian financial terms (CIBIL, SIPs, PPF, NPS).
2. Stay friendly, simple, and educational.

# SAFETY RULES
❌ Do NOT give personalized investing or tax advice.
❌ Do NOT recommend specific stocks, funds, brokers, or credit products.
✔ ALWAYS include a disclaimer: “This is for educational purposes only. Consult a SEBI-registered advisor for personal advice.”

# RESPONSE FORMAT
Use clean Markdown (Headings, Bullet Points, Tables).
"""

# ==============================================================================
# 2. DATABASE SETUP (SQLAlchemy - MYSQL)
# ==============================================================================

# Load sensitive credentials from environment variables (RECOMMENDED)
MYSQL_USER = os.environ.get("MYSQL_USER", "finny_user")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "secret_password")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "127.0.0.1")
MYSQL_DB = os.environ.get("MYSQL_DB", "finsense_db")

# MySQL Connection String using PyMySQL driver
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
)

# Create the SQLAlchemy engine
Engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_recycle=3600
)

# A factory for creating new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

# Base class for the declarative models
Base = declarative_base()


# Dependency function to get a database session for a single request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB_Session = Annotated[Session, Depends(get_db)]


# Placeholder for password hashing (⚠️ CRITICAL: REPLACE WITH REAL HASHING!)
def hash_password(password: str) -> str:
    return "NOT_SECURE_" + password


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password


# ==============================================================================
# 3. DATABASE MODELS
# ==============================================================================

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    expenses = relationship("UserExpense", back_populates="user_owner", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)

    name = Column(String(100), index=True)
    monthly_income = Column(Numeric(10, 2), nullable=False)
    saving_goal = Column(Numeric(10, 2), nullable=False)
    goal_description = Column(String(255))

    user = relationship("User", back_populates="profile")


class UserExpense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    description = Column(String(255), index=True)
    amount = Column(Numeric(10, 2))
    category = Column(String(50))
    date = Column(Date, default=dt_date.today)

    user_owner = relationship("User", back_populates="expenses")


# ==============================================================================
# 4. PYDANTIC SCHEMAS
# ==============================================================================

class ChatMessage(BaseModel):
    message: str


class AuthDetails(BaseModel):
    username: str
    password: str


class OnboardingData(BaseModel):
    name: str
    monthly_income: float
    saving_goal: float
    goal_description: str


class LogExpenseData(BaseModel):
    description: str
    amount: float
    category: str


# ==============================================================================
# 5. FASTAPI SETUP & INITIALIZATION
# ==============================================================================

app = FastAPI(title="FinSenseAI Backend", version="1.0.0")

# CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for AI chat
client = None
chat_session = None


# 5.1. STARTUP EVENT -> Initialize DB and Gemini
@app.on_event("startup")
def initialize_services():
    global client, chat_session

    # --- DATABASE INITIALIZATION with Debugging ---
    print(f"--- ATTEMPTING TO CONNECT TO MYSQL DB: {MYSQL_DB} on {MYSQL_HOST} ---")
    try:
        # This will attempt to connect and create tables in MySQL
        Base.metadata.create_all(bind=Engine)
        print("✅ MySQL Tables Created/Verified: 'users', 'profiles', and 'expenses' tables are ready.")
    except SQLAlchemyError as db_e:
        # CRITICAL DEBUGGING
        print("\n❌ FATAL DB ERROR: Failed to create database tables or connect to MySQL.")
        print("Check: MySQL Server running, credentials, and database exists.")
        print(f"Reason: {db_e}")
        raise db_e
    except Exception as e:
        print(f"An unexpected error occurred during DB setup: {e}")
        raise e

    # --- GEMINI AI INITIALIZATION ---
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        chat_session = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                temperature=0.3,
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        print("✅ Gemini AI Initialized Successfully")
    except Exception as e:
        print(f"\n❌ ERROR: Gemini Initialization Failed. Reason: {e}")
        pass


# ==============================================================================
# 6. DEPENDENCY FOR USER AUTHENTICATION
# ==============================================================================

def get_current_user_id(user_id_header: Annotated[Optional[str], Header(alias="X-User-ID")] = None) -> int:
    if not user_id_header or not user_id_header.isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated. 'X-User-ID' header required.",
        )
    return int(user_id_header)


CurrentUserID = Annotated[int, Depends(get_current_user_id)]


# ==============================================================================
# 7. AUTHENTICATION ENDPOINTS
# ==============================================================================

@app.post("/signup")
def signup(data: AuthDetails, db: DB_Session):
    if db.scalar(select(User).where(User.username == data.username)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already registered.")

    hashed_password = hash_password(data.password)
    db_user = User(username=data.username, password=hashed_password)

    try:
        db.add(db_user)
        # Create an initial (empty) profile entry
        db_profile = UserProfile(
            user_id=db_user.id,
            name=data.username,
            monthly_income=0.0,
            saving_goal=0.0
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        print(f"Signup DB Error: {e}")
        raise HTTPException(status_code=500, detail="Database error during signup.")

    return {"user_id": db_user.id, "message": "User created. Proceed to onboarding."}


@app.post("/login")
def login(data: AuthDetails, db: DB_Session):
    db_user = db.scalar(select(User).where(User.username == data.username))

    if not db_user or not verify_password(data.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password.")

    return {"user_id": db_user.id, "message": "Login successful."}


# ==============================================================================
# 8. DATA ENDPOINTS (Require Authentication)
# ==============================================================================

@app.post("/onboard")
def onboard_user(data: OnboardingData, user_id: CurrentUserID, db: DB_Session):
    db_profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))

    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found. Must sign up first.")

    db_profile.name = data.name
    db_profile.monthly_income = data.monthly_income
    db_profile.saving_goal = data.saving_goal
    db_profile.goal_description = data.goal_description

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Onboarding Update DB Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile data.")

    return {"status": "success", "message": "Profile updated successfully."}


@app.post("/log_expense")
def log_expense(data: LogExpenseData, user_id: CurrentUserID, db: DB_Session):
    db_expense = UserExpense(
        user_id=user_id,
        description=data.description,
        amount=data.amount,
        category=data.category,
        date=dt_date.today()
    )

    try:
        db.add(db_expense)
        db.commit()
        db.refresh(db_expense)
    except Exception as e:
        db.rollback()
        print(f"Expense DB Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to log expense.")

    return {"status": "success", "expense_id": db_expense.id, "message": "Expense logged."}


# ==============================================================================
# 9. CORE CHAT ENDPOINT
# ==============================================================================

@app.post("/chat")
async def chat_api(data: ChatMessage, user_id: CurrentUserID):
    global chat_session

    if not chat_session:
        raise HTTPException(
            status_code=503,
            detail="AI not initialized. Check GEMINI_API_KEY."
        )

    user_message = data.message.strip()
    try:
        response = chat_session.send_message(user_message)
        return {"response": response.text}
    except Exception as e:
        print("Gemini Error:", e)
        raise HTTPException(status_code=500, detail="Finny encountered an error.")


# 10. HEALTH CHECK ENDPOINT
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinSenseAI Backend", "gemini": "ready", "db": "ready"}


# ==============================================================================
# 11. SERVER RUNNER
# ==============================================================================
def start_server():
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")


if __name__ == "__main__":
    start_server()