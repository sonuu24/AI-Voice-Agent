from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # LLM
    groq_api_key: str
    openai_api_key: Optional[str] = None
    
    # Telephony
    twilio_account_sid: str  # Remove Optional
    twilio_auth_token: str   # Remove Optional
    twilio_phone_number: str # Remove Optional
    
    # LiveKit (for future use)
    livekit_url: str = "ws://localhost:7880"
    livekit_api_key: Optional[str] = None
    livekit_api_secret: Optional[str] = None
    
    # Vector DB - Qdrant Cloud
    qdrant_url: str
    qdrant_api_key: Optional[str] = None
    
    # App
    environment: str = "development"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()