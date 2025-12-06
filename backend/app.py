import uvicorn
import os
from fastapi import FastAPI, HTTPException, status, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from datetime import date as dt_date
from typing import Annotated, Optional

# SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date, ForeignKey, select
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from sqlalchemy.exc import SQLAlchemyError

# Import settings
from settings import settings

# ================================================================
# 1. SYSTEM INSTRUCTION
# ================================================================
SYSTEM_INSTRUCTION = """
You are FINNY, a friendly financial literacy coach for Indian youth.

Rules:
- Always use ₹.
- Never give personalized advice or promote investment products.
- End every answer with: 
  “This is for educational purposes only. Consult a SEBI-registered advisor for personal advice.”
"""


# ================================================================
# 2. DATABASE CONFIG
# ================================================================
MYSQL_USER = settings.MYSQL_USER
MYSQL_PASSWORD = settings.MYSQL_PASSWORD
MYSQL_HOST = settings.MYSQL_HOST
MYSQL_DB = settings.MYSQL_DB

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"

engine = create_engine(DATABASE_URL, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


DB_Session = Annotated[Session, Depends(get_db)]


# Password hashing (dummy for now)
def hash_password(password: str) -> str:
    return "HASH_" + password


def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


# ================================================================
# 3. MODELS
# ================================================================
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(255))

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    expenses = relationship("UserExpense", back_populates="user")


class UserProfile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    name = Column(String(100))
    monthly_income = Column(Numeric(10, 2), default=0.0)
    saving_goal = Column(Numeric(10, 2), default=0.0)
    goal_description = Column(String(255), default="")

    user = relationship("User", back_populates="profile")


class UserExpense(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String(255))
    amount = Column(Numeric(10, 2))
    category = Column(String(50))
    date = Column(Date, default=dt_date.today)

    user = relationship("User", back_populates="expenses")


# ================================================================
# 4. SCHEMAS
# ================================================================
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


class ChatMessage(BaseModel):
    message: str


# ================================================================
# 5. FASTAPI INIT
# ================================================================
app = FastAPI(title="FinSenseAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = None
chat_session = None


# ================================================================
# 6. STARTUP EVENT
# ================================================================
@app.on_event("startup")
def startup_event():
    global client, chat_session

    print("🔄 Creating MySQL tables...")
    Base.metadata.create_all(engine)
    print("✅ MySQL Ready")

    # Initialize Gemini
    try:
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        chat_session = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                temperature=0.3,
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        print("✅ Gemini Ready")
    except Exception as e:
        print("❌ Gemini Error:", e)


# ================================================================
# 7. AUTH
# ================================================================
@app.post("/signup")
def signup(data: AuthDetails, db: DB_Session):
    if db.scalar(select(User).where(User.username == data.username)):
        raise HTTPException(409, "Username already exists")

    user = User(username=data.username, password=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create empty profile
    profile = UserProfile(user_id=user.id, name=data.username)
    db.add(profile)
    db.commit()

    return {"user_id": user.id, "message": "Signup successful"}


@app.post("/login")
def login(data: AuthDetails, db: DB_Session):
    user = db.scalar(select(User).where(User.username == data.username))
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid login")

    return {"user_id": user.id, "message": "Login ok"}


# AUTH HEADER
def get_user(user_header: Annotated[str | None, Header(alias="X-User-ID")] = None):
    if not user_header or not user_header.isdigit():
        raise HTTPException(401, "Missing X-User-ID header")
    return int(user_header)


CurrentUser = Annotated[int, Depends(get_user)]


# ================================================================
# 8. PROFILE & EXPENSE API
# ================================================================
@app.post("/onboard")
def onboard(data: OnboardingData, user_id: CurrentUser, db: DB_Session):
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user_id))
    profile.name = data.name
    profile.monthly_income = data.monthly_income
    profile.saving_goal = data.saving_goal
    profile.goal_description = data.goal_description

    db.commit()
    return {"message": "Profile updated"}


@app.post("/log_expense")
def log_expense(data: LogExpenseData, user_id: CurrentUser, db: DB_Session):
    txn = UserExpense(
        user_id=user_id,
        description=data.description,
        amount=data.amount,
        category=data.category,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    return {"expense_id": txn.id, "message": "Expense added"}


# ================================================================
# 9. AI CHAT
# ================================================================
@app.post("/chat")
def chat(data: ChatMessage, user_id: CurrentUser):
    global chat_session

    reply = chat_session.send_message(data.message)
    return {"response": reply.text}


@app.get("/health")
def health():
    return {"status": "ok"}


# ================================================================
# 10. RUN
# ================================================================
def start_server():
    uvicorn.run(app, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    start_server()
