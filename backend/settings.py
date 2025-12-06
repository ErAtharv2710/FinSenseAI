# backend/settings.py
import os

# --- 1. GEMINI API KEY ---
# It's safest to load this from an environment variable (set in your terminal)
# If you must hardcode it for a quick test, replace os.environ.get(...) with your actual key:
# Example: GEMINI_API_KEY = "AIzaSy..."

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY environment variable not found.")
    print("Please set it in your terminal before running the server.")

# --- 2. CORS (Cross-Origin Resource Sharing) ---
# Since Electron runs on a custom protocol (usually file:// or localhost)
# we need to explicitly allow the origins where the frontend will run.
CORS_ORIGINS = [
    # The default port for your FastAPI server (even though uvicorn is running it)
    "http://127.0.0.1:5000",
    "http://localhost:5000",

    # Critical: Allow the Electron/file protocol for development
    "null",

    # If your Electron app runs on a specific port/address (e.g., from a dev server):
    # "http://localhost:8080",
]

# NOTE: In a production web environment, CORS_ORIGINS should only list the
# domain where your frontend is hosted. For Electron, "null" is often required.