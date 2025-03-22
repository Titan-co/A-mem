import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file if it exists
load_dotenv()

class Settings(BaseSettings):
    """Server settings"""
    APP_NAME: str = "A-MEM MCP Server"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Memory Control Protocol server for Agentic Memory System"
    
    # Server settings
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", 8000))
    DEBUG: bool = os.environ.get("DEBUG", "False").lower() in ("true", "1", "t")
    
    # A-MEM settings
    MODEL_NAME: str = os.environ.get("MODEL_NAME", "all-MiniLM-L6-v2")
    LLM_BACKEND: str = os.environ.get("LLM_BACKEND", "openai")
    LLM_MODEL: str = os.environ.get("LLM_MODEL", "gpt-4")
    EVO_THRESHOLD: int = int(os.environ.get("EVO_THRESHOLD", 3))
    API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    API_URL: str = os.environ.get("OPENAI_API_URL", "")  # OpenAI-compatible API URL
    
    # Default memory retrieval parameters
    DEFAULT_K: int = int(os.environ.get("DEFAULT_K", 5))
    
    # CORS settings - handled manually in server.py
    # We don't define these as fields to avoid pydantic parsing issues

# Create settings instance
settings = Settings()
