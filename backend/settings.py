# backend/settings.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional


# ==============================================================================
# 1. APPLICATION SETTINGS MODEL
# ==============================================================================

class AppSettings(BaseSettings):
    """
    Defines application settings, primarily loading from environment variables
    or using hardcoded defaults for development.
    """

    # --- API KEYS & IDENTIFIERS ---
    # Note: Using hardcoded value for quick testing, but setting it in
    # environment variables or .env file is highly recommended.
    GEMINI_API_KEY: str = "AIzaSyByTlk7pzNVg0MwJeaXXmx2-oSdOI8Mu6c"

    # --- DATABASE CONFIGURATION (MySQL) ---
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "The_Phantom_ThIef."
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_DB: str = "finsense_db"

    # --- CORS (Cross-Origin Resource Sharing) ---
    # Lists the origins allowed to access the FastAPI backend.
    # Includes "null" for compatibility with Electron/desktop environments.
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:5000",
        "http://localhost:5000",
        "null",
    ]

    # --- PYDANTIC V2 CONFIGURATION ---
    # Tells Pydantic to load variables from a .env file if it exists.
    # This replaces the old 'class Config:' structure.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra='ignore'  # Ignores extra variables in the environment
    )


# Initialize the settings object
settings = AppSettings()

# ==============================================================================
# 2. POST-INIT CHECKS
# ==============================================================================

if not settings.GEMINI_API_KEY:
    print("⚠️ WARNING: GEMINI_API_KEY is not set.")
    print("Please set this value in your environment variables or the AppSettings model.")