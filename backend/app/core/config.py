import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./enterprise_ai.db")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

settings = Settings()
