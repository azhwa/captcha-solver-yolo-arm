from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Captcha Solver API"
    
    # Security
    API_KEYS: List[str] = ["test-key-1", "test-key-2"]
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # YOLOv8 Model - Auto-detect production vs development
    MODEL_PATH: str = "/app/best.pt" if os.path.exists("/app/best.pt") else "../best.pt"
    
    # Temporary files
    TEMP_RESULTS_DIR: str = "/app/temp_results" if os.path.exists("/app") else "./temp_results"
    
    # Rate Limiting
    RATE_LIMIT: int = 100
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()