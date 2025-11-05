from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Captcha Solver API"
    
    # Admin Credentials (configurable via .env)
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"
    ADMIN_EMAIL: str = "admin@example.com"
    
    # Security
    API_KEYS: List[str] = ["test-key-1", "test-key-2"]
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # YOLOv8 Model - Auto-detect production vs development
    # Default path, will be checked at runtime (doesn't need to exist at startup)
    MODEL_PATH: str = "/app/best.pt" if os.path.exists("/app") else "../best.pt"
    
    # Temporary files
    TEMP_RESULTS_DIR: str = "/app/temp_results" if os.path.exists("/app") else "./temp_results"
    
    # Rate Limiting
    RATE_LIMIT: int = 100
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = "ignore"

settings = Settings()