# # backend/app.py
# import uvicorn
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from google import genai
# from google.genai import types
#
# # Import secure settings
# from .settings import settings
#
# # ==============================================================================
# # 1. FINALIZED SYSTEM INSTRUCTION (Embedding all compliance rules)
# # ==============================================================================
# SYSTEM_INSTRUCTION = """
# You are FINNY, a highly professional, patient, and knowledgeable Financial Literacy Coach specializing in educational guidance for young adults in India (16-28 years).
#
# # CORE MISSION AND TONE
# 1. Regional Context: All examples and advice MUST use ₹ currency and reference the Indian financial system (CIBIL, SIPs, PPF, NPS).
# 2. Persona: Be friendly, educational, and use simple analogies.
#
# # SAFETY, LEGAL, AND PROFESSIONAL GUARDRAILS (CRITICAL - NEVER VIOLATE)
# 1. ❌ **NO PERSONALIZED ADVICE:** Never recommend specific investments, products, or give personalized tax advice.
# 2. ✅ **DISCLAIMER:** You MUST conclude all major responses with a clear disclaimer (e.g., "This is for educational purposes only. Consult a SEBI-registered advisor for personal advice.").
# 3. **RISK:** Always mention market risks or credit misuse consequences.
#
# # RESPONSE TEMPLATE: Use structured Markdown for clarity (Headings, Bullet Points).
# """
#
# # ==============================================================================
# # 2. FASTAPI SETUP AND CHAT INITIALIZATION
# # ==============================================================================
#
# app = FastAPI(title="FinSenseAI Backend", version="1.0.0")
#
#
# # Pydantic model for incoming JSON data from the Electron frontend
# class ChatMessage(BaseModel):
#     message: str
#
#
# # 2.1. CORS Middleware (Essential for Electron)
# # Allows the Electron frontend (running on a different origin) to talk to the API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
# # Global variables to maintain state (client connection and chat history)
# # After (Corrected)
# client = None
# chat_session = None
#
#
# # 2.2. Startup Event: Initialize Gemini Client
# @app.on_event("startup")
# def startup_db_client():
#     global client, chat_session
#     try:
#         # Client loads the key from settings.GEMINI_API_KEY environment variable
#         client = genai.Client(api_key=settings.GEMINI_API_KEY)
#
#         # The persistent chat session maintains the conversation history
#         chat_session = client.chats.create(
#             model="gemini-2.5-flash",
#             config=types.GenerateContentConfig(
#                 temperature=0.3,
#                 system_instruction=SYSTEM_INSTRUCTION,
#             ),
#         )
#         print("✅ FastAPI Backend: Gemini Client and Persistent Chat Initialized.")
#     except Exception as e:
#         print(f"FATAL ERROR during startup: Failed to initialize Gemini Client. Check API Key. Error: {e}")
#         # The app will still run, but API calls will fail
#
#
# # 2.3. Health Check
# @app.get("/health")
# def health_check():
#     return {"status": "ok", "service": "FinSenseAI Backend"}
#
#
# # ==============================================================================
# # 3. CORE CHAT ENDPOINT
# # ==============================================================================
# @app.post("/chat")
# async def handle_chat_message(data: ChatMessage):
#     """Receives user input from Electron and sends it to the persistent chat session."""
#     if not chat_session:
#         raise HTTPException(status_code=503, detail="AI Service not initialized.")
#
#     user_message = data.message.strip()
#     if not user_message:
#         raise HTTPException(status_code=400, detail="Message cannot be empty.")
#
#     try:
#         # Call the persistent chat session
#         response = chat_session.send_message(user_message)
#         # Return the response text back to the Electron frontend
#         return {"response": response.text}
#     except Exception as e:
#         print(f"Gemini API Error: {e}")
#         # Return a clean error message to the user
#         raise HTTPException(status_code=500, detail="Finny encountered an unexpected error.")
#
#
# # --- 4. Function to run the server for Electron's child process ---
# def start_server():
#     # Use 127.0.0.1 to ensure it's only accessible locally
#     uvicorn.run(app, host="127.0.0.1", port=5000, log_level="error")
#
#
# if __name__ == "__main__":
#     start_server()


import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types

# Import secure settings
from .settings import settings

# ======================================================================
# 1. SYSTEM INSTRUCTION
# ======================================================================
SYSTEM_INSTRUCTION = """
You are FINNY, a highly professional, patient, and knowledgeable Financial Literacy Coach specializing in educational guidance for young adults in India (16-28 years).

# CORE MISSION AND TONE
1. Always use ₹ currency and Indian financial terms (CIBIL, SIPs, PPF, NPS).
2. Stay friendly, simple, and educational.

# SAFETY RULES
❌ Do NOT give personalized investing or tax advice.
❌ Do NOT recommend specific stocks, funds, brokers, or credit products.
✔ ALWAYS include a disclaimer: “This is for educational purposes only.”

# RESPONSE FORMAT
Use clean Markdown (Headings, Bullet Points, Tables).
"""

# ======================================================================
# 2. FASTAPI SETUP
# ======================================================================

app = FastAPI(title="FinSenseAI Backend", version="1.0.0")


class ChatMessage(BaseModel):
    message: str


# CORS for Electron
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Gemini Client
client = None
chat_session = None


# ======================================================================
# 3. STARTUP EVENT → Initialize Gemini
# ======================================================================
@app.on_event("startup")
def initialize_gemini():
    global client, chat_session
    try:
        # Initialize Gemini
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        # Create persistent chat session
        chat_session = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                temperature=0.3,
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )

        print("✅ Gemini AI Initialized Successfully")

    except Exception as e:
        print("\n❌ ERROR: Gemini Initialization Failed")
        print("Reason:", e)
        print("Check: GEMINI_API_KEY in settings.py or .env\n")


# ======================================================================
# 4. HEALTH CHECK ENDPOINT
# ======================================================================
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FinSenseAI Backend", "gemini": "ready"}


# ======================================================================
# 5. CHAT ENDPOINT
# ======================================================================
@app.post("/chat")
async def chat_api(data: ChatMessage):
    global chat_session

    if not chat_session:
        raise HTTPException(
            status_code=503,
            detail="AI not initialized. Check GEMINI_API_KEY."
        )

    user_message = data.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        # Send user message to Gemini persistent chat
        response = chat_session.send_message(user_message)

        return {"response": response.text}

    except Exception as e:
        print("Gemini Error:", e)
        raise HTTPException(status_code=500, detail="Finny encountered an error.")


# ======================================================================
# 6. SERVER RUNNER (For Electron)
# ======================================================================
def start_server():
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")


if __name__ == "__main__":
    start_server()
