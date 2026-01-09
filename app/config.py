from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # App
    APP_NAME: str = "News App API"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str
    
    # News API
    NEWS_API_KEY: str
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"
    
    # Gemini AI
    GEMINI_API_KEY: str
    
    # Gemini AI Chat (separate key for chat feature, optional - defaults to GEMINI_API_KEY)
    GEMINI_CHAT_API_KEY: Optional[str] = None
    
    @property
    def chat_api_key(self) -> str:
        """Return chat API key, fallback to main API key if not set"""
        return self.GEMINI_CHAT_API_KEY or self.GEMINI_API_KEY
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

settings = Settings()
