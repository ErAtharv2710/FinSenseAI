import sys
import os
# CRITICAL FIX for ModuleNotFoundError when running via Electron/npm start:
# Adds the project root directory to the Python path so the 'backend' package is found.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# --------------------------------------------------------------------------

import uvicorn
from fastapi import FastAPI, HTTPException, status, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from typing import Annotated, Optional

# Import secure settings
from backend.settings import settings

# ==============================================================================
# 1. SYSTEM INSTRUCTION (UPDATED for Tone and Professional Formatting)
# ==============================================================================
SYSTEM_INSTRUCTION = """
You are Finsense, a highly professional, patient, and knowledgeable Financial Literacy Coach specializing in educational guidance for young adults in India (16-28 years).

# CORE MISSION AND TONE
1. **Always begin the conversation with: "Hello! I am Finsense, your financial advisor."**
2. Always use ₹ currency and Indian financial terms (CIBIL, SIPs, PPF, NPS).
3. Stay friendly, simple, and educational.
4. **CRITICAL: Format responses using strong Markdown structure, including headings (##), bold text, bullet points, and numbered lists. Divide the output into small, meaningful paragraphs to avoid continuous, monolithic blocks of text.**

# SAFETY RULES
❌ Do NOT give personalized investing or tax advice.
❌ Do NOT recommend specific stocks, funds, brokers, or credit products.
✔ ALWAYS include a disclaimer: “This is for educational purposes only. Consult a SEBI-registered advisor for personal advice.”

# RESPONSE FORMAT
Use clean Markdown (Headings, Bullet Points, Tables).
"""

# ==============================================================================
# 2. DATABASE SETUP (TEMPORARILY BYPASSED)
# ==============================================================================

# Since we are bypassing the database, we can simplify or remove DB-related imports
# and setup, allowing the server to start without needing MySQL or PyMySQL dependencies.

# Define placeholder dependencies to allow FastAPI endpoints to still compile
# but remove actual database session dependency.
# This prevents crashes from importing SQLAlchemy components related to the DB session.

# Create a placeholder function that always returns None instead of a DB session
def get_db():
    yield None

# Define the type annotation for the placeholder
DB_Session = Annotated[None, Depends(get_db)]


# ==============================================================================
# 3. DATABASE MODELS (TEMPORARILY BYPASSED)
# ==============================================================================

# These classes are only needed for the /signup and /onboard endpoints,
# which are currently disabled in the simplified version below.

# ==============================================================================
# 4. PYDANTIC SCHEMAS (Simplified for Chat)
# ==============================================================================

class ChatMessage(BaseModel):
    message: str


class AuthDetails(BaseModel):
    username: str
    password: str


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


# 5.1. STARTUP EVENT -> Initialize ONLY Gemini
@app.on_event("startup")
def initialize_services():
    global client, chat_session

    # --- DATABASE BYPASSED ---
    print("--- DATABASE INITIALIZATION BYPASSED FOR SUBMISSION ---")

    # --- GEMINI AI INITIALIZATION ---
    try:
        # **CRITICAL:** Ensure your GEMINI_API_KEY in settings.py is valid!
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        chat_session = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                temperature=0.3,
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        print("Gemini AI Initialized Successfully")
    except Exception as e:
        print(f"\n*** FATAL AI ERROR: Gemini Initialization Failed. Reason: {e} ***")
        # If the AI fails to initialize, we MUST ensure the app doesn't start broken.
        # However, for a submission, we will let it continue running to show the server is up.
        pass


# ==============================================================================
# 6. DEPENDENCY FOR USER AUTHENTICATION (Simplified)
# ==============================================================================

# Since authentication is not needed for the chat demo, we can simplify this
def get_current_user_id(user_id_header: Annotated[Optional[str], Header(alias="X-User-ID")] = None) -> int:
    # Just return a placeholder ID if a header exists.
    if user_id_header and user_id_header.isdigit():
        return int(user_id_header)
    return 1 # Default placeholder user ID

CurrentUserID = Annotated[int, Depends(get_current_user_id)]


# ==============================================================================
# 7. AUTHENTICATION ENDPOINTS (TEMPORARILY DISABLED)
# ==============================================================================

@app.post("/signup")
def signup_disabled(data: AuthDetails, db: DB_Session):
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database disabled for demo.")

@app.post("/login")
def login_disabled(data: AuthDetails, db: DB_Session):
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database disabled for demo.")


# ==============================================================================
# 8. DATA ENDPOINTS (TEMPORARILY DISABLED)
# ==============================================================================

@app.post("/onboard")
def onboard_disabled(user_id: CurrentUserID, db: DB_Session):
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database disabled for demo.")

@app.post("/log_expense")
def log_expense_disabled(user_id: CurrentUserID, db: DB_Session):
    raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database disabled for demo.")


# ==============================================================================
# 9. CORE CHAT ENDPOINT
# ==============================================================================

@app.post("/chat")
async def chat_api(data: ChatMessage, user_id: CurrentUserID):
    global chat_session

    if not chat_session:
        # If AI failed to initialize, return a clear error message
        raise HTTPException(
            status_code=503,
            detail="AI service is not initialized. Check GEMINI_API_KEY in settings.py."
        )

    user_message = data.message.strip()
    try:
        response = chat_session.send_message(user_message)
        return {"response": response.text}
    except Exception as e:
        print("Gemini Error:", e)
        raise HTTPException(status_code=500, detail="Finny encountered an error while processing the message.")


# 10. HEALTH CHECK ENDPOINT
@app.get("/health")
def health_check():
    gemini_status = "ready" if chat_session else "failed"
    db_status = "disabled"
    return {"status": "ok", "service": "FinSenseAI Backend", "gemini": gemini_status, "db": db_status}


# ==============================================================================
# 11. SERVER RUNNER
# ==============================================================================
def start_server():
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")


if __name__ == "__main__":
    start_server()